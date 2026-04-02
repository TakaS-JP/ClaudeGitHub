"""SQLite-backed persistence layer for the Construction Contract Ledger."""
from __future__ import annotations

import os
import sqlite3
from datetime import date, datetime, timezone
from typing import Optional

from ledger.models.contract import ConstructionContract, ContractStatus

_CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS contracts (
    project_number      TEXT PRIMARY KEY,
    project_name        TEXT NOT NULL,
    location            TEXT NOT NULL,
    start_date          TEXT NOT NULL,
    end_date            TEXT NOT NULL,
    contractor_name     TEXT NOT NULL,
    contract_amount     INTEGER NOT NULL,
    change_amount       INTEGER NOT NULL DEFAULT 0,
    advance_payment     INTEGER NOT NULL DEFAULT 0,
    interim_payment     INTEGER NOT NULL DEFAULT 0,
    completion_payment  INTEGER NOT NULL DEFAULT 0,
    progress_percent    REAL NOT NULL DEFAULT 0.0,
    inspection_date     TEXT,
    completion_date     TEXT,
    notes               TEXT NOT NULL DEFAULT '',
    status              TEXT NOT NULL DEFAULT 'planned',
    created_at          TEXT NOT NULL,
    updated_at          TEXT NOT NULL
);
"""


class LedgerStore:
    """CRUD operations for ConstructionContract records backed by SQLite."""

    def __init__(self, db_path: str) -> None:
        if db_path != ":memory:":
            os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
        self._db_path = db_path
        # For :memory: databases, reuse a single connection (each new connection
        # is a separate in-memory DB). For file-based DBs, open per-operation.
        self._conn: sqlite3.Connection | None = None
        if db_path == ":memory:":
            self._conn = sqlite3.connect(":memory:", check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
        self._init_db()

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def _connect(self) -> sqlite3.Connection:
        if self._conn is not None:
            return self._conn
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        conn = self._connect()
        conn.execute(_CREATE_TABLE_SQL)
        conn.commit()

    # ── CRUD ──────────────────────────────────────────────────────────────────

    def create(self, contract: ConstructionContract) -> None:
        """Persist a new contract. Raises sqlite3.IntegrityError on duplicate project_number."""
        params = self._to_params(contract)
        placeholders = ", ".join(["?"] * len(params))
        columns = ", ".join(params.keys())
        sql = f"INSERT INTO contracts ({columns}) VALUES ({placeholders})"
        with self._connect() as conn:
            conn.execute(sql, list(params.values()))

    def get(self, project_number: str) -> Optional[ConstructionContract]:
        """Return a contract by project_number, or None if not found."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM contracts WHERE project_number = ?",
                (project_number,),
            ).fetchone()
        return self._from_row(row) if row else None

    def update(self, contract: ConstructionContract) -> bool:
        """Overwrite all fields for an existing contract. Returns True if found."""
        params = self._to_params(contract)
        set_clause = ", ".join(f"{k} = ?" for k in params if k != "project_number")
        values = [v for k, v in params.items() if k != "project_number"]
        values.append(contract.project_number)
        sql = f"UPDATE contracts SET {set_clause} WHERE project_number = ?"
        with self._connect() as conn:
            cursor = conn.execute(sql, values)
        return cursor.rowcount > 0

    def delete(self, project_number: str) -> bool:
        """Delete a contract. Returns True if a row was deleted."""
        with self._connect() as conn:
            cursor = conn.execute(
                "DELETE FROM contracts WHERE project_number = ?",
                (project_number,),
            )
        return cursor.rowcount > 0

    # ── Query ─────────────────────────────────────────────────────────────────

    def list_all(self) -> list[ConstructionContract]:
        """Return all contracts ordered by project_number."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM contracts ORDER BY project_number"
            ).fetchall()
        return [self._from_row(r) for r in rows]

    def search(
        self,
        status: Optional[str] = None,
        contractor: Optional[str] = None,
        year: Optional[int] = None,
    ) -> list[ConstructionContract]:
        """Filter contracts by optional criteria."""
        conditions: list[str] = []
        values: list = []

        if status:
            conditions.append("status = ?")
            values.append(status)
        if contractor:
            conditions.append("contractor_name LIKE ?")
            values.append(f"%{contractor}%")
        if year:
            conditions.append("(start_date LIKE ? OR end_date LIKE ?)")
            values.extend([f"{year}-%", f"{year}-%"])

        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        sql = f"SELECT * FROM contracts {where} ORDER BY project_number"

        with self._connect() as conn:
            rows = conn.execute(sql, values).fetchall()
        return [self._from_row(r) for r in rows]

    # ── Serialisation helpers ─────────────────────────────────────────────────

    def _to_params(self, c: ConstructionContract) -> dict:
        return {
            "project_number": c.project_number,
            "project_name": c.project_name,
            "location": c.location,
            "start_date": c.start_date.isoformat(),
            "end_date": c.end_date.isoformat(),
            "contractor_name": c.contractor_name,
            "contract_amount": c.contract_amount,
            "change_amount": c.change_amount,
            "advance_payment": c.advance_payment,
            "interim_payment": c.interim_payment,
            "completion_payment": c.completion_payment,
            "progress_percent": c.progress_percent,
            "inspection_date": c.inspection_date.isoformat() if c.inspection_date else None,
            "completion_date": c.completion_date.isoformat() if c.completion_date else None,
            "notes": c.notes,
            "status": c.status.value,
            "created_at": c.created_at.isoformat(),
            "updated_at": c.updated_at.isoformat(),
        }

    def _from_row(self, row: sqlite3.Row) -> ConstructionContract:
        r = dict(row)
        return ConstructionContract(
            project_number=r["project_number"],
            project_name=r["project_name"],
            location=r["location"],
            start_date=date.fromisoformat(r["start_date"]),
            end_date=date.fromisoformat(r["end_date"]),
            contractor_name=r["contractor_name"],
            contract_amount=r["contract_amount"],
            change_amount=r["change_amount"],
            advance_payment=r["advance_payment"],
            interim_payment=r["interim_payment"],
            completion_payment=r["completion_payment"],
            progress_percent=r["progress_percent"],
            inspection_date=date.fromisoformat(r["inspection_date"]) if r["inspection_date"] else None,
            completion_date=date.fromisoformat(r["completion_date"]) if r["completion_date"] else None,
            notes=r["notes"],
            status=ContractStatus(r["status"]),
            created_at=datetime.fromisoformat(r["created_at"]),
            updated_at=datetime.fromisoformat(r["updated_at"]),
        )
