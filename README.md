# Somnia × DreamDEX Autonomous Event Contract Agent

An ultra-low-latency, non-custodial AI Agent and smart contract routing protocol engineered for **Somnia Layer-1** and **DreamDEX Event Contracts**.

## 1. Problem Statement
Prediction markets and binary event contracts often suffer from:
1. **Spread & Arbitrage Inefficiencies:** Retail participants trade without real-time volatility gating, overpaying for low-probability outcomes during consolidation regimes.
2. **Reentrancy & Execution Risks:** Naive settlement routers lack deterministic invariant checks, exposing pools to flash-drain attacks.
3. **Execution Latency:** High-frequency event resolution requires sub-second finality.

## 2. Architecture & Solution
`somnia-dreamdex-agent` combines:
* **DreamDEXRouter.sol:** Non-reentrant EVM settlement router optimized for Somnia's 400,000+ TPS testnet.
* **Parkinson Volatility Gating:** Autonomous agent locks out trading during low-volatility chop (<15 bps), deploying liquidity only during confirmed volatility breakouts.
* **Non-Custodial Settlement:** Merkle-verified event resolution with atomic payouts and zero custodial risk.

```
Real-Time Market Volatility Stream
               │
               ▼
   Parkinson Volatility Gating
    ├── (Chop < 15 bps)        ──► PASS (Zero Capital Risked)
    └── (Volatility Expansion) ──► Triple-Timeframe Momentum Direction
                                              │
                                              ▼
                             DreamDEXRouter.sol (Somnia L1)
```

## 3. Verification & Testing
```bash
git clone https://github.com/Ishant5436/somnia-dreamdex-agent.git
cd somnia-dreamdex-agent
python3 tests/test_agent.py
```

## License
MIT License.
