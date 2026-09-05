# Somnia × DreamDEX Autonomous Agent — DoraHacks Submission Package

**Hackathon:** Event Contracts Hackathon (Somnia Network & DreamDEX)  
**Prize Pool:** $5,000 USD  
**Track:** Prediction Markets & Automated Event Contracts  
**GitHub Repository:** [https://github.com/Ishant5436/somnia-dreamdex-agent](https://github.com/Ishant5436/somnia-dreamdex-agent)  
**Smart Contract:** [`contracts/DreamDEXRouter.sol`](https://github.com/Ishant5436/somnia-dreamdex-agent/blob/main/contracts/DreamDEXRouter.sol)  
**Verified On-Chain Contract:** [`0xc0219209598d4d3A86ff0CcCcC531d623b51F36D`](https://shannon-explorer.somnia.network/address/0xc0219209598d4d3A86ff0CcCcC531d623b51F36D)  
**Creation Tx Hash:** [`0x79df1813e2ce54afa4c014ac4c7e2cc358a89a0a789c5adb4b1700593182e657`](https://shannon-explorer.somnia.network/tx/0x79df1813e2ce54afa4c014ac4c7e2cc358a89a0a789c5adb4b1700593182e657)  
**Deployer Address:** `0x31305a21497df91A9D8a60a2FF62519973Ab8323` (Somnia Shannon Testnet — Chain ID 50312)  

---

## 1. Executive Summary

**Somnia-DreamDEX-Agent** is an ultra-high-throughput autonomous prediction market agent and EVM event settlement router engineered natively for the **Somnia Shannon Layer-1 Testnet**.

Built to solve the dual failure modes of high-frequency prediction markets — capital bleed in chop and abandoned market freezes — our protocol delivers three core innovations:
1. **Parkinson Realized Volatility Gating:** Locks agent execution during consolidation chop (<15 bps) to eliminate spread slippage, deploying capital into DreamDEX binary event contracts only upon regime expansion.
2. **Permissionless Liveness Fallback (`emergencyResolveExpiredMarket`):** A trustless on-chain escape hatch that allows ANY participant to cancel an abandoned market and claim a 100% net deposit refund if the market creator or oracle fails to resolve within a 3-day grace period.
3. **Empty-Pool Auto-Refund Protection:** Guarantees that if a market resolves to an outcome with zero opposing deposits, all participants receive an automatic 100% principal refund rather than suffering permanent fund lockups.

---

## 2. Key Architecture & Deliverables

1. **Non-Reentrant Event Router ([`contracts/DreamDEXRouter.sol`](https://github.com/Ishant5436/somnia-dreamdex-agent/blob/main/contracts/DreamDEXRouter.sol)):**
   * Single-slot mutex locks preventing cross-contract and same-contract reentrancy.
   * Atomic outcome minting (`YES` / `NO` shares), oracle settlement, and proportional payout distribution.
   * **Permissionless Liveness Guarantee:** If the market owner or oracle ever goes offline or fails to resolve an expired market, `emergencyResolveExpiredMarket` unlocks 100% net deposit refunds.
   * Adheres strictly to Deterministic Safety Invariants (Power of 10 Rules: bounded loops, checked arithmetic).

2. **Autonomous Volatility Agent ([`src/agent_bot.py`](https://github.com/Ishant5436/somnia-dreamdex-agent/blob/main/src/agent_bot.py)):**
   * Real-time tick ingestion and rolling realized volatility calculation via Parkinson estimator.
   * Volatility chop filter gating orders below threshold.
   * Directional confidence scoring for binary prediction markets.

3. **Interactive Demo Walkthrough ([`scripts/record_demo_walkthrough.py`](https://github.com/Ishant5436/somnia-dreamdex-agent/blob/main/scripts/record_demo_walkthrough.py)):**
   * Full end-to-end simulation from tick ingestion to onchain transaction confirmation and oracle payout disbursement.
   * Visual terminal walkthrough demo: [`assets/somnia_agent_demo.gif`](https://raw.githubusercontent.com/Ishant5436/somnia-dreamdex-agent/main/assets/somnia_agent_demo.gif)
   * High-definition video walkthrough: [`assets/somnia_agent_demo.mp4`](https://github.com/Ishant5436/somnia-dreamdex-agent/raw/main/assets/somnia_agent_demo.mp4)

---

## 3. Power of 10 Deterministic Safety Invariants Audit

The implementation strictly satisfies the Power of 10 Safety Invariants:

| Invariant | Standard Enforced | Implementation Evidence |
| :--- | :--- | :--- |
| **Rule 1: Simple Control Flow** | Zero recursion, zero goto | Straight-line execution in router; iterative deque processing in Python. |
| **Rule 2: Bounded Loops** | Fixed upper bounds on all loops | Sliding window deque bounded at $N \le 256$; bounded iterations across all price feeds. |
| **Rule 3: Deterministic Memory** | Bounded memory allocations | Pre-allocated monotonic extremum deques; zero dynamic memory growth on tick path. |
| **Rule 4: Function Length** | <= 60 lines per routine | Modular helper architecture; zero monolithic procedures in contract or agent. |
| **Rule 5: Assertion Density** | >= 2 assertions per function | Boundary preconditions and postconditions verified across all mathematical routines. |
| **Rule 6: Smallest Scope** | Encapsulated State | Contract state strictly private/internal with explicit accessors; zero bare module globals. |
| **Rule 7: Check Returns & Parameters** | Strict input validation | All external calls in router check success; market IDs and timestamps bounds-checked. |
| **Rule 8: Minimal Metaprogramming** | Zero dynamic code evaluation | Standard Solidity 0.8.20 and typed Python; zero `eval()`, `exec()`, or dynamic proxies. |
| **Rule 9: Restrict Pointer Indirection** | Single-level reference traversal | Direct storage slot lookups; no complex pointer trees or uncontrolled delegatecalls. |
| **Rule 10: Static Analysis & Tests** | 100% test pass rate, 0 warnings | 19/19 passing test suite (unit, whitebox, and blackbox tests) & clean static analysis. |

---

## 4. Judge Reproduction & Verification Guide

```bash
# 1. Clone & Enter Repository
git clone https://github.com/Ishant5436/somnia-dreamdex-agent.git
cd somnia-dreamdex-agent

# 2. Install Dependencies & Execute Automated Test Suite (19/19 Passing)
pip install -r requirements.txt
python3 -m pytest -v

# 3. Run Interactive Demo Execution Walkthrough
python3 scripts/record_demo_walkthrough.py
```

### Verified Test Telemetry:
```
============================= test session starts ==============================
collected 19 items

tests/test_agent.py::test_agent_initialization PASSED                    [  5%]
tests/test_agent.py::test_volatility_chop_gating PASSED                  [ 10%]
tests/test_agent.py::test_momentum_expansion_bull_signal PASSED          [ 15%]
tests/test_agent.py::test_momentum_expansion_bear_signal PASSED          [ 21%]
tests/test_agent.py::test_simulated_execution PASSED                     [ 26%]
tests/test_blackbox.py::test_blackbox_demo_walkthrough_execution PASSED  [ 31%]
tests/test_indicators.py::test_parkinson_volatility_zero_spread PASSED   [ 36%]
tests/test_indicators.py::test_parkinson_volatility_known_values PASSED  [ 42%]
tests/test_indicators.py::test_monotonic_deque_sliding_maximum PASSED    [ 47%]
tests/test_indicators.py::test_monotonic_deque_sliding_minimum PASSED    [ 52%]
tests/test_indicators.py::test_parkinson_volatility_floating_point_drift_resilience PASSED [ 57%]
tests/test_whitebox.py::test_whitebox_volatility_exact_boundary PASSED   [ 63%]
tests/test_whitebox.py::test_whitebox_trend_signal_deadband_boundaries PASSED [ 68%]
tests/test_whitebox.py::test_whitebox_confidence_score_ceiling_and_floors PASSED [ 73%]
tests/test_whitebox.py::test_whitebox_assertion_defense PASSED           [ 78%]
tests/test_whitebox.py::test_whitebox_router_payout_proportional_math PASSED [ 84%]
tests/test_whitebox.py::test_whitebox_reentrancy_attack_blocked_by_guard PASSED [ 89%]
tests/test_whitebox.py::test_whitebox_emergency_resolve_expired_market_liveness PASSED [ 94%]
tests/test_whitebox.py::test_whitebox_empty_pool_resolution_auto_refund PASSED [100%]

============================== 19 passed in 5.31s ==============================
```
