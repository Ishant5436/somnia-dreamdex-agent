# dreamDEX Perps Builder Bounty — Submission Dossier

**Hackathon Portal:** dreamDEX Perps Builder Bounty on DoraHacks  
**Prize Pool:** $3,000 USD  
**Submission Deadline:** November 1, 2026 at 15:59 UTC-7  
**Author / Developer:** Ishant Panchal (`Ishant5436` / `ishant.p@somaiya.edu`)  
**Project Name:** `Somnia-DreamDEX-Agent`  
**Repository:** [https://github.com/Ishant5436/somnia-dreamdex-agent](https://github.com/Ishant5436/somnia-dreamdex-agent)  
**Target Network:** Somnia Shannon Layer-1 Testnet (Chain ID 50312) & DreamDEX Event/Perps Contracts  
**Verified Router Contract:** [`0xc0219209598d4d3A86ff0CcCcC531d623b51F36D`](https://shannon-explorer.somnia.network/address/0xc0219209598d4d3A86ff0CcCcC531d623b51F36D)  
**Contract Creation Tx:** [`0x79df1813e2ce54afa4c014ac4c7e2cc358a89a0a789c5adb4b1700593182e657`](https://shannon-explorer.somnia.network/tx/0x79df1813e2ce54afa4c014ac4c7e2cc358a89a0a789c5adb4b1700593182e657)  

---

## 1. Project Description & Problem Statement

Perpetuals and binary event markets on high-throughput L1 chains like Somnia require automated agents capable of liquidity routing and risk mitigation without human latency. However, high-frequency bot strategies frequently run into toxic order execution: during low-volatility consolidation chop, they over-trade and bleed capital via exchange spreads and taker fees.

`Somnia-DreamDEX-Agent` introduces an institutional quantitative approach to DreamDEX event trading by pairing a Parkinson high-low realized volatility filter with an EVM-verified non-reentrant router contract:

1. **Parkinson Volatility Gate:**
   - Computes rolling Parkinson volatility using continuous price extremes rather than discrete closing prices, providing $5\times$ variance efficiency.
   - Restricts order generation when volatility is below 15 bps (consolidation regimes), preserving principal.
   - Deploys directional capital during confirmed volatility regime expansion.

2. **Non-Reentrant Router Contract (`DreamDEXRouter.sol`):**
   - Single-slot mutex preventing both cross-contract and same-contract reentrancy attacks.
   - Atomic outcome minting, oracle settlement, and proportional pari-mutuel payout distribution.
   - Permissionless liveness fallback: if an oracle goes offline, any participant can trigger emergency cancellation after a 3-day grace period. Empty winning pools automatically trigger full principal refunds.

---

## 2. Quantitative Algorithms & Safety Invariants

- **Monotonic Extrema Deque:** $O(1)$ amortized sliding maximum/minimum tracking for sub-millisecond envelope generation.
- **Power of 10 Deterministic Safety Invariants:**
  - Function length strictly $\le 60$ lines.
  - Assertion density $\ge 2$ checks per function.
  - Zero dynamic heap allocation on the hot path after initialization.
  - Zero unhandled exceptions or unchecked arithmetic.

---

## 3. Verification & Reproduction Steps

1. Clone repository:
   ```bash
   git clone https://github.com/Ishant5436/somnia-dreamdex-agent.git
   cd somnia-dreamdex-agent
   ```
2. Run automated test suite (19/19 passing tests including reentrancy defense and emergency auto-refund):
   ```bash
   make test
   ```
3. Run instant visual demonstration:
   ```bash
   make demo
   ```
