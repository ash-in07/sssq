from sqlalchemy import create_engine


def create_oracle_engine(username: str, password: str, host: str, port: str, service_name: str):
    """Create a SQLAlchemy engine for an Oracle database using cx_Oracle."""
    connection_string = (
        f"oracle+cx_oracle://{username}:{password}@{host}:{port}/?service_name={service_name}"
    )
    return create_engine(connection_string, pool_pre_ping=True)
