"""Anonymous usage / feedback counters (SQLite). No birth data or question text."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent
DEFAULT_DB_PATH = ROOT / "cache" / "usage.sqlite"

COUNTER_MAIN = "main_report"
COUNTER_WITH_Q = "with_question"
COUNTER_WITHOUT_Q = "without_question"


@dataclass(frozen=True)
class UsageStats:
    total: int
    with_question: int
    without_question: int


def _db_path(override: Optional[Path] = None) -> Path:
    return Path(override) if override is not None else DEFAULT_DB_PATH


def _connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), timeout=5)
    # Explicit autocommit-friendly mode; avoid nested BEGIN issues.
    conn.isolation_level = None
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS counters (
            name TEXT PRIMARY KEY,
            value INTEGER NOT NULL DEFAULT 0
        )
        """
    )
    return conn


def _run(path: Path, fn):
    conn = _connect(path)
    try:
        return fn(conn)
    finally:
        conn.close()


def _get_counter(conn: sqlite3.Connection, name: str) -> int:
    row = conn.execute(
        "SELECT value FROM counters WHERE name = ?", (name,)
    ).fetchone()
    return int(row[0]) if row else 0


def _bump(conn: sqlite3.Connection, name: str, delta: int = 1) -> None:
    conn.execute(
        """
        INSERT INTO counters(name, value) VALUES(?, ?)
        ON CONFLICT(name) DO UPDATE SET value = value + excluded.value
        """,
        (name, delta),
    )


def get_usage_stats(
    *,
    db_path: Optional[Path] = None,
    total_base: int = 0,
    question_base: int = 0,
) -> UsageStats:
    path = _db_path(db_path)
    try:
        def _read(conn: sqlite3.Connection):
            return (
                _get_counter(conn, COUNTER_MAIN),
                _get_counter(conn, COUNTER_WITH_Q),
                _get_counter(conn, COUNTER_WITHOUT_Q),
            )

        total, with_q, without_q = _run(path, _read)
    except Exception:  # noqa: BLE001 — never break the app for stats
        return UsageStats(total=max(0, total_base), with_question=max(0, question_base), without_question=0)
    return UsageStats(
        total=max(0, total_base) + total,
        with_question=max(0, question_base) + with_q,
        without_question=without_q,
    )


def record_successful_report(
    *,
    has_question: bool,
    db_path: Optional[Path] = None,
) -> UsageStats:
    """Increment main + with/without question. Safe no-op on DB errors."""
    path = _db_path(db_path)
    try:
        def _write(conn: sqlite3.Connection):
            _bump(conn, COUNTER_MAIN, 1)
            if has_question:
                _bump(conn, COUNTER_WITH_Q, 1)
            else:
                _bump(conn, COUNTER_WITHOUT_Q, 1)
            conn.commit()

        _run(path, _write)
    except Exception:  # noqa: BLE001
        return get_usage_stats(db_path=path)
    return get_usage_stats(db_path=path)


def record_section_feedback(
    *,
    section: int,
    hit: bool,
    db_path: Optional[Path] = None,
) -> None:
    """Increment s{n}_hit or s{n}_miss. Ignores DB errors."""
    if section < 1 or section > 5:
        return
    key = f"s{section}_{'hit' if hit else 'miss'}"
    path = _db_path(db_path)
    try:
        def _write(conn: sqlite3.Connection):
            _bump(conn, key, 1)
            conn.commit()

        _run(path, _write)
    except Exception:  # noqa: BLE001
        return


def get_section_feedback_counts(
    section: int,
    *,
    db_path: Optional[Path] = None,
) -> tuple[int, int]:
    path = _db_path(db_path)
    try:
        def _read(conn: sqlite3.Connection):
            return (
                _get_counter(conn, f"s{section}_hit"),
                _get_counter(conn, f"s{section}_miss"),
            )

        return _run(path, _read)
    except Exception:  # noqa: BLE001
        return 0, 0
