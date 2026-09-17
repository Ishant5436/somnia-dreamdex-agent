# Software Quality Risk Register (FMEA Matrix): Somnia DreamDEX Agent
## Conforming to ISO/DIS 9001:2026 Clause 6 (Risk-Based Thinking)

This document tracks identified quality hazards, algorithmic risks, and automated mitigations for `somnia-dreamdex-agent`.

---

## 1. Risk Evaluation Scale
- **Severity (S):** 1 (Negligible) to 5 (Catastrophic pool drain / capital wipeout)
- **Likelihood (L):** 1 (Extremely Rare) to 5 (Frequent without controls)
- **Risk Priority Number (RPN):** $S \times L$ (Scale 1 to 25). RPN $\ge 12$ mandates automated gating.

---

## 2. Failure Modes and Effects Analysis (FMEA)

| Risk ID | Potential Failure Mode | Impact / Effect | Severity (S) | Likelihood (L) | Initial RPN | Automated Mitigation & Quality Control | Residual RPN |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **RSK-SD-01** | Reentrancy attack on liquidity withdrawal or swap | Complete contract treasury depletion | 5 | 3 | **15** | OpenZeppelin `ReentrancyGuard` nonReentrant modifiers on all state-mutating functions; verified in `DreamDEXRouter.sol` | **2** (S=2, L=1) |
| **RSK-SD-02** | Trade execution during low-volatility chop regime | Severe taker fee drag and whipsaw losses | 4 | 4 | **16** | Parkinson volatility threshold filter gating order dispatch (`evaluate_market_opportunity`); verified in `test_volatility_chop_gating` | **2** (S=2, L=1) |
| **RSK-SD-03** | Floating point NaN or negative volatility propagation | Engine crash or nonsensical trade sizing | 4 | 3 | **12** | Explicit assertions (`assert not math.isnan(current_vol_bps)`); verified in `test_whitebox_assertion_defense` | **2** (S=2, L=1) |
| **RSK-SD-04** | Monotonic deque sliding window index corruption | False extreme price detection triggering wrong trades | 4 | 3 | **12** | Strict FIFO monotonic deque eviction maintaining exact window invariant; verified in `test_monotonic_deque_sliding_maximum` | **2** (S=2, L=1) |
| **RSK-SD-05** | Unchecked division by zero in router payout distribution | Stuck contract funds and transaction reverts | 4 | 3 | **12** | Proportional payout math requiring positive pool token supply; verified in `test_whitebox_router_payout_proportional_math` | **2** (S=2, L=1) |
| **RSK-SD-06** | Confidence score boundary overflow beyond $[0.0, 1.0]$ | Invalid order weights and oversized risk exposure | 4 | 3 | **12** | Hard bounding of confidence score; verified in `test_whitebox_confidence_score_ceiling_and_floors` | **2** (S=2, L=1) |

---

## 3. Governance
Audited on each commit via `make audit-iso9001`.
