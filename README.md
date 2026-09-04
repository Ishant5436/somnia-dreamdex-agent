# Somnia × DreamDEX Autonomous Event Contract Agent

An ultra-high-throughput, non-custodial AI Agent and smart contract routing protocol engineered natively for **Somnia Layer-1** (Shannon Testnet) and **DreamDEX Event Contracts**.

[![Tests](https://img.shields.io/badge/Tests-17%2F17%20Passed-brightgreen)](tests/)
[![CI](https://github.com/Ishant5436/somnia-dreamdex-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/Ishant5436/somnia-dreamdex-agent/actions)
[![Network](https://img.shields.io/badge/Network-Somnia%20Shannon%20(50312)-blue)](https://somnia.network)
[![Contract](https://img.shields.io/badge/Contract-0xc021...F36D-green)](https://shannon-explorer.somnia.network/address/0xc0219209598d4d3A86ff0CcCcC531d623b51F36D)
[![Solidity](https://img.shields.io/badge/Solidity-0.8.20-orange)](contracts/DreamDEXRouter.sol)
[![Safety](https://img.shields.io/badge/Safety%20Standard-Deterministic%20Invariants-purple)](contracts/DreamDEXRouter.sol)

> **Competition Track:** Event Contracts Hackathon (Somnia Network & DreamDEX) — $5,000 Prize Pool  
> **Verified Somnia Shannon Testnet Contract:** [`0xc0219209598d4d3A86ff0CcCcC531d623b51F36D`](https://shannon-explorer.somnia.network/address/0xc0219209598d4d3A86ff0CcCcC531d623b51F36D)  
> **On-Chain Creation Tx:** [`0x79df1813e2ce54afa4c014ac4c7e2cc358a89a0a789c5adb4b1700593182e657`](https://shannon-explorer.somnia.network/tx/0x79df1813e2ce54afa4c014ac4c7e2cc358a89a0a789c5adb4b1700593182e657)  
> **1-Second Instant Demo:** `make demo`

![Somnia DreamDEX Agent Demo](assets/somnia_agent_demo.gif)

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

---

## 2. Data Structures & Algorithmic Complexity

| Component | Primitive | Time Complexity | Space Complexity | Theoretical Invariant |
| :--- | :--- | :---: | :---: | :--- |
| **Parkinson Volatility** | High-Low Log-Spread Kernel | $\mathcal{O}(1)$ rolling step | $\mathcal{O}(W)$ deque | $\sigma^2 = \frac{1}{4 \ln 2 \cdot N} \sum \ln(H_i / L_i)^2$; 5x variance efficiency over close-to-close returns. |
| **Extrema Deque** | `SlidingMonotonicExtremum` | $\mathcal{O}(1)$ amortized | $\mathcal{O}(W)$ index queue | Monotonic index-tagged deque; evicts non-extrema in-place; zero heap allocations. |
| **Pari-Mutuel Router** | `DreamDEXRouter.sol` | $\mathcal{O}(1)$ execution | $\mathcal{O}(1)$ slot storage | Single-slot reentrancy mutex (`_status == 1 -> 2 -> 1`); checks-effects-interactions payout distribution. |
| **Chop Filter Gate** | Threshold Deadband | $\mathcal{O}(1)$ check | $\mathcal{O}(1)$ scalar | Bounded signal deadband $[-0.30, +0.30]$; strict confidence score floor and ceiling ($[0.0, 0.95]$). |

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

# 2. Run Comprehensive QA Test Suite (17/17 tests pass in < 0.05s)
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
