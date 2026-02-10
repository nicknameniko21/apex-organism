# Copyright (c) 2026 AI Center Plus. All Rights Reserved.
# This software is proprietary and confidential. See LICENSE file.
# Unauthorized copying, distribution, or modification is strictly prohibited.

"""
Swarm Orchestrator - Deploys 1-20 parallel agents
Massive parallelization for 10x-100x speedup.
"""

import asyncio
from typing import List, Dict, Any
from datetime import datetime
from rich.console import Console
from rich.progress import Progress

console = Console()


class SwarmOrchestrator:
    """
    Manages swarms of parallel agents for massive speedup.
    """

    def __init__(self, apex_organism):
        self.apex = apex_organism
        self.max_agents = apex_organism.config.get("apex", {}).get("swarm", {}).get("max_agents", 20)

    async def deploy_swarm(self, num_agents: int, task_description: str) -> List[Dict[str, Any]]:
        """
        Deploy a swarm of N agents to complete a task in parallel.

        Args:
            num_agents: Number of parallel agents (1-20)
            task_description: What the swarm should accomplish

        Returns:
            List of results from each agent
        """
        num_agents = min(num_agents, self.max_agents)

        console.print(f"\n[bold magenta]  DEPLOYING {num_agents}-AGENT SWARM[/bold magenta]")

        # Break task into subtasks
        subtasks = await self._decompose_task(task_description, num_agents)

        # Execute in parallel
        results = []
        with Progress() as progress:
            task = progress.add_task(
                f"[magenta]Swarm executing ({num_agents} agents)...",
                total=len(subtasks)
            )

            # Create async tasks
            async_tasks = [
                self._execute_agent(i, subtask)
                for i, subtask in enumerate(subtasks)
            ]

            # Run all agents in parallel
            for coro in asyncio.as_completed(async_tasks):
                result = await coro
                results.append(result)
                progress.advance(task)

        # Aggregate results
        aggregated = await self._aggregate_results(task_description, results)

        console.print(f"\n[bold green]  SWARM COMPLETE[/bold green]")
        console.print(f"  Agents deployed: {num_agents}")
        console.print(f"  Results collected: {len(results)}")
        console.print(f"\n[green]Aggregated Result:[/green]\n{aggregated}\n")

        # Save to Oracle
        await self.apex.oracle.save_task({
            "command": f"swarm:{task_description}",
            "status": "complete",
            "agents_used": [f"agent_{i}" for i in range(num_agents)],
            "output": aggregated,
        })

        return results

    async def _decompose_task(self, task_description: str, num_agents: int) -> List[str]:
        """Break a task into subtasks for parallel execution."""
        if num_agents == 1:
            return [task_description]

        prompt = f"""Break this task into exactly {num_agents} independent subtasks that can be executed in parallel:

Task: "{task_description}"

Return a JSON array of {num_agents} subtask strings:
["subtask 1 description", "subtask 2 description", ...]

Each subtask should be self-contained and contribute to the overall goal.
Return ONLY the JSON array."""

        result = await self.apex.mcp_client.query(prompt, task_type="general")

        try:
            import json, re
            json_match = re.search(r'\[.*\]', result, re.DOTALL)
            if json_match:
                subtasks = json.loads(json_match.group())
                if isinstance(subtasks, list) and len(subtasks) > 0:
                    return subtasks[:num_agents]
        except Exception:
            pass

        # Fallback: duplicate the task
        return [f"{task_description} (perspective {i+1})" for i in range(num_agents)]

    async def _execute_agent(self, agent_id: int, subtask: str) -> Dict[str, Any]:
        """Execute a single agent's subtask."""
        start_time = datetime.now()

        console.print(f"  [dim]Agent {agent_id}: Working on '{subtask[:60]}...'[/dim]")

        result = await self.apex.mcp_client.query(subtask, task_type="research")

        duration = (datetime.now() - start_time).total_seconds()

        return {
            "agent_id": agent_id,
            "subtask": subtask,
            "result": result,
            "duration_seconds": duration,
        }

    async def _aggregate_results(self, original_task: str,
                                  results: List[Dict[str, Any]]) -> str:
        """Aggregate results from all agents into a unified response."""
        if len(results) == 1:
            return results[0]["result"]

        # Combine all results
        combined = "\n\n".join([
            f"--- Agent {r['agent_id']} ({r['duration_seconds']:.1f}s) ---\n{r['result'][:1000]}"
            for r in results
        ])

        prompt = f"""Synthesize these {len(results)} research results into a single comprehensive answer.

Original task: "{original_task}"

Individual results:
{combined[:4000]}

Create a unified, well-organized synthesis that combines the best insights from all agents.
Remove duplicates and contradictions. Prioritize accuracy."""

        return await self.apex.mcp_client.query(prompt, task_type="general")
