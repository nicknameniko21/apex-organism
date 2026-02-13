# Copyright (c) 2026 AI Center Plus.
# Licensed under the MIT License. See LICENSE file for details.

"""
MCP Client - Multi-AI Connection Layer
Connects to multiple AI services via their APIs.
Supports: Perplexity, DeepSeek, Gemini, MiniMax, Kimi, and any OpenAI-compatible API.
"""

import httpx
import json
import asyncio
from typing import Dict, Any, Optional, List
from rich.console import Console

console = Console()


class AIOrgan:
    """Represents a single AI service connection."""

    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.enabled = config.get("enabled", False)
        self.api_key = config.get("api_key", "")
        self.base_url = config.get("base_url", "")
        self.model = config.get("model", "")
        self.role = config.get("role", "General")
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=120.0,
            )
        return self._client

    async def query(self, prompt: str, system_prompt: str = "") -> str:
        """Send a query to this AI organ using OpenAI-compatible chat API."""
        if not self.enabled:
            return f"[{self.name}] Organ is disabled."

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            # Most AI services support OpenAI-compatible /chat/completions
            endpoint = "/chat/completions"

            # Special handling for Gemini
            if "googleapis" in self.base_url:
                return await self._query_gemini(prompt, system_prompt)

            response = await self.client.post(
                endpoint,
                json={
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": 4096,
                    "temperature": 0.7,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

        except Exception as e:
            return f"[{self.name}] Error: {str(e)}"

    async def _query_gemini(self, prompt: str, system_prompt: str = "") -> str:
        """Query Google Gemini API."""
        try:
            url = f"{self.base_url}/v1beta/models/{self.model}:generateContent?key={self.api_key}"
            parts = []
            if system_prompt:
                parts.append({"text": system_prompt + "\n\n"})
            parts.append({"text": prompt})

            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    url,
                    json={"contents": [{"parts": parts}]},
                )
                response.raise_for_status()
                data = response.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            return f"[gemini] Error: {str(e)}"

    async def close(self):
        if self._client:
            await self._client.aclose()


class MCPClient:
    """
    Multi-AI Connection Layer.
    Manages connections to all AI organs and routes queries intelligently.
    """

    def __init__(self, ai_services_config: Dict[str, Any]):
        self.organs: Dict[str, AIOrgan] = {}

        for name, config in ai_services_config.items():
            if isinstance(config, dict):
                self.organs[name] = AIOrgan(name, config)

    def check_connections(self) -> int:
        """Check how many AI organs are active."""
        active = sum(1 for organ in self.organs.values() if organ.enabled)
        for name, organ in self.organs.items():
            status = "ACTIVE" if organ.enabled else "DISABLED"
            console.print(f"    {name.capitalize()}: {status} ({organ.role})")
        return active

    def count_active_organs(self) -> int:
        """Count active organs."""
        return sum(1 for organ in self.organs.values() if organ.enabled)

    def get_best_organ(self, task_type: str = "general") -> Optional[AIOrgan]:
        """Get the best available organ for a task type."""
        role_map = {
            "research": ["perplexity", "kimi", "deepseek"],
            "code": ["deepseek", "openai_compatible", "kimi"],
            "vision": ["gemini", "openai_compatible"],
            "creative": ["minimax", "gemini"],
            "memory": ["kimi", "deepseek"],
            "general": ["deepseek", "perplexity", "openai_compatible", "gemini", "kimi", "minimax"],
        }

        preferred = role_map.get(task_type, role_map["general"])
        for name in preferred:
            organ = self.organs.get(name)
            if organ and organ.enabled:
                return organ

        # Fallback: any active organ
        for organ in self.organs.values():
            if organ.enabled:
                return organ

        return None

    async def query(self, prompt: str, task_type: str = "general",
                    system_prompt: str = "") -> str:
        """Route a query to the best available AI organ."""
        organ = self.get_best_organ(task_type)
        if not organ:
            return "No AI organs are active. Please enable at least one AI service in config.yaml."

        console.print(f"  [dim]Using {organ.name.capitalize()} ({organ.role})...[/dim]")
        return await organ.query(prompt, system_prompt)

    async def research(self, query: str) -> str:
        """Research a topic using the best research organ."""
        system_prompt = (
            "You are APEX's Research Department. Provide comprehensive, "
            "well-sourced research on the given topic. Include key facts, "
            "recent developments, and actionable insights."
        )
        return await self.query(query, task_type="research", system_prompt=system_prompt)

    async def analyze(self, target: str) -> str:
        """Analyze something using the best analysis organ."""
        system_prompt = (
            "You are APEX's Analysis Engine. Provide detailed, structured "
            "analysis of the given target. Include observations, patterns, "
            "and recommendations."
        )
        return await self.query(f"Analyze: {target}", task_type="general",
                                system_prompt=system_prompt)

    async def create(self, description: str) -> str:
        """Create something using the best creative organ."""
        system_prompt = (
            "You are APEX's Creation Studio. Generate high-quality output "
            "based on the description. Be thorough and creative."
        )
        return await self.query(f"Create: {description}", task_type="creative",
                                system_prompt=system_prompt)

    async def generate_code(self, description: str) -> str:
        """Generate code using the best coding organ."""
        system_prompt = (
            "You are APEX's Engineering Lab. Generate clean, well-documented, "
            "production-ready code. Include error handling and comments."
        )
        return await self.query(description, task_type="code",
                                system_prompt=system_prompt)

    async def interpret_command(self, user_input: str) -> Dict[str, Any]:
        """Use AI to interpret an ambiguous command."""
        prompt = f"""Interpret this user command and return a JSON response:

User said: "{user_input}"

Return JSON:
{{
    "action": "brief description of what to do",
    "intent": "search|create|analyze|learn|download|manage",
    "params": {{"key": "value"}},
    "confidence": 0.95
}}

Return ONLY valid JSON, no other text."""

        result = await self.query(prompt, task_type="general")

        try:
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except (json.JSONDecodeError, AttributeError):
            pass

        return {
            "action": user_input,
            "intent": "general",
            "params": {},
            "confidence": 0.5,
        }

    async def parallel_query(self, prompt: str, organ_names: List[str] = None) -> Dict[str, str]:
        """Query multiple organs in parallel and collect all responses."""
        if organ_names is None:
            organ_names = [n for n, o in self.organs.items() if o.enabled]

        tasks = {}
        for name in organ_names:
            organ = self.organs.get(name)
            if organ and organ.enabled:
                tasks[name] = organ.query(prompt)

        if not tasks:
            return {"error": "No active organs to query."}

        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        return dict(zip(tasks.keys(), [
            str(r) if isinstance(r, Exception) else r for r in results
        ]))

    async def close(self):
        """Close all organ connections."""
        for organ in self.organs.values():
            await organ.close()
