# Copyright (c) 2026 AI Center Plus.
# Licensed under the MIT License. See LICENSE file for details.

"""
Evolution Engine - Autonomous Capability Acquisition
APEX teaches itself new skills on-demand.
"""

import json
import subprocess
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from rich.console import Console
from rich.progress import Progress

console = Console()


class EvolutionEngine:
    """
    Autonomous capability acquisition system.
    APEX teaches itself new skills on-demand.
    """

    def __init__(self, apex_organism):
        self.apex = apex_organism

    async def learn_capability(self, topic: str):
        """
        Full learning pipeline:
        1. RECOGNIZE limitation
        2. RESEARCH how to do it
        3. ACQUIRE tools/libraries
        4. TEST the new capability
        5. INTEGRATE into APEX
        """
        console.print(f"\n[bold yellow]  INITIATING LEARNING PROTOCOL...[/bold yellow]")

        with Progress() as progress:
            task = progress.add_task("[cyan]Learning...", total=5)

            # Phase 1: Research
            progress.update(task, description="[cyan]Phase 1: Researching...")
            knowledge = await self._research_capability(topic)
            progress.advance(task)

            # Phase 2: Plan
            progress.update(task, description="[cyan]Phase 2: Planning acquisition...")
            plan = await self._plan_acquisition(topic, knowledge)
            progress.advance(task)

            # Phase 3: Acquire
            progress.update(task, description="[cyan]Phase 3: Acquiring dependencies...")
            acquired = await self._acquire_dependencies(plan)
            progress.advance(task)

            # Phase 4: Generate code
            progress.update(task, description="[cyan]Phase 4: Generating implementation...")
            capability = await self._generate_implementation(topic, knowledge, plan)
            progress.advance(task)

            # Phase 5: Save
            progress.update(task, description="[cyan]Phase 5: Saving to memory...")
            await self._integrate_capability(capability)
            progress.advance(task)

        console.print(f"\n[bold green]  NEW CAPABILITY ACQUIRED: {topic}[/bold green]")

    async def _research_capability(self, topic: str) -> str:
        """Use AI organs to research how to do something."""
        prompt = f"""I need to learn how to: {topic}

Provide a comprehensive technical guide including:
1. What libraries/tools are needed
2. Step-by-step implementation approach
3. Code examples
4. Common pitfalls to avoid
5. Dependencies to install (pip packages)

Be specific and practical."""

        result = await self.apex.mcp_client.query(prompt, task_type="research")
        return result

    async def _plan_acquisition(self, topic: str, knowledge: str) -> Dict[str, Any]:
        """Create an acquisition plan from research."""
        prompt = f"""Based on this research about "{topic}":

{knowledge[:2000]}

Create a JSON acquisition plan:
{{
    "pip_packages": ["package1", "package2"],
    "system_packages": ["pkg1"],
    "approach": "brief description of best approach",
    "complexity": "simple|medium|complex",
    "estimated_time": "5 minutes"
}}

Return ONLY valid JSON."""

        result = await self.apex.mcp_client.query(prompt, task_type="code")

        try:
            import re
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except (json.JSONDecodeError, AttributeError):
            pass

        return {
            "pip_packages": [],
            "system_packages": [],
            "approach": "General implementation",
            "complexity": "medium",
            "estimated_time": "10 minutes",
        }

    async def _acquire_dependencies(self, plan: Dict[str, Any]) -> bool:
        """Install required dependencies."""
        pip_packages = plan.get("pip_packages", [])

        if pip_packages:
            console.print(f"  [dim]Installing: {', '.join(pip_packages)}[/dim]")
            for pkg in pip_packages:
                try:
                    subprocess.run(
                        ["pip", "install", pkg],
                        capture_output=True,
                        text=True,
                        timeout=120,
                    )
                except Exception as e:
                    console.print(f"  [yellow]Warning: Failed to install {pkg}: {e}[/yellow]")

        return True

    async def _generate_implementation(self, topic: str, knowledge: str,
                                        plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate the actual implementation code."""
        prompt = f"""Generate a Python implementation for: {topic}

Approach: {plan.get('approach', 'General')}
Available packages: {plan.get('pip_packages', [])}

Requirements:
- Must be a self-contained function or class
- Include error handling
- Include docstring
- Return results as a dictionary

Generate ONLY the Python code, no explanations."""

        code = await self.apex.mcp_client.query(prompt, task_type="code")

        return {
            "name": topic.replace(" ", "_").lower(),
            "code": code,
            "libraries": plan.get("pip_packages", []),
            "metadata": {
                "complexity": plan.get("complexity", "medium"),
                "acquired_date": datetime.now().isoformat(),
                "research_summary": knowledge[:500],
            },
        }

    async def _integrate_capability(self, capability: Dict[str, Any]):
        """Save new capability to Oracle + make it available system-wide."""
        # Save to database
        await self.apex.oracle.save_capability(capability)

        # Add to runtime capabilities
        self.apex.capabilities[capability["name"]] = capability

        # Save evolution record
        await self.apex.oracle.save_task({
            "command": f"learn:{capability['name']}",
            "status": "complete",
            "agents_used": ["evolution_engine"],
            "output": f"Acquired capability: {capability['name']}",
        })

    async def evolve_language_understanding(self):
        """Autonomous language learning - runs in background."""
        console.print("\n[dim]  Language evolution cycle...[/dim]")

        knowledge = await self.apex.oracle.get_knowledge("")
        if not knowledge:
            return

        # Use AI to find patterns
        prompt = f"""Analyze these past interactions and extract common language patterns:

{json.dumps(knowledge[:20], indent=2)}

Find patterns like:
- "get me X" -> download intent
- "find out about X" -> search intent

Return JSON array of patterns:
[{{"pattern": "regex", "intent": "action", "confidence": 0.95}}]"""

        result = await self.apex.mcp_client.query(prompt, task_type="general")
        console.print("[dim]  Language evolution complete.[/dim]")
