import os
import json
import pandas as pd
from typing import Dict, Any
from backend.database.connection_manager import create_engine_for_config
from backend.processors.csv_processor import read_csv_file
from backend.processors.excel_processor import read_excel_file
from backend.processors.schema_generator import generate_create_table_schema
from backend.processors.sql_dump_processor import import_sql_dump
from backend.utils.file_handler import resolve_upload_path

# Absolute path to the default SQLite database, resolved relative to this file
_DEFAULT_SQLITE_DB = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "database", "migration_target.db")
)


def _read_file(file_path: str) -> pd.DataFrame:
    """Read a CSV, JSON, or Excel file into a pandas DataFrame."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        return read_csv_file(file_path)
    if ext == ".json":
        with open(file_path, "r", encoding="utf-8") as fh:
            raw = json.load(fh)
        # Accept both a list-of-records and a dict with a data key
        if isinstance(raw, list):
            return pd.DataFrame(raw)
        if isinstance(raw, dict):
            # Try common wrapper keys
            for key in ("data", "rows", "records", "results"):
                if key in raw and isinstance(raw[key], list):
                    return pd.DataFrame(raw[key])
            return pd.DataFrame([raw])
        raise ValueError(f"Unsupported JSON structure in {file_path}.")
    if ext in (".xlsx", ".xls"):
        return read_excel_file(file_path)
    raise ValueError(
        f"Unsupported file extension '{ext}'. Supported types: .csv, .json, .xlsx, .xls"
    )


def import_file_to_sql(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Import a CSV, JSON, Excel, or SQL dump file into a target database.

    For tabular files (.csv/.json/.xlsx/.xls) the data is loaded via pandas
    and written with ``DataFrame.to_sql``.

    For SQL dump files (.sql) the statements are executed directly against
    the target engine inside a single transaction (strict mode).
    """
    file_path = payload.get("file_path")
    if file_path is None:
        raise ValueError("File path is required for import.")

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()

    target_db_type = (payload.get("target_db_type") or "sqlite").strip().lower()
    target_database = (payload.get("target_database") or "").strip()

    # Default SQLite target database configuration to avoid app_data.db conflicts
    if not target_database and target_db_type == "sqlite":
        target_database = _DEFAULT_SQLITE_DB
    elif target_db_type == "sqlite" and not os.path.isabs(target_database):
        # Resolve relative SQLite paths relative to the database directory
        target_database = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "database", target_database)
        )

    target_config = {
        "db_type": target_db_type,
        "username": payload.get("target_username", ""),
        "password": payload.get("target_password", ""),
        "host": payload.get("target_host", "localhost"),
        "port": payload.get("target_port", ""),
        "database": target_database,
    }
    target_engine = create_engine_for_config(target_config)

    # ------------------------------------------------------------------ SQL dump
    if ext == ".sql":
        dump_result = import_sql_dump(file_path, target_engine)
        return {
            "import_type": "sql_dump",
            "file_name": os.path.basename(file_path),
            "statements_executed": dump_result["statements_executed"],
            "statements_skipped": dump_result["statements_skipped"],
            "rows_imported": None,
            "schema_sql": None,
            "target_database": dump_result["target_database"],
        }

    # ------------------------------------------------ Tabular: CSV / JSON / Excel
    data_frame = _read_file(file_path)
    table_name = payload.get("target_table") or os.path.splitext(os.path.basename(file_path))[0]

    # Sanitize column names: strip surrounding whitespace to avoid hard-to-query column names
    # (e.g. 'selling rate ' with trailing space becomes 'selling rate')
    data_frame.columns = [col.strip() for col in data_frame.columns]

    data_frame.to_sql(table_name, target_engine, if_exists=payload.get("if_exists", "replace"), index=False)

    schema_sql = generate_create_table_schema(file_path, table_name)
    return {
        "import_type": "tabular",
        "file_name": os.path.basename(file_path),
        "table_name": table_name,
        "rows_imported": int(data_frame.shape[0]),
        "schema_sql": schema_sql,
        "target_database": target_config.get("database"),
    }
