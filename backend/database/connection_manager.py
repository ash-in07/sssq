from typing import Any, Dict, Optional
import os

from sqlalchemy.engine import Engine

from .mysql_connection import create_mysql_engine
from .postgres_connection import create_postgres_engine
from .sqlite_connection import create_sqlite_engine
from .oracle_connection import create_oracle_engine

# Default SQLite DB path (absolute, resolved relative to this file)
_DEFAULT_SQLITE_DB_FALLBACK = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "app_data.db")
)


def create_engine_for_config(config: Dict[str, Any], connect_args: Optional[Dict[str, Any]] = None) -> Engine:
    """Create a SQLAlchemy engine based on common application configuration.

    Args:
        config: dict with keys db_type, username, password, host, port, database.
        connect_args: optional dict passed through to SQLAlchemy's ``connect_args``
            (e.g. ``{"connect_timeout": 5}`` for Postgres/MySQL).
    """
    connect_args = connect_args or {}
    db_type = (config.get("db_type") or "").lower().strip()
    if db_type == "mysql":
        return create_mysql_engine(
            username=config.get("username", ""),
            password=config.get("password", ""),
            host=config.get("host", "localhost"),
            port=config.get("port", "3306"),
            database=config.get("database", ""),
            connect_args=connect_args,
        )
    if db_type in ("postgresql", "postgres"):
        return create_postgres_engine(
            username=config.get("username", ""),
            password=config.get("password", ""),
            host=config.get("host", "localhost"),
            port=config.get("port", "5432"),
            database=config.get("database", ""),
            connect_args=connect_args,
        )
    if db_type == "sqlite":
        return create_sqlite_engine(config.get("database", ":memory:"))
    if db_type == "oracle":
        return create_oracle_engine(
            username=config.get("username", ""),
            password=config.get("password", ""),
            host=config.get("host", "localhost"),
            port=config.get("port", "1521"),
            service_name=config.get("database", "XE"),
        )
    if db_type == "sqlserver":
        # SQL Server uses pyodbc or pymssql — fall back to a basic mssql URL
        from urllib.parse import quote_plus
        user = quote_plus(config.get("username", ""))
        pwd = quote_plus(config.get("password", ""))
        host = config.get("host", "localhost")
        port = config.get("port", "1433")
        database = config.get("database", "")
        from sqlalchemy import create_engine
        url = f"mssql+pymssql://{user}:{pwd}@{host}:{port}/{database}"
        return create_engine(url, connect_args=connect_args)
    supported = ["mysql", "postgresql", "postgres", "sqlite", "oracle", "sqlserver"]
    raise ValueError(
        f"Unsupported database type: '{db_type}'. "
        f"Please select one of: {', '.join(supported)}."
    )

