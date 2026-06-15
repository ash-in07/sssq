from typing import Any, Dict, List
from sqlalchemy import MetaData, Table, Column, inspect
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd

from backend.database.connection_manager import create_engine_for_config
from backend.validators.migration_validator import validate_table_counts
from backend.converters.datatype_mapper import map_datatype


def build_table_schema(source_engine, table_name: str, target_db_type: str) -> Table:
    """Build a target SQLAlchemy Table object from a source table schema."""
    source_meta = MetaData()
    target_meta = MetaData()
    source_table = Table(table_name, source_meta, autoload_with=source_engine)

    columns = []
    for column in source_table.columns:
        mapped_type = map_datatype(str(column.type), target_db_type)
        column_args = {
            "primary_key": column.primary_key,
            "nullable": column.nullable,
        }
        columns.append(Column(column.name, mapped_type, **column_args))

    return Table(table_name, target_meta, *columns)


def migrate_sql_to_sql(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Perform a SQL-to-SQL migration workflow between two databases."""
    source_config = {
        "db_type": payload.get("source_db_type"),
        "username": payload.get("source_username"),
        "password": payload.get("source_password"),
        "host": payload.get("source_host"),
        "port": payload.get("source_port"),
        "database": payload.get("source_database"),
    }
    target_config = {
        "db_type": payload.get("target_db_type"),
        "username": payload.get("target_username"),
        "password": payload.get("target_password"),
        "host": payload.get("target_host"),
        "port": payload.get("target_port"),
        "database": payload.get("target_database"),
    }
    selected_tables = payload.get("tables") or []

    source_engine = create_engine_for_config(source_config)
    target_engine = create_engine_for_config(target_config)
    inspector = inspect(source_engine)
    source_tables = inspector.get_table_names()
    tables = selected_tables if selected_tables else source_tables

    if not tables:
        raise ValueError("No tables were selected for migration.")

    summary: List[Dict[str, Any]] = []
    for table_name in tables:
        if table_name not in source_tables:
            summary.append({"table": table_name, "status": "skipped", "reason": "Table not found on source."})
            continue

        try:
            target_table = build_table_schema(source_engine, table_name, target_config["db_type"])
            target_table.metadata.create_all(target_engine)

            data_frame = pd.read_sql_table(table_name, source_engine)
            if not data_frame.empty:
                data_frame.to_sql(table_name, target_engine, if_exists="append", index=False)
            validation = validate_table_counts(source_engine, target_engine, table_name)
            summary.append({
                "table": table_name,
                "rows_transferred": int(data_frame.shape[0]),
                "validation": validation,
                "status": "completed",
            })
        except SQLAlchemyError as error:
            summary.append({"table": table_name, "status": "failed", "error": str(error)})

    return {
        "summary": summary,
        "tables": tables,
        "source_db": source_config,
        "target_db": target_config,
    }
