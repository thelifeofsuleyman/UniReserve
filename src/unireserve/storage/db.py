"""SQLite engine and unit-of-work utilities.

BEGIN IMMEDIATE acquires SQLite's write reservation before reading intervals,
so competing booking decisions are serialized across engine connections.
"""
from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterator
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from .models import Base

def make_engine(path: str | Path, *, busy_timeout_ms: int = 15000) -> Engine:
    path = Path(path).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(
        f"sqlite:///{path.as_posix()}",
        connect_args={"timeout": busy_timeout_ms / 1000, "check_same_thread": False},
        future=True,
    )
    @event.listens_for(engine, "connect")
    def configure_connection(dbapi_connection, connection_record) -> None:
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute(f"PRAGMA busy_timeout={busy_timeout_ms}")
        finally:
            cursor.close()
    return engine

def create_schema(engine: Engine) -> None:
    Base.metadata.create_all(engine)
    # Defense-in-depth: audit events are append-only even if a maintenance
    # script bypasses the application service layer.
    with engine.begin() as connection:
        connection.exec_driver_sql("""
            CREATE TRIGGER IF NOT EXISTS reservation_events_no_update
            BEFORE UPDATE ON reservation_events BEGIN
                SELECT RAISE(ABORT, 'audit events cannot be updated');
            END
        """)
        connection.exec_driver_sql("""
            CREATE TRIGGER IF NOT EXISTS reservation_events_no_delete
            BEFORE DELETE ON reservation_events BEGIN
                SELECT RAISE(ABORT, 'audit events cannot be deleted');
            END
        """)

@contextmanager
def write_transaction(engine: Engine) -> Iterator[Session]:
    """Start the SQLite write transaction before any capacity read."""
    with engine.connect() as connection:
        connection.exec_driver_sql("BEGIN IMMEDIATE")
        with Session(bind=connection, expire_on_commit=False, autoflush=False) as session:
            try:
                yield session
                session.flush()
                connection.commit()
            except BaseException:
                connection.rollback()
                raise
