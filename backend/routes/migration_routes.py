from flask import request
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from werkzeug.utils import secure_filename

from backend.models.migration_model import Migration
from backend.models.history_model import MigrationHistory
from backend.models.report_model import Report
from backend.extensions import db
from backend.utils.helpers import get_placeholder_data
from backend.utils.file_handler import resolve_upload_path
from backend.converters.sql_converter import migrate_sql_to_sql
from backend.converters.file_to_sql import import_file_to_sql
from backend.converters.sql_to_file import export_sql_to_file
from backend.processors.schema_generator import generate_create_table_schema
from backend.database.connection_manager import create_engine_for_config, _DEFAULT_SQLITE_DB_FALLBACK

import json
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError


class SqlToSqlResource(Resource):
    """Endpoint to migrate tables from one SQL database to another."""

    def post(self):
        payload = request.get_json(silent=True) or {}
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
            db.session.flush()
            migration_record.status = "completed"
            migration_record.report_id = report.id
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
            db.session.rollback()
            mig = db.session.get(Migration, migration_record.id)
            if mig:
                mig.status = "failed"
                mig.error_message = str(exc)
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
        migration = db.session.get(Migration, migration_id)
        if migration is None:
            return {"message": "Migration not found."}, 404
        return {"migration": migration.to_dict()}, 200


class MigrationHistoryResource(Resource):
    """Endpoint to list migration history entries."""

    def get(self):
        records = db.session.execute(
            db.select(MigrationHistory).order_by(MigrationHistory.timestamp.desc())
        ).scalars().all()
        history = [record.to_dict() for record in records]
        return {"history": history, "count": len(history)}, 200


class FileImportResource(Resource):
    """Endpoint to import a CSV or Excel file into a SQL database."""

    def post(self):
        if request.is_json:
            payload = request.get_json(silent=True) or {}
            file_obj = None
        else:
            payload = request.form.to_dict()
            file_obj = request.files.get("file")

        if not payload and not file_obj:
            return {"message": "Request body is required."}, 400

        file_path = payload.get("file_path")

        if file_obj and file_obj.filename:
            filename = secure_filename(file_obj.filename)
            file_path = resolve_upload_path(filename)
            file_obj.save(file_path)
            payload["file_path"] = file_path

        if not file_path:
            return {"message": "A file upload is required."}, 400

        if "<FRONTEND" in str(file_path):
            return {"message": "Replace placeholder file path with a real file path."}, 400

        try:
            import_result = import_file_to_sql(payload)
            import os
            target_db_type = payload.get("target_db_type", "sqlite")
            target_host = payload.get("target_host", "localhost")
            history = MigrationHistory(
                migration_type="file_to_sql",
                source_db="file://" + os.path.basename(file_path),
                target_db=f"{target_db_type}://{target_host}",
                status="completed",
                errors=None,
                report_summary=f"Imported file into {import_result.get('table_name') or 'table'}.",
            )
            db.session.add(history)
            db.session.commit()
            return {"message": "File import completed.", "result": import_result}, 200
        except FileNotFoundError as exc:
            import os
            target_db_type = payload.get("target_db_type", "sqlite")
            target_host = payload.get("target_host", "localhost")
            history = MigrationHistory(
                migration_type="file_to_sql",
                source_db="file://" + os.path.basename(file_path) if file_path else "file://unknown",
                target_db=f"{target_db_type}://{target_host}",
                status="failed",
                errors=str(exc),
                report_summary="File not found.",
            )
            db.session.add(history)
            db.session.commit()
            return {"message": f"File not found: {file_path}"}, 404
        except (ValueError, SQLAlchemyError) as exc:
            import os
            raw = str(exc)
            short = raw.split("\n")[0].split("(Background")[0].strip()
            target_db_type = payload.get("target_db_type", "sqlite")
            target_host = payload.get("target_host", "localhost")
            history = MigrationHistory(
                migration_type="file_to_sql",
                source_db="file://" + os.path.basename(file_path) if file_path else "file://unknown",
                target_db=f"{target_db_type}://{target_host}",
                status="failed",
                errors=short or raw,
                report_summary="File import failed.",
            )
            db.session.add(history)
            db.session.commit()
            return {"message": "File import failed.", "error": short or raw}, 400
        except Exception as exc:
            import os
            target_db_type = payload.get("target_db_type", "sqlite")
            target_host = payload.get("target_host", "localhost")
            history = MigrationHistory(
                migration_type="file_to_sql",
                source_db="file://" + os.path.basename(file_path) if file_path else "file://unknown",
                target_db=f"{target_db_type}://{target_host}",
                status="failed",
                errors=str(exc),
                report_summary="File import failed.",
            )
            db.session.add(history)
            db.session.commit()
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
            source_db_type = payload.get("source_db_type", "sqlite")
            source_host = payload.get("source_host", "localhost")
            history = MigrationHistory(
                migration_type="sql_to_file",
                source_db=f"{source_db_type}://{source_host}",
                target_db="file://" + export_result.get("filename", "unknown"),
                status="completed",
                errors=None,
                report_summary=f"Exported table {export_result.get('table_name')} to file.",
            )
            db.session.add(history)
            
            # Record report metadata as well
            report = Report(
                migration_id=None,
                report_format=export_result.get("export_format", "csv"),
                file_path=export_result.get("export_path"),
                summary=f"Exported {export_result.get('rows_exported')} rows from {export_result.get('table_name')}.",
            )
            db.session.add(report)
            db.session.commit()
            
            return {"message": "Export completed.", "result": export_result}, 200
        except ValueError as exc:
            source_db_type = payload.get("source_db_type", "sqlite")
            source_host = payload.get("source_host", "localhost")
            history = MigrationHistory(
                migration_type="sql_to_file",
                source_db=f"{source_db_type}://{source_host}",
                target_db="file://unknown",
                status="failed",
                errors=str(exc),
                report_summary="Export failed.",
            )
            db.session.add(history)
            db.session.commit()
            return {"message": str(exc)}, 400
        except Exception as exc:
            source_db_type = payload.get("source_db_type", "sqlite")
            source_host = payload.get("source_host", "localhost")
            history = MigrationHistory(
                migration_type="sql_to_file",
                source_db=f"{source_db_type}://{source_host}",
                target_db="file://unknown",
                status="failed",
                errors=str(exc),
                report_summary="Export failed.",
            )
            db.session.add(history)
            db.session.commit()
            return {"message": "Export failed.", "error": str(exc)}, 500


