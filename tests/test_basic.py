# Copyright (c) 2026 AI Center Plus.
# Licensed under the MIT License. See LICENSE file for details.

"""
APEX Organism v0.1 - Basic Tests
Run: python -m pytest tests/ -v
"""

import asyncio
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.oracle_sync import OracleSync
from core.money_gate import MoneyGate
from core.apex_core import ApexOrganism


@pytest.fixture
def config():
    return {
        "oracle": {"enabled": False},
        "ai_services": {
            "deepseek": {"enabled": False, "api_key": "", "base_url": "", "model": "", "role": "Test"},
        },
        "apex": {
            "version": "0.1.0",
            "money_gate": {"enabled": True, "max_auto_cost_usd": 1.00},
            "swarm": {"max_agents": 20},
        },
        "dashboard": {"host": "0.0.0.0", "port": 8080},
    }


def test_oracle_sync_init():
    """Test OracleSync initializes correctly."""
    oracle = OracleSync({"enabled": False})
    assert oracle._use_oracle is False
    assert oracle._connected is False


def test_oracle_sqlite_fallback():
    """Test SQLite fallback works."""
    oracle = OracleSync({"enabled": False})
    result = asyncio.run(oracle.test_connection())
    assert result is True
    assert oracle.is_connected() is True


def test_money_gate_auto_approve():
    """Test MoneyGate auto-approves small costs."""
    gate = MoneyGate({"enabled": True, "max_auto_cost_usd": 1.00})
    assert gate.request_approval("test", 0.50) is True
    assert gate.total_spent == 0.50


def test_money_gate_disabled():
    """Test MoneyGate passes everything when disabled."""
    gate = MoneyGate({"enabled": False})
    assert gate.request_approval("test", 100.00) is True


def test_apex_organism_init(config):
    """Test ApexOrganism initializes correctly."""
    apex = ApexOrganism(config)
    assert apex.config == config
    assert apex._running is True
    assert apex.capabilities == {}


def test_apex_status(config):
    """Test status report."""
    apex = ApexOrganism(config)
    status = apex.get_status()
    assert "health" in status
    assert "intelligence" in status
    assert "version" in status
    assert status["version"] == "0.1.0"


def test_intelligence_calculation(config):
    """Test intelligence grows with capabilities."""
    apex = ApexOrganism(config)
    base_intelligence = apex.calculate_intelligence()

    # Add fake capabilities
    for i in range(20):
        apex.capabilities[f"skill_{i}"] = {"name": f"skill_{i}"}

    new_intelligence = apex.calculate_intelligence()
    assert new_intelligence > base_intelligence


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
