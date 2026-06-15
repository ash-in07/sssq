#backend/routes/migration_routes.py
from flask import request
from flask_restful import Resource

from backend.models.migration_model import Migration
from backend.models.history_model import MigrationHistory
from backend.models.report_model import Report
from backend.extensions import db
from backend.utils.helpers import get_placeholder_data, sanitize_string
from backend.converters.sql_converter import migrate_sql_to_sql
from backend.converters.file_to_sql import import_file_to_sql
from backend.converters.sql_to_file import export_sql_to_file
from backend.processors.schema_generator import generate_create_table_schema

import json


class SqlToSqlResource(Resource):
    """Endpoint to migrate tables from one SQL database to another."""

    def post(self):
        payload = request.get_json(silent=True) or {}
        print("PAYLOAD RECEIVED:", payload)
        defaults = {
            "source_db_type": "mysql",
            "source_host": None,
            "source_port": None,
            "source_username": None,
            "source_password": None,
            "source_database": None,
            "target_db_type": "postgresql",
            "target_host": None,
            "target_port": None,
            "target_username": None,
            "target_password": None,
            "target_database": None,
            "tables": [],
        }
        if not payload:
            payload = get_placeholder_data(defaults)

        migration_record = Migration(
            migration_type="sql_to_sql",
            source_db=f"{payload.get('source_db_type')}://{payload.get('source_host')}",
            target_db=f"{payload.get('target_db_type')}://{payload.get('target_host')}",
            status="running",
        )
        db.session.add(migration_record)
        db.session.commit()

        try:
            report_data = migrate_sql_to_sql(payload)
            migration_record.status = "completed"
            report = Report(
                migration_id=migration_record.id,
                report_format="json",
                file_path="",
                summary=json.dumps(
                    report_data.get("summary", []),
                    default=str
                ),
            )
            db.session.add(report)
            db.session.commit()
            migration_record.report_id = report.id
            db.session.commit()
            history = MigrationHistory(
                migration_type="sql_to_sql",
                source_db=migration_record.source_db,
                target_db=migration_record.target_db,
                status="completed",
                errors=None,
                report_summary=report.summary,
            )
            db.session.add(history)
            db.session.commit()
            return {
                "message": "Migration completed.",
                "report": report_data
            }, 200
        except Exception as exc:
            migration_record.status = "failed"
            migration_record.error_message = str(exc)
            db.session.rollback()
            db.session.add(migration_record)
            db.session.commit()
            history = MigrationHistory(
                migration_type="sql_to_sql",
                source_db=migration_record.source_db,
                target_db=migration_record.target_db,
                status="failed",
                errors=str(exc),
                report_summary="Migration failed.",
            )
            db.session.add(history)
            db.session.commit()
            return {
                "message": "Migration failed.",
                "error": str(exc)
            }, 500


class MigrationStatusResource(Resource):
    """Endpoint to check the status of a migration by ID."""

    def get(self, migration_id: int):
        migration = Migration.query.get(migration_id)
        if migration is None:
            return {"message": "Migration not found."}, 404
        return {"migration": migration.to_dict()}, 200


class MigrationHistoryResource(Resource):
    """Endpoint to list migration history entries."""

    def get(self):
        history = [record.to_dict() for record in MigrationHistory.query.order_by(MigrationHistory.timestamp.desc()).all()]
        return {"history": history, "count": len(history)}, 200


class FileImportResource(Resource):
    """Endpoint to import a CSV or Excel file into a SQL database."""

    def post(self):
        payload = request.get_json(silent=True) or {}

        if not payload:
            return {"message": "Request body is required."}, 400

        file_path = payload.get("file_path")

        if not file_path:
            return {"message": "file_path is required."}, 400

        if "<FRONTEND" in str(file_path):
            return {"message": "Replace placeholder file path with a real file path."}, 400

        try:
            import_result = import_file_to_sql(payload)
            return {"message": "File import completed.", "result": import_result}, 200
        except FileNotFoundError:
            return {"message": f"File not found: {file_path}"}, 404
        except Exception as exc:
            return {"message": "File import failed.", "error": str(exc)}, 500


class SqlExportResource(Resource):
    """Endpoint to export SQL data to CSV or Excel."""

    def post(self):
        payload = request.get_json(silent=True) or {}

        if not payload:
            return {"message": "Request body is required."}, 400

        source_table = payload.get("source_table")

        if not source_table:
            return {"message": "source_table is required."}, 400

        try:
            export_result = export_sql_to_file(payload)
            return {"message": "Export completed.", "result": export_result}, 200
        except ValueError as exc:
            return {"message": str(exc)}, 400
        except Exception as exc:
            return {"message": "Export failed.", "error": str(exc)}, 500


class SchemaGeneratorResource(Resource):
    """Endpoint to generate CREATE TABLE schema from a file."""

    def post(self):
        payload = request.get_json(silent=True) or {}

        if not payload:
            return {"message": "Request body is required."}, 400

        file_path = payload.get("file_path")
        table_name = payload.get("table_name")

        if not file_path:
            return {"message": "file_path is required."}, 400

        if "<FRONTEND" in str(file_path):
            return {"message": "Replace placeholder file path with a real file path."}, 400

        try:
            schema_sql = generate_create_table_schema(file_path, table_name)
            return {"schema_sql": schema_sql}, 200
        except FileNotFoundError:
            return {"message": f"File not found: {file_path}"}, 404
        except Exception as exc:
            return {"message": "Schema generation failed.", "error": str(exc)}, 500