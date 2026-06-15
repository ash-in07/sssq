from sqlalchemy import create_engine


def create_sqlite_engine(database: str):
    """Create a SQLAlchemy engine for a SQLite database file."""
    connection_string = f"sqlite:///{database}"
    return create_engine(connection_string, connect_args={"check_same_thread": False})
