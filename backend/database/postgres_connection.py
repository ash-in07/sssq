from urllib.parse import quote_plus
from typing import Dict, Any, Optional
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def create_postgres_engine(
    username: str,
    password: str,
    host: str,
    port: str,
    database: str,
    connect_args: Optional[Dict[str, Any]] = None,
) -> Engine:
    """Create a SQLAlchemy engine for a PostgreSQL database using psycopg2.

    ``connect_args`` is forwarded to psycopg2 and supports keys such as
    ``connect_timeout`` (seconds as int).
    """
    # URL-encode both username and password so special chars (@ % : /) are safe
    encoded_user = quote_plus(username)
    encoded_password = quote_plus(password)

    connection_string = (
        f"postgresql+psycopg2://"
        f"{encoded_user}:{encoded_password}@{host}:{port}/{database}"
    )

    return create_engine(
        connection_string,
        pool_pre_ping=True,
        connect_args=connect_args or {},
    )
