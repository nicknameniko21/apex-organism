# Copyright (c) 2026 AI Center Plus. All Rights Reserved.
# This software is proprietary and confidential. See LICENSE file.
# Unauthorized copying, distribution, or modification is strictly prohibited.

"""
Natural Language Command Processor
Converts human speech into APEX actions.
"""

import re
from typing import Dict, Any, Optional, Tuple
from rich.console import Console

console = Console()


class NaturalLanguageProcessor:
    """
    Interprets natural language commands and routes them to APEX capabilities.
    """

    def __init__(self, apex_organism):
        self.apex = apex_organism

        # Intent patterns (regex-based, will evolve to use AI)
        self.intent_patterns = {
            "learn": [
                r"learn (how to |about )?(.+)",
                r"teach yourself (.+)",
                r"acquire (.+) capability",
                r"study (.+)",
            ],
            "search": [
                r"(search|find|look for|google|research) (.+)",
                r"what is (.+)",
                r"who is (.+)",
                r"tell me about (.+)",
            ],
            "analyze": [
                r"analyze (.+)",
                r"process (.+)",
                r"examine (.+)",
                r"check (.+)",
            ],
            "create": [
                r"(create|make|build|generate|write|develop) (.+)",
            ],
            "swarm": [
                r"use (\d+) agents? (?:to|for) (.+)",
                r"parallelize (.+)",
                r"deploy swarm (.+)",
            ],
            "status": [
                r"^(status|health|how are you)$",
                r"^what can you do$",
                r"^list capabilities$",
                r"^show me what you know$",
            ],
            "help": [
                r"^help$",
                r"^examples$",
                r"^what can I say$",
            ],
            "parallel": [
                r"ask all (?:ais?|organs?) (.+)",
                r"compare (.+)",
            ],
        }

    async def process_command(self, user_input: str):
        """Main NL processing entry point."""
        intent, params = self._detect_intent(user_input)

        if not intent:
            # Fallback: Let AI interpret
            await self._ai_interpret(user_input)
            return

        handlers = {
            "learn": self._handle_learn,
            "search": self._handle_search,
            "analyze": self._handle_analyze,
            "create": self._handle_create,
            "swarm": self._handle_swarm,
            "status": self._handle_status,
            "help": self._handle_help,
            "parallel": self._handle_parallel,
        }

        handler = handlers.get(intent)
        if handler:
            await handler(params, user_input)
        else:
            await self._ai_interpret(user_input)

    def _detect_intent(self, text: str) -> Tuple[Optional[str], Optional[tuple]]:
        """Pattern-based intent detection."""
        text_lower = text.lower().strip()

        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text_lower, re.IGNORECASE)
                if match:
                    return intent, match.groups()

        return None, None

    async def _handle_learn(self, params: tuple, raw_input: str):
        """Handle learning requests."""
        topic = params[-1] if params else raw_input
        console.print(f"[bold cyan]APEX:[/bold cyan] I'll learn about '{topic}'...")
        await self.apex.learn(topic)

    async def _handle_search(self, params: tuple, raw_input: str):
        """Handle search/research requests."""
        query = params[-1] if params else raw_input
        console.print(f"[bold cyan]APEX:[/bold cyan] Researching '{query}'...")
        await self.apex.search(query)

    async def _handle_analyze(self, params: tuple, raw_input: str):
        """Handle analysis requests."""
        target = params[0] if params else raw_input
        console.print(f"[bold cyan]APEX:[/bold cyan] Analyzing '{target}'...")
        await self.apex.analyze(target)

    async def _handle_create(self, params: tuple, raw_input: str):
        """Handle creation requests."""
        thing = params[-1] if params else raw_input
        console.print(f"[bold cyan]APEX:[/bold cyan] Creating '{thing}'...")
        await self.apex.create(thing)

    async def _handle_swarm(self, params: tuple, raw_input: str):
        """Handle swarm deployment requests."""
        try:
            num_agents = int(params[0])
        except (ValueError, IndexError):
            num_agents = 5
        task = params[-1] if len(params) > 1 else raw_input
        console.print(
            f"[bold cyan]APEX:[/bold cyan] Deploying {num_agents}-agent swarm for '{task}'..."
        )
        await self.apex.deploy_swarm(num_agents, task)

    async def _handle_parallel(self, params: tuple, raw_input: str):
        """Handle parallel query to all AIs."""
        query = params[0] if params else raw_input
        console.print(f"[bold cyan]APEX:[/bold cyan] Asking all AI organs: '{query}'...")
        results = await self.apex.mcp_client.parallel_query(query)
        for name, result in results.items():
            console.print(f"\n[bold magenta]{name.upper()}:[/bold magenta]")
            console.print(result[:500])

    async def _handle_status(self, params: tuple, raw_input: str):
        """Show APEX status and capabilities."""
        self.apex._display_status_table()

    async def _handle_help(self, params: tuple, raw_input: str):
        """Show help and examples."""
        console.print("""
[bold green]APEX NATURAL LANGUAGE EXAMPLES[/bold green]

[bold]LEARNING:[/bold]
  "Learn how to process videos"
  "Teach yourself network security"

[bold]SEARCHING:[/bold]
  "Search for recent AI breakthroughs"
  "What is quantum computing?"
  "Research Mars colonization"

[bold]ANALYZING:[/bold]
  "Analyze this data"
  "Examine my server performance"

[bold]CREATING:[/bold]
  "Create a firewall for my server"
  "Build a web scraper"
  "Write a Python script to sort files"

[bold]SWARM OPERATIONS:[/bold]
  "Use 10 agents to research AI companies"
  "Deploy swarm to analyze market data"

[bold]PARALLEL QUERIES:[/bold]
  "Ask all AIs about climate change"
  "Compare opinions on cryptocurrency"

[bold]STATUS & HELP:[/bold]
  "status" / "help" / "exit"

[dim]Just speak naturally - APEX will figure it out![/dim]
        """)

    async def _ai_interpret(self, user_input: str):
        """Fallback: Use AI to interpret complex/ambiguous commands."""
        console.print("[dim]  Interpreting your request with AI...[/dim]")

        interpretation = await self.apex.mcp_client.interpret_command(user_input)

        intent = interpretation.get("intent", "general")
        action = interpretation.get("action", user_input)
        confidence = interpretation.get("confidence", 0.5)

        console.print(
            f"[dim]  Understood ({confidence:.0%} confidence): {action}[/dim]"
        )

        # Route based on interpreted intent
        intent_to_handler = {
            "search": self._handle_search,
            "create": self._handle_create,
            "analyze": self._handle_analyze,
            "learn": self._handle_learn,
        }

        handler = intent_to_handler.get(intent)
        if handler:
            await handler((action,), user_input)
        else:
            # Generic execution
            result = await self.apex.mcp_client.query(user_input)
            console.print(f"\n{result}\n")
