from sqlalchemy import inspect, text


def validate_table_counts(source_engine, target_engine, table_name: str) -> dict:
    """Compare row counts for a source and target table to validate migration."""

    source_inspector = inspect(source_engine)
    target_inspector = inspect(target_engine)

    source_count = None
    target_count = None

    if table_name in source_inspector.get_table_names():
        with source_engine.connect() as connection:
            source_count = connection.execute(
                text(f"SELECT COUNT(*) FROM {table_name}")
            ).scalar()

    if table_name in target_inspector.get_table_names():
        with target_engine.connect() as connection:
            target_count = connection.execute(
                text(f"SELECT COUNT(*) FROM {table_name}")
            ).scalar()

    return {
        "source_row_count": int(source_count or 0),
        "target_row_count": int(target_count or 0),
        "match": source_count == target_count,
    }