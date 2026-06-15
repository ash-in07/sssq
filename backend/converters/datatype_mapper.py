from sqlalchemy import Integer, String, Text, Float, DateTime, Boolean, LargeBinary


def map_datatype(source_type: str, target_db_type: str):
    """Map a source column type string to a target database SQLAlchemy type."""
    lower_type = source_type.lower()
    if "int" in lower_type or "serial" in lower_type:
        return Integer
    if "char" in lower_type or "text" in lower_type or "clob" in lower_type:
        return Text
    if "varchar" in lower_type or "string" in lower_type or "nvarchar" in lower_type:
        return String(255)
    if "float" in lower_type or "double" in lower_type or "real" in lower_type:
        return Float
    if "bool" in lower_type or "bit" in lower_type:
        return Boolean
    if "datetime" in lower_type or "timestamp" in lower_type or "date" in lower_type:
        return DateTime
    if "binary" in lower_type or "blob" in lower_type:
        return LargeBinary
    return String(255)
