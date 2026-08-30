import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from agent_bot import DreamDEXAgent

def test_agent_initialization():
    agent = DreamDEXAgent()
    assert agent.trade_count == 0
    assert agent.settlement_count == 0

def test_volatility_chop_gating():
    agent = DreamDEXAgent()
    # Volatility under 15 bps should trigger PASS / Chop Gated
    decision = agent.evaluate_event_contract("BTC Volatility Test", current_vol_bps=12.0, trend_signal=0.8)
    assert decision["action"] == "PASS (Chop Gated)"
    assert decision["side"] == "NONE"

def test_momentum_expansion_bull_signal():
    agent = DreamDEXAgent()
    decision = agent.evaluate_event_contract("ETH Breakout Test", current_vol_bps=28.0, trend_signal=0.7)
    assert decision["action"] == "BUY_LONG"
    assert decision["side"] == "LONG"
    assert decision["confidence_score"] > 0.7

def test_momentum_expansion_bear_signal():
    agent = DreamDEXAgent()
    decision = agent.evaluate_event_contract("SOL Breakdown Test", current_vol_bps=35.0, trend_signal=-0.6)
    assert decision["action"] == "BUY_SHORT"
    assert decision["side"] == "SHORT"
    assert decision["confidence_score"] > 0.7

def test_simulated_execution():
    agent = DreamDEXAgent()
    res = agent.simulate_order_execution("0xabc123", "LONG", 0.05)
    assert res["status"] == "CONFIRMED"
    assert res["amount_eth"] == 0.05
    assert res["tx_hash"].startswith("0x")
    assert agent.trade_count == 1

if __name__ == "__main__":
    pytest.main(["-v", __file__])
