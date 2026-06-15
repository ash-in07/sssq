import os
import tempfile
import pandas as pd
from backend.app import create_app
from backend.extensions import db


def test_schema_generator_creates_sql():
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w", encoding="utf-8") as temp_file:
        temp_file.write("name,age,is_active\nAlice,30,True\nBob,25,False\n")
        path = temp_file.name

    app = create_app()
    with app.app_context():
        sql = None
        from backend.processors.schema_generator import generate_create_table_schema
        sql = generate_create_table_schema(path, "test_users")
        assert "CREATE TABLE IF NOT EXISTS test_users" in sql
        assert "name TEXT" in sql or "name VARCHAR" in sql

    os.unlink(path)


def test_file_import_placeholder_returns_summary():
    os.environ["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app = create_app()
    app.config["TESTING"] = True
    with app.app_context():
        from backend.converters.file_to_sql import import_file_to_sql

        path = tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w", encoding="utf-8").name
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("name,age\nAlice,30\n")

        payload = {
            "file_path": path,
            "target_db_type": "sqlite",
            "target_database": ":memory:",
            "target_table": "imported_users",
            "if_exists": "replace",
        }
        result = import_file_to_sql(payload)
        assert result["table_name"] == "imported_users"

        os.unlink(path)


def test_import_sql_dump_collisions():
    from backend.converters.file_to_sql import import_file_to_sql
    from sqlalchemy import text
    import pytest

    # Create a temporary sql file that creates a table
    with tempfile.NamedTemporaryFile(suffix=".sql", delete=False, mode="w", encoding="utf-8") as temp_file:
        temp_file.write("CREATE TABLE collision_test (id INT, name TEXT);\nINSERT INTO collision_test VALUES (1, 'Alice');\n")
        sql_path = temp_file.name

    # We will use an in-memory SQLite or a temp DB file
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as db_file:
        db_path = db_file.name

    payload = {
        "file_path": sql_path,
        "target_db_type": "sqlite",
        "target_database": db_path,
        "if_exists": "fail",
    }

    try:
        # First import should succeed and create the table
        res1 = import_file_to_sql(payload)
        assert res1["statements_executed"] == 2

        # Second import with "fail" should raise a ValueError
        with pytest.raises(ValueError) as excinfo:
            import_file_to_sql(payload)
        assert "already exist" in str(excinfo.value)

        # Third import with "replace" should succeed
        payload["if_exists"] = "replace"
        res2 = import_file_to_sql(payload)
        assert res2["statements_executed"] == 2

        # Fourth import with "append" should succeed (and insert another row)
        payload["if_exists"] = "append"
        res3 = import_file_to_sql(payload)
        assert res3["statements_executed"] == 2

        # Verify that we have 2 Alice rows now
        from backend.database.connection_manager import create_engine_for_config
        engine = create_engine_for_config({
            "db_type": "sqlite",
            "database": db_path
        })
        with engine.connect() as conn:
            rows = conn.execute(text("SELECT COUNT(*) FROM collision_test")).scalar()
            assert rows == 2

    finally:
        if os.path.exists(sql_path):
            os.unlink(sql_path)
        if os.path.exists(db_path):
            os.unlink(db_path)
