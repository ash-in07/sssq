from typing import List
from sqlalchemy import inspect


def check_column_compatibility(source_engine, target_engine, table_name: str) -> List[str]:
    """Check whether source and target column types appear compatible."""
    source_inspector = inspect(source_engine)
    target_inspector = inspect(target_engine)
    errors = []

    if table_name not in source_inspector.get_table_names():
        return [f"Source table {table_name} was not found."]
    if table_name not in target_inspector.get_table_names():
        return [f"Target table {table_name} was not found."]

    source_columns = {col["name"]: col for col in source_inspector.get_columns(table_name)}
    target_columns = {col["name"]: col for col in target_inspector.get_columns(table_name)}

    for name, source_col in source_columns.items():
        if name not in target_columns:
            errors.append(f"Missing target column: {name}")
            continue

        source_type = str(source_col.get("type", "")).lower()
        target_type = str(target_columns[name].get("type", "")).lower()
        if source_type != target_type and not any(token in target_type for token in source_type.split()):
            errors.append(f"Column type mismatch for '{name}': source={source_type}, target={target_type}")

    return errors
