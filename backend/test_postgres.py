from database.postgres_connection import create_postgres_engine
from sqlalchemy import text

engine = create_postgres_engine(
    username="jishnu",
    password="",
    host="localhost",
    port="5432",
    database="migration_test"
)

with engine.connect() as conn:
    conn.execute(
        text("""
            INSERT INTO python_test (name)
            VALUES (:name)
        """),
        {"name": "Jishnu"}
    )
    conn.commit()

print("Row inserted!")