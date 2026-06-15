"""sql_dump_processor.py
Parses and executes a SQL dump file against a SQLAlchemy engine.

Strategy (strict/transactional):
- The entire dump is executed inside a single BEGIN … COMMIT block.
- If any statement raises an error the transaction is rolled back and the
  error is re-raised so the caller can surface it cleanly.
- Known non-portable directives (MySQL SET, LOCK TABLES, USE, /*!…*/ comments)
  are silently skipped so that MySQL dumps work reasonably against other targets.
"""

import re
import os
from typing import Dict, Any, List, Optional

from sqlalchemy.engine import Engine
from sqlalchemy import text, inspect


# ---------------------------------------------------------------------------
# Patterns for statements we want to skip silently
# ---------------------------------------------------------------------------
_SKIP_PATTERNS: List[re.Pattern] = [
    re.compile(r"^\s*SET\s+", re.IGNORECASE),                    # MySQL SET @@session.xxx
    re.compile(r"^\s*LOCK\s+TABLES\s+", re.IGNORECASE),
    re.compile(r"^\s*UNLOCK\s+TABLES", re.IGNORECASE),
    re.compile(r"^\s*USE\s+\w+\s*$", re.IGNORECASE),            # USE db_name
    re.compile(r"^/\*!", re.IGNORECASE),                         # /*!50003 … */ MySQL versioned comments
]


def _should_skip(stmt: str) -> bool:
    """Return True if this statement should be silently skipped."""
    stmt = stmt.strip()
    return any(p.match(stmt) for p in _SKIP_PATTERNS)


def parse_sql_statements(sql_text: str) -> List[str]:
    """Split a SQL dump into individual executable statements.

    Handles:
    - Single-line ``--`` and ``#`` comments (stripped)
    - Block ``/* … */`` comments (stripped)
    - String literals that contain semicolons (not treated as terminators)
    - The final statement even if it has no trailing semicolon
    """
    # Remove block comments (non-greedy so we don't eat too much)
    sql_text = re.sub(r"/\*.*?\*/", " ", sql_text, flags=re.DOTALL)

    statements: List[str] = []
    current: List[str] = []
    in_single_quote = False
    in_double_quote = False
    i = 0
    n = len(sql_text)

    while i < n:
        ch = sql_text[i]

        # Track string delimiters so ';' inside a string is not a terminator
        if ch == "'" and not in_double_quote:
            in_single_quote = not in_single_quote
        elif ch == '"' and not in_single_quote:
            in_double_quote = not in_double_quote

        # Strip line comments outside strings
        if not in_single_quote and not in_double_quote:
            # -- comment or # comment
            if (ch == "-" and i + 1 < n and sql_text[i + 1] == "-") or ch == "#":
                # Skip to end of line
                while i < n and sql_text[i] != "\n":
                    i += 1
                continue

            if ch == ";" :
                stmt = "".join(current).strip()
                if stmt:
                    statements.append(stmt)
                current = []
                i += 1
                continue

        current.append(ch)
        i += 1

    # Handle trailing statement without semicolon
    remainder = "".join(current).strip()
    if remainder:
        statements.append(remainder)

    return statements


def extract_table_name_from_create(stmt: str) -> Optional[str]:
    """Extract table name from a CREATE TABLE statement."""
    match = re.search(
        r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([`\"\w\.-]+)",
        stmt,
        re.IGNORECASE
    )
    if match:
        name = match.group(1)
        return name.replace("`", "").replace('"', "").strip()
    return None


def import_sql_dump(file_path: str, target_engine: Engine, if_exists: str = "fail") -> Dict[str, Any]:
    """Read *file_path* and execute all SQL statements against *target_engine*.

    Handles table collisions:
    - fail: raises ValueError if any table to create already exists.
    - replace: drops existing conflicting tables before execution.
    - append: converts CREATE TABLE to CREATE TABLE IF NOT EXISTS.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"SQL dump not found: {file_path}")

    if_exists = if_exists.strip().lower()

    with open(file_path, "r", encoding="utf-8", errors="replace") as fh:
        raw_sql = fh.read()

    statements = parse_sql_statements(raw_sql)

    # 1. Check for table collisions
    tables_to_create = []
    for stmt in statements:
        if stmt.strip().upper().startswith("CREATE TABLE"):
            tname = extract_table_name_from_create(stmt)
            if tname:
                tables_to_create.append(tname)

    if tables_to_create:
        try:
            existing_tables = inspect(target_engine).get_table_names()
        except Exception:
            existing_tables = []

        overlap = [t for t in tables_to_create if t in existing_tables]
        if overlap:
            if if_exists == "fail":
                tables_str = ", ".join(f"'{t}'" for t in overlap)
                raise ValueError(
                    f"Table(s) {tables_str} already exist in the target database. "
                    "Please select 'Replace' to overwrite existing tables, or 'Append' to add rows."
                )
            elif if_exists == "replace":
                with target_engine.begin() as conn:
                    for t in overlap:
                        quoted_t = target_engine.dialect.identifier_preparer.quote(t)
                        conn.execute(text(f"DROP TABLE IF EXISTS {quoted_t}"))
            elif if_exists == "append":
                for idx, stmt in enumerate(statements):
                    if stmt.strip().upper().startswith("CREATE TABLE"):
                        if "IF NOT EXISTS" not in stmt.upper():
                            statements[idx] = re.sub(
                                r"\bCREATE\s+TABLE\b",
                                "CREATE TABLE IF NOT EXISTS",
                                stmt,
                                count=1,
                                flags=re.IGNORECASE
                            )

    executed = 0
    skipped = 0

    with target_engine.begin() as conn:          # auto-commit or rollback
        for stmt in statements:
            clean = stmt.strip()
            if not clean:
                continue
            if _should_skip(clean):
                skipped += 1
                continue
            conn.execute(text(clean))
            executed += 1

    # Best-effort: extract DB path/name from engine URL for reporting
    try:
        db_label = str(target_engine.url.database or target_engine.url)
    except Exception:
        db_label = str(target_engine.url)

    return {
        "statements_executed": executed,
        "statements_skipped": skipped,
        "target_database": db_label,
    }
