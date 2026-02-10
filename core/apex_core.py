# Copyright (c) 2026 AI Center Plus. All Rights Reserved.
# This software is proprietary and confidential. See LICENSE file.
# Unauthorized copying, distribution, or modification is strictly prohibited.

"""
APEX ORGANISM - Core Orchestrator
The living heart of the digital organism.
Coordinates all subsystems: memory, AI organs, swarm, evolution.
"""

import asyncio
import time
import threading
from datetime import datetime
from typing import Dict, Any, List, Optional
from rich.console import Console
from rich.table import Table

console = Console()


class ApexOrganism:
    """
    The living digital organism.
    Coordinates all subsystems and evolves continuously.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.birth_time = datetime.now()
        self.heartbeat_bpm = 72
        self.capabilities: Dict[str, Any] = {}
        self._running = True

        # Lazy-loaded subsystems
        self._oracle = None
        self._mcp_client = None
        self._evolution_engine = None
        self._swarm_orchestrator = None
        self._money_gate = None
        self._dashboard = None

    @property
    def oracle(self):
        if self._oracle is None:
            from core.oracle_sync import OracleSync
            self._oracle = OracleSync(self.config.get("oracle", {}))
        return self._oracle

    @property
    def mcp_client(self):
        if self._mcp_client is None:
            from core.mcp_client import MCPClient
            self._mcp_client = MCPClient(self.config.get("ai_services", {}))
        return self._mcp_client

    @property
    def evolution_engine(self):
        if self._evolution_engine is None:
            from core.evolution_engine import EvolutionEngine
            self._evolution_engine = EvolutionEngine(self)
        return self._evolution_engine

    @property
    def swarm_orchestrator(self):
        if self._swarm_orchestrator is None:
            from core.swarm_orchestrator import SwarmOrchestrator
            self._swarm_orchestrator = SwarmOrchestrator(self)
        return self._swarm_orchestrator

    @property
    def money_gate(self):
        if self._money_gate is None:
            from core.money_gate import MoneyGate
            self._money_gate = MoneyGate(
                self.config.get("apex", {}).get("money_gate", {})
            )
        return self._money_gate

    async def startup_sequence(self):
        """Organism initialization checks."""
        console.print("\n[bold green]Running startup diagnostics...[/bold green]\n")

        # Check Oracle connection
        oracle_ok = await self.oracle.test_connection()
        if oracle_ok:
            console.print("[green]  Oracle memory: Connected[/green]")
            cap_count = await self.oracle.count_capabilities()
            console.print(f"  Loaded {cap_count} existing capabilities from memory")
        else:
            console.print("[yellow]  Oracle memory: Offline (using local SQLite fallback)[/yellow]")

        # Check AI organs
        active_organs = self.mcp_client.check_connections()
        console.print(f"  AI Organs: {active_organs}/6 active")

        # Load capabilities from memory
        self.capabilities = await self.oracle.load_capabilities()

        # Start heartbeat
        self._start_heartbeat()

        # Display status table
        self._display_status_table()

    def _start_heartbeat(self):
        """Living organism heartbeat (background thread)."""
        def pulse():
            while self._running:
                time.sleep(60.0 / self.heartbeat_bpm)

        heartbeat_thread = threading.Thread(target=pulse, daemon=True)
        heartbeat_thread.start()

    def _display_status_table(self):
        """Display a rich status table."""
        table = Table(title="APEX Organism Status", border_style="green")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details", style="white")

        # Oracle
        oracle_status = "ONLINE" if self.oracle.is_connected() else "FALLBACK (SQLite)"
        table.add_row("Memory Core", oracle_status, "Persistent storage")

        # AI Organs
        for name, svc in self.config.get("ai_services", {}).items():
            if isinstance(svc, dict) and svc.get("enabled"):
                table.add_row(
                    f"  {name.capitalize()}",
                    "ACTIVE",
                    svc.get("role", "General")
                )

        # Capabilities
        table.add_row(
            "Capabilities",
            str(len(self.capabilities)),
            "Learned skills"
        )

        # Intelligence
        intelligence = self.calculate_intelligence()
        table.add_row("Intelligence", f"{intelligence}%", "Growing...")

        console.print(table)

    def get_status(self) -> Dict[str, Any]:
        """Get current organism status as a dictionary."""
        return {
            "health": 100,
            "intelligence": self.calculate_intelligence(),
            "oracle_connected": self.oracle.is_connected(),
            "ai_organs_active": self.mcp_client.count_active_organs(),
            "capabilities_count": len(self.capabilities),
            "capabilities": list(self.capabilities.keys()),
            "uptime_seconds": (datetime.now() - self.birth_time).total_seconds(),
            "version": self.config.get("apex", {}).get("version", "0.1.0"),
        }

    def calculate_intelligence(self) -> int:
        """Calculate intelligence level based on capabilities."""
        base = 10
        per_capability = 0.5
        intelligence = base + (len(self.capabilities) * per_capability)
        return min(int(intelligence), 99)

    async def search(self, query: str) -> str:
        """Research using the best available AI organ."""
        console.print(f"[cyan]  Researching '{query}'...[/cyan]")
        result = await self.mcp_client.research(query)
        console.print(f"\n[green]Research Results:[/green]\n{result}\n")
        await self.oracle.save_research(query, result)
        return result

    async def analyze(self, target: str) -> str:
        """Analyze something (file, URL, data)."""
        console.print(f"[cyan]  Analyzing '{target}'...[/cyan]")
        result = await self.mcp_client.analyze(target)
        console.print(f"\n[green]Analysis:[/green]\n{result}\n")
        return result

    async def create(self, description: str) -> str:
        """Create something based on description."""
        console.print(f"[cyan]  Creating '{description}'...[/cyan]")
        result = await self.mcp_client.create(description)
        console.print(f"\n[green]Created:[/green]\n{result}\n")
        return result

    async def learn(self, topic: str):
        """Learn a new capability."""
        console.print(f"[cyan]  Learning '{topic}'...[/cyan]")
        await self.evolution_engine.learn_capability(topic)

    async def deploy_swarm(self, num_agents: int, task: str):
        """Deploy a swarm of agents."""
        console.print(f"[cyan]  Deploying {num_agents}-agent swarm for '{task}'...[/cyan]")
        results = await self.swarm_orchestrator.deploy_swarm(num_agents, task)
        return results

    async def shutdown(self):
        """Graceful shutdown - save all state."""
        self._running = False
        console.print("[yellow]  Saving organism state...[/yellow]")
        state = self.get_status()
        await self.oracle.save_state(state)
        await self.oracle.close()
        console.print("[green]  State saved. APEX is hibernating.[/green]")
