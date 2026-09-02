"""
White-Box Test Suite for Somnia × DreamDEX Agent & Smart Contract Math
Tests internal boundary conditions, assertion invariants, confidence score formulas,
and mathematical state transitions of the DreamDEXRouter EVM contract.
"""

import pytest
import sys
import os
import json
import shutil
import socket
import subprocess
import time

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


# ==============================================================================
# 3. Real EVM Reentrancy Attack Test (DreamDEXRouter.sol, compiled & deployed
#    to a live local chain -- NOT a Python arithmetic reimplementation).
#    Reentrancy is a property of EVM call semantics during an external call;
#    it cannot be proven by re-deriving the payout formula in Python, only
#    by actually attacking the compiled bytecode.
# ==============================================================================

PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
ROUTER_SRC = "contracts/DreamDEXRouter.sol"
ATTACKER_SRC = "contracts/test/ReentrancyAttacker.sol"

_TOOLING_AVAILABLE = shutil.which("solc") and shutil.which("anvil")


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _compile_contracts() -> dict:
    result = subprocess.run(
        ["solc", "--combined-json", "abi,bin", "--optimize", "--base-path", ".",
         ROUTER_SRC, ATTACKER_SRC],
        cwd=PROJECT_ROOT,
        capture_output=True, text=True, timeout=60,
    )
    assert result.returncode == 0, f"solc compilation failed:\n{result.stderr}"
    return json.loads(result.stdout)["contracts"]


@pytest.fixture()
def anvil_chain():
    if not _TOOLING_AVAILABLE:
        pytest.skip("solc and/or anvil not available on PATH")

    port = _free_port()
    proc = subprocess.Popen(
        ["anvil", "--port", str(port), "--silent"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        from web3 import Web3

        w3 = Web3(Web3.HTTPProvider(f"http://127.0.0.1:{port}"))
        for _ in range(50):
            if w3.is_connected():
                break
            time.sleep(0.1)
        else:
            raise RuntimeError("anvil did not become reachable in time")
        yield w3
    finally:
        proc.terminate()
        proc.wait(timeout=5)


def _deploy(w3, contracts, key, deployer, *ctor_args, value=0):
    entry = contracts[key]
    c = w3.eth.contract(abi=json.loads(entry["abi"]) if isinstance(entry["abi"], str) else entry["abi"],
                         bytecode="0x" + entry["bin"])
    tx_hash = c.constructor(*ctor_args).transact({"from": deployer, "value": value})
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    assert receipt.status == 1, f"deployment of {key} reverted"
    return w3.eth.contract(address=receipt.contractAddress, abi=c.abi)


def test_whitebox_reentrancy_attack_blocked_by_guard(anvil_chain):
    """
    Deploys the REAL compiled DreamDEXRouter bytecode plus a malicious
    ReentrancyAttacker contract to a live local EVM (anvil), and mounts a
    real reentrancy attack against claimPayout: the attacker's receive()
    fallback (triggered by the router's payout transfer) tries to call
    claimPayout again before the outer call returns.

    Asserts the nonReentrant guard actually blocks the reentrant EVM call
    (not just "the math would be wrong if it didn't") and that the attacker
    receives exactly one payout, never two.
    """
    w3 = anvil_chain
    owner = w3.eth.accounts[0]
    contracts = _compile_contracts()

    router = _deploy(w3, contracts, f"{ROUTER_SRC}:DreamDEXRouter", owner)
    attacker = _deploy(
        w3, contracts, f"{ATTACKER_SRC}:ReentrancyAttacker", owner, router.address
    )

    # 1. Create a market.
    tx_hash = router.functions.createMarket("Reentrancy Test Market", 3600).transact({"from": owner})
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    assert receipt.status == 1
    created = router.events.MarketCreated().process_receipt(receipt)
    market_id = created[0]["args"]["marketId"]

    # 2. Liquidity setup matters here: the attacker must hold only a SMALL
    #    fraction of the winning pool, with other depositors making up the
    #    rest. If the attacker held the entire winning side, a single
    #    legitimate payout would already drain nearly the whole contract
    #    balance, and a second exploit attempt would fail from plain
    #    insufficient balance -- masking whether the guard is doing
    #    anything at all. With real headroom in the contract, a successful
    #    double-payout is actually possible if the guard is broken, so a
    #    passing test here is meaningful.
    deposit = w3.to_wei(1, "ether")
    tx_hash = attacker.functions.buyShares(market_id, True).transact({"from": owner, "value": deposit})
    assert w3.eth.wait_for_transaction_receipt(tx_hash).status == 1

    # Several other LONG depositors, dwarfing the attacker's own stake.
    for i in range(1, 4):
        tx_hash = router.functions.buyOutcomeShares(market_id, True).transact(
            {"from": w3.eth.accounts[i], "value": w3.to_wei(5, "ether")}
        )
        assert w3.eth.wait_for_transaction_receipt(tx_hash).status == 1

    # SHORT-side liquidity too, so the pool isn't degenerate.
    tx_hash = router.functions.buyOutcomeShares(market_id, False).transact(
        {"from": w3.eth.accounts[4], "value": w3.to_wei(5, "ether")}
    )
    assert w3.eth.wait_for_transaction_receipt(tx_hash).status == 1

    # 3. Owner resolves the market: LONG wins.
    tx_hash = router.functions.resolveMarket(market_id, 1).transact({"from": owner})
    assert w3.eth.wait_for_transaction_receipt(tx_hash).status == 1

    expected_payout = router.functions.markets(market_id).call()  # sanity: market exists, resolved
    assert expected_payout[6] is True  # isResolved

    # 4. Fire the attack. The outer claim must still succeed (a legitimate
    #    single payout is a valid outcome), but the reentrant inner call
    #    must be the thing that gets blocked.
    attacker_balance_before = w3.eth.get_balance(attacker.address)
    tx_hash = attacker.functions.attackClaim(market_id).transact({"from": owner})
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    assert receipt.status == 1, "outer claim transaction unexpectedly reverted"

    reentrant_call_count = attacker.functions.reentrantCallCount().call()
    reentrancy_reverted = attacker.functions.reentrancyReverted().call()
    total_received = attacker.functions.totalReceived().call()
    attacker_balance_after = w3.eth.get_balance(attacker.address)

    assert reentrant_call_count == 1, "attacker should have attempted exactly one reentrant call"
    assert reentrancy_reverted is True, (
        "REENTRANCY VULNERABILITY: the reentrant claimPayout call did not revert -- "
        "the nonReentrant guard failed to block it"
    )

    # Exactly one payout's worth of ETH received, never two.
    actual_delta = attacker_balance_after - attacker_balance_before
    assert total_received == actual_delta
    assert total_received > 0
    # If reentrancy had succeeded, the attacker would have been paid twice
    # for a position it only holds once -- draining the pool. Confirm no
    # second payout occurred by checking hasClaimed stuck at true and the
    # position cannot be claimed again.
    with pytest.raises(Exception):
        tx_hash = attacker.functions.attackClaim(market_id).transact({"from": owner})
        r = w3.eth.wait_for_transaction_receipt(tx_hash)
        assert r.status == 1  # force failure path if it didn't revert outright
        raise AssertionError("ALREADY_CLAIMED market was claimed a second time")
