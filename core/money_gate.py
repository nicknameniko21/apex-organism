# Copyright (c) 2026 AI Center Plus.
# Licensed under the MIT License. See LICENSE file for details.

"""
Money Gate - Cost Approval System
All paid operations require user approval above threshold.
"""

from typing import Dict, Any
from rich.console import Console
from rich.prompt import Confirm

console = Console()


class MoneyGate:
    """
    Controls spending. All paid API calls go through this gate.
    """

    def __init__(self, config: Dict[str, Any]):
        self.enabled = config.get("enabled", True)
        self.max_auto_cost = config.get("max_auto_cost_usd", 1.00)
        self.total_spent = 0.0
        self.spending_log = []

    def request_approval(self, service_name: str, estimated_cost: float,
                         description: str = "") -> bool:
        """
        Request approval for a paid operation.
        Auto-approves if cost is below threshold.
        """
        if not self.enabled:
            return True

        if estimated_cost <= self.max_auto_cost:
            self._log_spending(service_name, estimated_cost, "auto-approved")
            return True

        # Ask user for approval
        console.print(f"\n[bold yellow]  MONEY GATE[/bold yellow]")
        console.print(f"  Service: {service_name}")
        console.print(f"  Estimated cost: ${estimated_cost:.2f}")
        if description:
            console.print(f"  Purpose: {description}")
        console.print(f"  Total spent this session: ${self.total_spent:.2f}")

        approved = Confirm.ask("  Approve this cost?", default=False)

        if approved:
            self._log_spending(service_name, estimated_cost, "user-approved")
        else:
            self._log_spending(service_name, estimated_cost, "rejected")

        return approved

    def _log_spending(self, service: str, cost: float, status: str):
        """Log a spending event."""
        if status != "rejected":
            self.total_spent += cost

        self.spending_log.append({
            "service": service,
            "cost": cost,
            "status": status,
            "total": self.total_spent,
        })

    def get_spending_report(self) -> Dict[str, Any]:
        """Get spending summary."""
        return {
            "total_spent_usd": self.total_spent,
            "transactions": len(self.spending_log),
            "log": self.spending_log,
        }
