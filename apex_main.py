#!/usr/bin/env python3
# Copyright (c) 2026 AI Center Plus. All Rights Reserved.
# This software is proprietary and confidential. See LICENSE file.
# Unauthorized copying, distribution, or modification is strictly prohibited.

"""
APEX ORGANISM v0.1 - Main Entry Point
The living digital organism that orchestrates multiple AI services,
learns autonomously, and stores all knowledge in Oracle.

Usage:
    python apex_main.py              # Start with interactive CLI
    python apex_main.py --dashboard  # Start with web dashboard
    python apex_main.py --api        # Start API server only
"""

import asyncio
import sys
import os
import signal
import shutil
import yaml
import click
import webbrowser
import threading
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.apex_core import ApexOrganism
from core.natural_language import NaturalLanguageProcessor

console = Console()

BANNER = r"""
    ╔═══════════════════════════════════════════════════╗
    ║                                                   ║
    ║     █████╗ ██████╗ ███████╗██╗  ██╗              ║
    ║    ██╔══██╗██╔══██╗██╔════╝╚██╗██╔╝              ║
    ║    ███████║██████╔╝█████╗   ╚███╔╝               ║
    ║    ██╔══██║██╔═══╝ ██╔══╝   ██╔██╗               ║
    ║    ██║  ██║██║     ███████╗██╔╝ ██╗              ║
    ║    ╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝              ║
    ║                                                   ║
    ║         O R G A N I S M   v 0 . 1                ║
    ║                                                   ║
    ╚═══════════════════════════════════════════════════╝
"""


def load_config(config_path: str = "config.yaml", example_path: str = "config.yaml.example") -> dict:
    """Load configuration from YAML file, creating defaults when missing."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = config_path if os.path.isabs(config_path) else os.path.join(base_dir, config_path)
    example_file = example_path if os.path.isabs(example_path) else os.path.join(base_dir, example_path)

    default_config = {
        "oracle": {"enabled": False},
        "ai_services": {
            "perplexity": {"enabled": False, "api_key": "", "base_url": "https://api.perplexity.ai", "model": "sonar-pro", "role": "Research Department"},
            "deepseek": {"enabled": False, "api_key": "", "base_url": "https://api.deepseek.com", "model": "deepseek-chat", "role": "Engineering Lab"},
            "gemini": {"enabled": False, "api_key": "", "base_url": "https://generativelanguage.googleapis.com", "model": "gemini-2.0-flash", "role": "Vision System"},
            "minimax": {"enabled": False, "api_key": "", "base_url": "https://api.minimax.chat", "model": "abab6.5-chat", "role": "Creation Studio"},
            "kimi": {"enabled": False, "api_key": "", "base_url": "https://api.moonshot.cn/v1", "model": "moonshot-v1-128k", "role": "Memory Bank"},
            "openai_compatible": {"enabled": False, "api_key": "", "base_url": "https://api.openai.com/v1", "model": "gpt-4.1-mini", "role": "General Assistant"},
        },
        "apex": {
            "name": "APEX",
            "version": "0.1.0",
            "autonomous_mode": False,
            "money_gate": {"enabled": True, "max_auto_cost_usd": 1.00},
            "swarm": {"max_agents": 20},
            "evolution": {"auto_learn": True, "capability_storage": "plugins/"},
        },
        "dashboard": {"enabled": True, "host": "0.0.0.0", "port": 8080, "auto_open_browser": True},
    }

    if not os.path.exists(config_file):
        console.print(f"[yellow]Config file not found: {config_file}. Creating defaults...[/yellow]")
        if os.path.exists(example_file):
            shutil.copy(example_file, config_file)
            console.print("[green]Default config created from config.yaml.example[/green]")
        else:
            with open(config_file, "w") as f:
                yaml.safe_dump(default_config, f)
            console.print("[green]Default config created with safe defaults[/green]")

    with open(config_file, "r") as f:
        loaded = yaml.safe_load(f) or {}

    return loaded or default_config


async def run_cli(apex: ApexOrganism):
    """Run the interactive command-line interface."""
    nlp = NaturalLanguageProcessor(apex)

    console.print(BANNER, style="bold green")
    console.print(Panel(
        "[bold green]APEX ORGANISM is ALIVE[/bold green]\n"
        "Type your commands in natural language.\n"
        "Type [bold]'help'[/bold] for examples, [bold]'status'[/bold] for health check, "
        "[bold]'exit'[/bold] to shutdown.",
        title="Welcome",
        border_style="green"
    ))

    # Run startup diagnostics
    await apex.startup_sequence()

    while True:
        try:
            user_input = await asyncio.get_event_loop().run_in_executor(
                None, lambda: console.input("\n[bold green]APEX>[/bold green] ")
            )

            if not user_input or not user_input.strip():
                continue

            user_input = user_input.strip()

            # Exit commands
            if user_input.lower() in ("exit", "quit", "bye", "goodbye", "shutdown"):
                console.print("\n[bold green]APEX hibernating... All memory saved.[/bold green]")
                await apex.shutdown()
                break

            # Process natural language command
            await nlp.process_command(user_input)

        except (KeyboardInterrupt, EOFError):
            console.print("\n\n[bold yellow]Interrupted. Saving state...[/bold yellow]")
            await apex.shutdown()
            console.print("[bold green]Goodbye.[/bold green]")
            break
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")
            console.print("[green]APEX remains stable. Try rephrasing your request.[/green]")


def _auto_open_dashboard(apex: ApexOrganism):
    """Open dashboard URL in the default browser when enabled."""
    cfg = apex.config.get("dashboard", {})
    if not cfg.get("auto_open_browser"):
        return

    host = cfg.get("host", "0.0.0.0")
    port = cfg.get("port", 8080)
    host_for_url = "127.0.0.1" if host == "0.0.0.0" else host
    url = f"http://{host_for_url}:{port}"

    threading.Thread(target=webbrowser.open, args=(url,), daemon=True).start()


async def run_api(apex: ApexOrganism):
    """Run the FastAPI server for dashboard and API access."""
    from dashboard.api_server import create_app

    app = create_app(apex)
    _auto_open_dashboard(apex)

    import uvicorn
    config = uvicorn.Config(
        app,
        host=apex.config.get("dashboard", {}).get("host", "0.0.0.0"),
        port=apex.config.get("dashboard", {}).get("port", 8080),
        log_level="info",
    )
    server = uvicorn.Server(config)
    await server.serve()


@click.command()
@click.option("--dashboard", is_flag=True, help="Start with web dashboard")
@click.option("--api", is_flag=True, help="Start API server only")
@click.option("--config", default="config.yaml", help="Path to config file")
def main(dashboard: bool, api: bool, config: str):
    """APEX Organism v0.1 - Living Digital Intelligence"""
    cfg = load_config(config)

    if not cfg:
        console.print("[red]Failed to load configuration. Exiting.[/red]")
        sys.exit(1)

    apex = ApexOrganism(cfg)

    if dashboard or api:
        console.print(BANNER, style="bold green")
        console.print("[bold green]Starting APEX API Server...[/bold green]")
        asyncio.run(run_api(apex))
    else:
        asyncio.run(run_cli(apex))


if __name__ == "__main__":
    main()