class DownloadExportResource(Resource):
    """Endpoint to download exported files."""

    def get(self, filename: str):
        import os
        from flask import send_from_directory
        from werkzeug.utils import secure_filename
        from backend.utils.file_handler import resolve_export_path
        
        filename = secure_filename(filename)
        export_dir = os.path.dirname(resolve_export_path(filename))
        return send_from_directory(export_dir, filename, as_attachment=True)



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


class TestConnectionResource(Resource):
    """Endpoint to test a database connection without performing a migration."""

    def post(self):
        payload = request.get_json(silent=True) or {}

        if not payload:
            return {"status": "error", "message": "Request body is required."}, 400

        db_type = (payload.get("db_type") or "").strip().lower()
        if not db_type:
            return {"status": "error", "message": "db_type is required."}, 400

        config = {
            "db_type": db_type,
            "username": payload.get("username") or "",
            "password": payload.get("password") or "",
            "host": payload.get("host") or "localhost",
            "port": payload.get("port") or "",
            "database": payload.get("database") or (
                _DEFAULT_SQLITE_DB_FALLBACK if db_type == "sqlite" else ""
            ),
        }

        # Per-driver connect timeout (5 s) so a bad host doesn't stall the server
        connect_args: dict = {}
        if db_type in ("postgres", "postgresql"):
            connect_args = {"connect_timeout": 5}
        elif db_type == "mysql":
            connect_args = {"connect_timeout": 5}

        try:
            engine = create_engine_for_config(config, connect_args=connect_args)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return {
                "status": "ok",
                "message": f"Connected successfully to {db_type}.",
                "db_type": db_type,
            }, 200
        except Exception as exc:
            # Strip verbose SQLAlchemy boilerplate from the error message
            raw = str(exc)
            # Take only the first meaningful line before the long traceback hint
            short = raw.split("\n")[0].split("(Background")[0].strip()
            return {
                "status": "error",
                "message": short or raw,
                "db_type": db_type,
            }, 200   # Always 200 so the frontend receives JSON, not a fetch error


class DashboardStatsResource(Resource):
    """Endpoint to fetch combined statistics for the dashboard."""

    @jwt_required()
    def get(self):
        from flask_jwt_extended import jwt_required
        
        total = MigrationHistory.query.count()
        successful = MigrationHistory.query.filter_by(status="completed").count()
        failed = MigrationHistory.query.filter_by(status="failed").count()
        reports_count = Report.query.count()

        # Count databases usage from history
        db_counts = {"mysql": 0, "postgres": 0, "sqlite": 0, "oracle": 0}
        for r in MigrationHistory.query.all():
            src_type = r.source_db.split("://")[0].lower()
            tgt_type = r.target_db.split("://")[0].lower()
            for t in (src_type, tgt_type):
                if "mysql" in t:
                    db_counts["mysql"] += 1
                elif "postgres" in t:
                    db_counts["postgres"] += 1
                elif "sqlite" in t:
                    db_counts["sqlite"] += 1
                elif "oracle" in t:
                    db_counts["oracle"] += 1

        # Fetch 5 most recent activities
        recent_records = MigrationHistory.query.order_by(MigrationHistory.timestamp.desc()).limit(5).all()
        recent_activity = []
        for r in recent_records:
            action_desc = ""
            if r.migration_type == "sql_to_sql":
                action_desc = "Completed SQL to SQL migration"
            elif r.migration_type == "sql_to_file":
                fmt = r.target_db.split(".")[-1].upper() if "." in r.target_db else "FILE"
                action_desc = f"Exported table to {fmt}"
            elif r.migration_type == "file_to_sql":
                action_desc = f"Imported file into {r.target_db.split('://')[0].upper()}"
            
            recent_activity.append({
                "user": "System User",
                "action": action_desc or "Database operation",
                "time": r.timestamp.isoformat()
            })

        return {
            "total_migrations": total,
            "successful": successful,
            "failed": failed,
            "reports": reports_count,
            "database_usage": db_counts,
            "recent_activity": recent_activity
        }, 200

