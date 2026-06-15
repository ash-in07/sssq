import os
import pandas as pd
from typing import Optional
from backend.utils.file_handler import resolve_upload_path

_TYPE_MAP = {
    "int64": "INTEGER",
    "int32": "INTEGER",
    "int16": "INTEGER",
    "int8": "INTEGER",
    "float64": "REAL",
    "float32": "REAL",
    "bool": "BOOLEAN",
    "datetime64[ns]": "DATETIME",
    "object": "TEXT",
}


def _needs_quoting(name: str) -> bool:
    """Return True if a column name needs double-quote wrapping in SQL."""
    import re
    # Quote if name contains spaces, special chars, or starts with a digit
    return bool(re.search(r'[^a-zA-Z0-9_]', name) or (name and name[0].isdigit()))


def _quote_col(name: str) -> str:
    """Wrap column name in double-quotes, escaping any existing double-quotes."""
    escaped = name.replace('"', '""')
    return f'"{escaped}"'


def infer_sql_type(dtype: str, series=None) -> str:
    """Infer a SQL data type string from a pandas dtype.
    
    When dtype is 'object' and a pandas Series is provided, sniff the
    actual Python types stored in the column to detect hidden datetimes.
    """
    # Fast path for explicitly typed columns
    for key, sql_type in _TYPE_MAP.items():
        if dtype.startswith(key):
            return sql_type

    # For object columns, check if the values are datetime objects
    if dtype == "object" and series is not None:
        import datetime
        sample = series.dropna().head(20)
        if len(sample) > 0 and all(
            isinstance(v, (datetime.datetime, datetime.date)) for v in sample
        ):
            return "DATETIME"

    return "TEXT"


def generate_create_table_schema(file_path: str, table_name: Optional[str] = None) -> str:
    """Generate a CREATE TABLE SQL statement from a CSV or Excel file."""
    if not table_name:
        table_name = os.path.splitext(os.path.basename(file_path))[0]

    extension = os.path.splitext(file_path)[1].lower()
    if extension == ".csv":
        data_frame = pd.read_csv(file_path)
    elif extension == ".json":
        import json as _json
        with open(file_path, "r", encoding="utf-8") as fh:
            raw = _json.load(fh)
        if isinstance(raw, list):
            data_frame = pd.DataFrame(raw)
        elif isinstance(raw, dict):
            for key in ("data", "rows", "records", "results"):
                if key in raw and isinstance(raw[key], list):
                    data_frame = pd.DataFrame(raw[key])
                    break
            else:
                data_frame = pd.DataFrame([raw])
        else:
            data_frame = pd.DataFrame()
    else:
        data_frame = pd.read_excel(file_path)

    # Strip surrounding whitespace from column names (matches import behaviour)
    data_frame.columns = [str(c).strip() for c in data_frame.columns]

    columns = []
    for column_name, dtype in data_frame.dtypes.items():
        sql_type = infer_sql_type(str(dtype), data_frame[column_name])
        col_def_name = _quote_col(column_name) if _needs_quoting(str(column_name)) else column_name
        columns.append(f"{col_def_name} {sql_type}")

    sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n    id INTEGER PRIMARY KEY AUTOINCREMENT,\n    "
    sql += ",\n    ".join(columns)
    sql += "\n);"
    return sql
