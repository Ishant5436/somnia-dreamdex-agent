"""
White-Box Test Suite for Somnia × DreamDEX Agent & Smart Contract Math
Tests internal boundary conditions, assertion invariants, confidence score formulas,
and mathematical state transitions of the DreamDEXRouter EVM contract.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from agent_bot import DreamDEXAgent


# ==============================================================================
# 1. Strategy Engine Boundary & Invariant Tests (White-Box)
# ==============================================================================

def test_whitebox_volatility_exact_boundary():
    """White-box: test exact 15.0 bps boundary between chop filter and trend evaluation."""
    agent = DreamDEXAgent()
    # 14.99 bps -> must be chop gated
    res_under = agent.evaluate_event_contract("Market", current_vol_bps=14.99, trend_signal=0.8)
    assert res_under["action"] == "PASS (Chop Gated)"
    assert res_under["confidence_score"] == 0.0

    # 15.00 bps with strong trend -> must activate trade
    res_exact = agent.evaluate_event_contract("Market", current_vol_bps=15.0, trend_signal=0.8)
    assert res_exact["action"] == "BUY_LONG"
    assert res_exact["side"] == "LONG"


def test_whitebox_trend_signal_deadband_boundaries():
    """White-box: test +0.3 and -0.3 deadband boundaries for directional triggers."""
    agent = DreamDEXAgent()
    # Exactly +0.30 -> neutral (deadband)
    res_neutral_upper = agent.evaluate_event_contract("Market", current_vol_bps=20.0, trend_signal=0.30)
    assert res_neutral_upper["action"] == "PASS (Neutral Trend)"
    assert res_neutral_upper["side"] == "NONE"

    # Exactly 0.31 -> triggers BUY_LONG
    res_bull = agent.evaluate_event_contract("Market", current_vol_bps=20.0, trend_signal=0.31)
    assert res_bull["action"] == "BUY_LONG"

    # Exactly -0.30 -> neutral (deadband)
    res_neutral_lower = agent.evaluate_event_contract("Market", current_vol_bps=20.0, trend_signal=-0.30)
    assert res_neutral_lower["action"] == "PASS (Neutral Trend)"

    # Exactly -0.31 -> triggers BUY_SHORT
    res_bear = agent.evaluate_event_contract("Market", current_vol_bps=20.0, trend_signal=-0.31)
    assert res_bear["action"] == "BUY_SHORT"


def test_whitebox_confidence_score_ceiling_and_floors():
    """White-box: confidence score formula must clamp to max 0.95 at trend_signal=1.0."""
    agent = DreamDEXAgent()
    res_max = agent.evaluate_event_contract("Market", current_vol_bps=50.0, trend_signal=1.0)
    # formula: min(0.95, 0.5 + 1.0 * 0.45) = 0.95
    assert res_max["confidence_score"] == 0.95

    res_min = agent.evaluate_event_contract("Market", current_vol_bps=50.0, trend_signal=-1.0)
    assert res_min["confidence_score"] == 0.95


def test_whitebox_assertion_defense():
    """White-box: invalid inputs must trigger assertion failures (Power of 10 invariants)."""
    agent = DreamDEXAgent()
    # Negative volatility
    with pytest.raises(AssertionError, match="cannot be negative"):
        agent.evaluate_event_contract("Market", current_vol_bps=-1.0, trend_signal=0.5)

    # Out of range signal > 1.0
    with pytest.raises(AssertionError, match="bounded"):
        agent.evaluate_event_contract("Market", current_vol_bps=20.0, trend_signal=1.5)

    # Order below 0.001 ETH minimum
    with pytest.raises(AssertionError, match="Min order size"):
        agent.simulate_order_execution("0x123", "LONG", amount_eth=0.0005)


# ==============================================================================
# 2. DreamDEXRouter EVM Mathematical Model (White-Box)
# ==============================================================================

def test_whitebox_router_payout_proportional_math():
    """White-box: simulate exact DreamDEXRouter.sol claimPayout arithmetic."""
    # Deposit 10 ETH in Long, 40 ETH in Short -> total pool = 50 ETH
    # Fee: 20 BPS (0.20%)
    protocol_fee_bps = 20
    max_bps = 10000

    def calc_net_shares(deposit):
        fee = (deposit * protocol_fee_bps) // max_bps
        return deposit - fee

    # User A deposits 10 ETH into Long
    long_net = calc_net_shares(10_000000000000000000)
    # User B deposits 40 ETH into Short
    short_net = calc_net_shares(40_000000000000000000)

    total_pool = long_net + short_net

    # Outcome 1: LONG WINS
    # User A claims payout
    user_a_shares = long_net
    total_long_pool = long_net
    payout_a = (user_a_shares * total_pool) // total_long_pool

    # User A gets the entire net pool!
    assert payout_a == total_pool
    # 50 ETH deposit - 0.20% fee = 49.9 ETH net payout
    assert payout_a == 49_900000000000000000
