def build_json_report(summary: dict) -> dict:
    """Return the report summary as JSON."""
    return summary


def build_text_report(summary: dict) -> str:
    """Build a human-readable text report from a summary dictionary."""
    lines = ["SQL Migrator Report", "====================", ""]
    lines.append(f"Source: {summary.get('source_db')}")
    lines.append(f"Target: {summary.get('target_db')}")
    lines.append(f"Tables: {', '.join(str(table) for table in summary.get('tables', []))}")
    lines.append("")
    for table_info in summary.get("summary", []):
        lines.append(f"Table: {table_info.get('table')}")
        lines.append(f"  Status: {table_info.get('status')}")
        if table_info.get("rows_transferred") is not None:
            lines.append(f"  Rows transferred: {table_info.get('rows_transferred')}")
        if table_info.get("error"):
            lines.append(f"  Error: {table_info.get('error')}")
        lines.append("")
    return "\n".join(lines)
