import os
import pandas as pd
from typing import Dict, Any
from backend.database.connection_manager import create_engine_for_config
from backend.utils.file_handler import resolve_export_path


def export_sql_to_file(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Export SQL query results or full table data to a CSV or Excel file."""
    source_config = {
        "db_type": payload.get("source_db_type", "sqlite"),
        "username": payload.get("source_username", ""),
        "password": payload.get("source_password", ""),
        "host": payload.get("source_host", "localhost"),
        "port": payload.get("source_port", ""),
        "database": payload.get("source_database", "./backend/database/app_data.db"),
    }
    source_engine = create_engine_for_config(source_config)
    table_name = payload.get("source_table")
    export_format = payload.get("export_format", "csv").lower()
    export_path = payload.get("export_path")
    filters = payload.get("filters")
    columns = payload.get("columns") or []

    if table_name is None:
        raise ValueError("Source table name is required for export.")

    query = f"SELECT {', '.join(columns) if columns else '*'} FROM {table_name}"
    if filters:
        query += f" WHERE {filters}"

    df = pd.read_sql_query(query, source_engine)
    if export_path is None or export_path.startswith("<FRONTEND"):
        export_path = resolve_export_path(f"export_{table_name}.{export_format}")

    if export_format == "csv":
        df.to_csv(export_path, index=False)
    elif export_format == "json":
        df.to_json(export_path, orient="records", indent=2)
    else:
        df.to_excel(export_path, index=False)

    return {
        "table_name": table_name,
        "rows_exported": int(df.shape[0]),
        "export_format": export_format,
        "export_path": export_path,
        "filename": os.path.basename(export_path),
    }

