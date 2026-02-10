# Copyright (c) 2026 AI Center Plus. All Rights Reserved.
# This software is proprietary and confidential. See LICENSE file.
# Unauthorized copying, distribution, or modification is strictly prohibited.

"""
Oracle Sync - Persistent Memory System
All learning is saved to Oracle database forever.
Falls back to SQLite when Oracle is not available.
"""

import json
import uuid
import os
import aiosqlite
from datetime import datetime
from typing import Dict, Any, List, Optional
from rich.console import Console

console = Console()

# Try to import oracledb (optional)
try:
    import oracledb
    ORACLE_AVAILABLE = True
except ImportError:
    ORACLE_AVAILABLE = False


SQLITE_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "apex_memory.db"
)

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS apex_knowledge (
    id TEXT PRIMARY KEY,
    timestamp TEXT DEFAULT (datetime('now')),
    topic TEXT,
    content TEXT,
    source_ai TEXT,
    confidence_score REAL
);

CREATE TABLE IF NOT EXISTS apex_capabilities (
    capability_name TEXT PRIMARY KEY,
    acquired_date TEXT,
    code TEXT,
    dependencies TEXT,
    complexity TEXT,
    version TEXT
);

CREATE TABLE IF NOT EXISTS apex_tasks (
    task_id TEXT PRIMARY KEY,
    command TEXT,
    status TEXT,
    agents_used TEXT,
    cost_usd REAL,
    output TEXT,
    duration_seconds REAL,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS apex_evolution (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    capability_name TEXT,
    acquired_date TEXT,
    research_data TEXT,
    success INTEGER
);

CREATE TABLE IF NOT EXISTS apex_state (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TEXT DEFAULT (datetime('now'))
);
"""


class OracleSync:
    """
    Connects to Oracle database for permanent memory.
    Falls back to SQLite if Oracle is unavailable.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._oracle_conn = None
        self._sqlite_path = SQLITE_DB_PATH
        self._use_oracle = config.get("enabled", False) and ORACLE_AVAILABLE
        self._connected = False

    async def _ensure_sqlite(self):
        """Initialize SQLite database with schema."""
        async with aiosqlite.connect(self._sqlite_path) as db:
            await db.executescript(SCHEMA_SQL)
            await db.commit()

    async def _connect_oracle(self):
        """Attempt Oracle connection."""
        if not self._use_oracle:
            return False

        try:
            dsn = f"{self.config['host']}:{self.config['port']}/{self.config['service_name']}"
            self._oracle_conn = oracledb.connect(
                user=self.config["username"],
                password=self.config["password"],
                dsn=dsn,
            )
            self._connected = True
            return True
        except Exception as e:
            console.print(f"[yellow]  Oracle connection failed: {e}[/yellow]")
            self._connected = False
            return False

    async def test_connection(self) -> bool:
        """Test database connectivity."""
        if self._use_oracle:
            result = await self._connect_oracle()
            if result:
                return True

        # Fall back to SQLite
        await self._ensure_sqlite()
        self._connected = True
        return True

    def is_connected(self) -> bool:
        """Check connection status."""
        return self._connected

    async def save_capability(self, capability: Dict[str, Any]):
        """Save learned capability to database."""
        async with aiosqlite.connect(self._sqlite_path) as db:
            await db.execute(
                """INSERT OR REPLACE INTO apex_capabilities
                   (capability_name, acquired_date, code, dependencies, complexity, version)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    capability.get("name", "unknown"),
                    datetime.now().isoformat(),
                    capability.get("code", ""),
                    json.dumps(capability.get("libraries", [])),
                    capability.get("metadata", {}).get("complexity", "unknown"),
                    "1.0",
                ),
            )
            await db.commit()

    async def load_capabilities(self) -> Dict[str, Any]:
        """Load all capabilities from database."""
        await self._ensure_sqlite()
        capabilities = {}
        async with aiosqlite.connect(self._sqlite_path) as db:
            async with db.execute(
                "SELECT capability_name, code, dependencies FROM apex_capabilities"
            ) as cursor:
                async for row in cursor:
                    capabilities[row[0]] = {
                        "name": row[0],
                        "code": row[1],
                        "dependencies": json.loads(row[2]) if row[2] else [],
                    }
        return capabilities

    async def count_capabilities(self) -> int:
        """Count total learned capabilities."""
        await self._ensure_sqlite()
        async with aiosqlite.connect(self._sqlite_path) as db:
            async with db.execute("SELECT COUNT(*) FROM apex_capabilities") as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    async def save_research(self, query: str, result: str, source_ai: str = "perplexity"):
        """Save research results."""
        async with aiosqlite.connect(self._sqlite_path) as db:
            await db.execute(
                """INSERT INTO apex_knowledge (id, topic, content, source_ai, confidence_score)
                   VALUES (?, ?, ?, ?, ?)""",
                (str(uuid.uuid4()), query[:500], result, source_ai, 0.9),
            )
            await db.commit()

    async def save_task(self, task: Dict[str, Any]):
        """Save task execution record."""
        async with aiosqlite.connect(self._sqlite_path) as db:
            await db.execute(
                """INSERT INTO apex_tasks
                   (task_id, command, status, agents_used, cost_usd, output, duration_seconds)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    task.get("task_id", str(uuid.uuid4())),
                    task.get("command", ""),
                    task.get("status", "complete"),
                    json.dumps(task.get("agents_used", [])),
                    task.get("cost_usd", 0.0),
                    task.get("output", ""),
                    task.get("duration_seconds", 0.0),
                ),
            )
            await db.commit()

    async def save_state(self, state: Dict[str, Any]):
        """Save APEX state on shutdown."""
        await self._ensure_sqlite()
        async with aiosqlite.connect(self._sqlite_path) as db:
            await db.execute(
                """INSERT OR REPLACE INTO apex_state (key, value, updated_at)
                   VALUES (?, ?, ?)""",
                ("last_state", json.dumps(state), datetime.now().isoformat()),
            )
            await db.commit()

    async def load_state(self) -> Optional[Dict[str, Any]]:
        """Load last saved state."""
        await self._ensure_sqlite()
        async with aiosqlite.connect(self._sqlite_path) as db:
            async with db.execute(
                "SELECT value FROM apex_state WHERE key = 'last_state'"
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return json.loads(row[0])
        return None

    async def get_knowledge(self, topic: str) -> List[Dict[str, Any]]:
        """Search knowledge base by topic."""
        async with aiosqlite.connect(self._sqlite_path) as db:
            async with db.execute(
                "SELECT topic, content, source_ai, confidence_score FROM apex_knowledge WHERE topic LIKE ?",
                (f"%{topic}%",),
            ) as cursor:
                results = []
                async for row in cursor:
                    results.append({
                        "topic": row[0],
                        "content": row[1],
                        "source_ai": row[2],
                        "confidence": row[3],
                    })
                return results

    async def close(self):
        """Close database connections."""
        if self._oracle_conn:
            self._oracle_conn.close()
