"""
Black-Box Test Suite for Somnia × DreamDEX Agent
Tests CLI walkthrough execution, end-to-end simulation lifecycle,
and external response format verification.
"""

import subprocess
import os
import sys
import pytest

SOMNIA_ROOT = "/Users/ishantpanchal/somnia-dreamdex-agent"
DEMO_SCRIPT = os.path.join(SOMNIA_ROOT, "scripts/record_demo_walkthrough.py")


def test_blackbox_demo_walkthrough_execution():
    """Black-box: run demo walkthrough script and verify all 4 lifecycle phases complete."""
    res = subprocess.run([sys.executable, DEMO_SCRIPT], cwd=SOMNIA_ROOT, capture_output=True, text=True)
    assert res.returncode == 0
    stdout = res.stdout

    # Verify Header
    assert "SOMNIA × DREAMDEX AUTONOMOUS EVENT CONTRACT TRADING AGENT" in stdout

    # Verify Phase 1: RPC initialization
    assert "1. INITIALIZING SOMNIA L1 RPC & CONTRACT ROUTER" in stdout
    assert "Chain ID: 50312" in stdout

    # Verify Phase 2: Tick streaming & chop gating
    assert "2. STREAMING TICK DATA & EVALUATING VOLATILITY GATING" in stdout
    assert "CHOP GATED" in stdout
    assert "VOLATILITY BREAKOUT" in stdout

    # Verify Phase 3: Autonomous order execution
    assert "3. EXECUTING AUTONOMOUS EVENT CONTRACT ORDER" in stdout
    assert "Transaction Confirmed on Somnia L1!" in stdout
    assert "Gas Used:" in stdout

    # Verify Phase 4: Settlement & payout
    assert "4. ORACLE RESOLUTION & ATOMIC PAYOUT CLAIM" in stdout
    assert "OUTCOME_YES CONFIRMED" in stdout
    assert "100% SUCCESSFUL" in stdout
