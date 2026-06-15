from typing import Dict, Any, Optional
from urllib.parse import quote_plus
from sqlalchemy import create_engine


def create_mysql_engine(
    username: str,
    password: str,
    host: str,
    port: str,
    database: str,
    connect_args: Optional[Dict[str, Any]] = None,
):
    """Create a SQLAlchemy engine for a MySQL database using pymysql."""
    encoded_user = quote_plus(username)
    encoded_password = quote_plus(password)
    connection_string = (
        f"mysql+pymysql://{encoded_user}:{encoded_password}@{host}:{port}/{database}"
    )
    return create_engine(connection_string, pool_pre_ping=True, connect_args=connect_args or {})
