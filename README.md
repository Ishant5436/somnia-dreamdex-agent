# Somnia × DreamDEX Autonomous Event Contract Agent

An ultra-high-throughput, non-custodial AI Agent and smart contract routing protocol engineered natively for **Somnia Layer-1** (Shannon Testnet) and **DreamDEX Event Contracts**.

[![Tests](https://img.shields.io/badge/Tests-11%2F11%20Passed-brightgreen)](tests/)
[![Network](https://img.shields.io/badge/Network-Somnia%20Shannon%20(50312)-blue)](https://somnia.network)
[![Solidity](https://img.shields.io/badge/Solidity-0.8.20-orange)](contracts/DreamDEXRouter.sol)
[![Safety](https://img.shields.io/badge/Safety%20Standard-Deterministic%20Invariants-purple)](contracts/DreamDEXRouter.sol)

---

## 1. Problem & Core Innovation

Prediction markets and binary event contracts on high-speed Layer-1 networks face two critical structural challenges:
1. **Spread Drag & Consolidation Bleed:** Automated retail bots trade continuously in range-bound chop, bleeding capital to bid-ask spread friction and protocol taker fees.
2. **Reentrancy & Settlement Vulnerabilities:** Naive prediction routers lack single-slot mutex locks, exposing pari-mutuel prize pools to cross-contract drain exploits.

### The Solution
`somnia-dreamdex-agent` solves this by introducing **Parkinson Realized Volatility Gating**:
* The agent streams real-time micro-ticks and computes rolling realized volatility.
* **Chop Filter:** When volatility is below 15 bps, execution is 100% gated (zero capital risked).
* **Breakout Deployment:** When volatility expands with triple-timeframe momentum alignment ($|\text{trend}| > 0.30$), the agent deploys directional liquidity into DreamDEX binary event contracts.

```
                    Real-Time Somnia L1 Tick Stream
                                  │
                                  ▼
                   Parkinson Volatility Evaluator
                    ├── (Realized Vol < 15 bps)  ──► PASS (Chop Gated / $0 Risk)
                    └── (Vol Expansion > 15 bps) ──► Momentum Directional Scoring
                                                               │
                                                               ▼
                                                  DreamDEXRouter.sol (Somnia L1)
                                                  ├── Atomic Pari-Mutuel Shares
                                                  ├── Mutex Reentrancy Guard
                                                  └── Oracle Settlement & Payout
```

---

## 2. Mathematical & Architectural Specification

### Realized Volatility Formulation
Realized volatility is computed over rolling tick windows:
$$\sigma_{\text{realized}} = \sqrt{\frac{1}{N} \sum_{i=1}^{N} \left(\frac{P_i - P_{i-1}}{P_{i-1}}\right)^2} \times 10{,}000 \quad (\text{bps})$$

### Pari-Mutuel Settlement Formula ([`contracts/DreamDEXRouter.sol`](contracts/DreamDEXRouter.sol))
When a binary market resolves with outcome $W \in \{\text{LONG}, \text{SHORT}\}$:
$$\text{Payout}(u) = \frac{\text{Shares}(u, W) \times \text{TotalPool}_{\text{net}}}{\text{TotalPool}(W)}$$
$$\text{TotalPool}_{\text{net}} = \text{Deposit}_{\text{gross}} \times \left(1 - \frac{\text{Fee}_{\text{BPS}}}{10{,}000}\right)$$

---

## 3. Key Deliverables & Safety Standards

1. **Non-Reentrant Settlement Router ([`contracts/DreamDEXRouter.sol`](contracts/DreamDEXRouter.sol)):**
   * Single-slot mutex locks (`_locked == 1 -> 2 -> 1`) preventing reentrancy attacks.
   * Proportional payout accounting with safe principal refund on market cancellations.
   * Owner fee segregation and withdrawal (`withdrawFees()`).
   * Fallback `receive()` handler for direct transfers.

2. **Autonomous Volatility Agent ([`src/agent_bot.py`](src/agent_bot.py)):**
   * Rolling volatility calculation and chop gating.
   * Bounded confidence scoring $[0.0, 0.95]$.
   * Power of 10 safety invariants (checked returns, parameter validation).

3. **Interactive Demo Simulation ([`scripts/record_demo_walkthrough.py`](scripts/record_demo_walkthrough.py)):**
   * End-to-end simulation from tick ingestion to onchain execution and oracle payout.

---

## 4. Quickstart & Test Verification

```bash
# 1. Clone Repository
git clone https://github.com/Ishant5436/somnia-dreamdex-agent.git
cd somnia-dreamdex-agent

# 2. Run Comprehensive QA Test Suite (11/11 tests pass in < 0.05s)
python3 -m pytest -v

# 3. Execute Interactive Terminal Demo Walkthrough
python3 scripts/record_demo_walkthrough.py
```

---

## 5. Network Configuration

* **Network:** Somnia Shannon Testnet
* **Chain ID:** `50312`
* **RPC Endpoint:** `https://dream-rpc.somnia.network`
* **Currency Symbol:** `STT`

---

## License
MIT License. Open source and non-custodial.
