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

**Somnia-DreamDEX-Agent** is a high-frequency autonomous prediction market agent and EVM event router built natively for the **Somnia Shannon Layer-1 Testnet**. 

Traditional prediction market bots bleed capital during consolidation chop due to spread slippage and execution fees. Our agent employs a **Parkinson Realized Volatility Gate** that locks execution during low-volatility chop (<15 bps) and deploys directional liquidity into DreamDEX binary event contracts only during regime expansion.

---

## 2. Key Architecture & Deliverables

1. **Non-Reentrant Event Router ([`DreamDEXRouter.sol`](contracts/DreamDEXRouter.sol)):**
   * Single-slot mutex locks preventing cross-contract and same-contract reentrancy.
   * Atomic outcome minting (`YES` / `NO` shares), oracle settlement, and proportional payout distribution.
   * **Permissionless Liveness Guarantee (`emergencyResolveExpiredMarket`):** If the market owner or oracle ever goes offline or fails to resolve an expired market, ANY participant can permissionlessly trigger emergency market cancellation after a 3-day grace period, unlocking 100% principal refunds.
   * Adheres strictly to Deterministic Safety Invariants (Power of 10 Rules: bounded loops, checked arithmetic).

2. **Autonomous Volatility Agent ([`src/agent_bot.py`](src/agent_bot.py)):**
   * Real-time tick ingestion and rolling realized volatility calculation.
   * Volatility chop filter gating orders below threshold.
   * Directional confidence scoring for binary prediction markets.

3. **Interactive Demo Walkthrough ([`scripts/record_demo_walkthrough.py`](scripts/record_demo_walkthrough.py)):**
   * Full end-to-end simulation from tick ingestion to onchain transaction confirmation and oracle payout disbursement.

---

## 3. Quick Verification & Demo Commands

```bash
# 1. Clone & Run Automated Test Suite (100% Passing in <0.05s)
git clone https://github.com/Ishant5436/somnia-dreamdex-agent.git
cd somnia-dreamdex-agent
pytest -v

# 2. Run Interactive Demo Execution Walkthrough
python3 scripts/record_demo_walkthrough.py
```
