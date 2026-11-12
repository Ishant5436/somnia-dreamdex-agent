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

---

## 4. Formal Smart Contract Bug & Vulnerability Reports ($95 Claim)

The audit team identified three structural vulnerabilities in standard perpetual / event prediction routing logic and implemented validated remediation fixtures in `contracts/DreamDEXRouter.sol`:

1. **[ISSUE-01: Zero Winning Pool Collateral Lockup](feedback/ISSUE_01_EMPTY_WINNING_POOL_LOCKUP.md)** ($35 Bounty Claim)
   - *Impact:* When an outcome wins that has zero token holders, all collateral in the losing pool becomes permanently unclaimable.
   - *Remediation:* Automatically routes funds to emergency refund when `winningPool == 0`.

2. **[ISSUE-02: Oracle Settlement Liveness Deadlock](feedback/ISSUE_02_LIVENESS_DEADLOCK_EXPIRY.md)** ($35 Bounty Claim)
   - *Impact:* An offline or compromised oracle halts outcome resolution indefinitely with no fallback.
   - *Remediation:* Enforces a 3-day post-expiration grace period after which any participant can trigger emergency refund.

3. **[ISSUE-03: Unaccounted Native Balance Lockup](feedback/ISSUE_03_UNACCOUNTED_RECEIVE_LOCKUP.md)** ($25 Bounty Claim)
   - *Impact:* Direct transfers of native gas tokens to the router without calling `mintOutcome` cause permanent collateral entrapment.
   - *Remediation:* Restricts `receive()` / `fallback()` to verified refund mechanisms only.

