# HashKey Chain Horizon Hackathon (Mumbai Edition) — AI Agent Trading Track

**Hackathon Portal:** HashKey Chain Horizon Hackathon (Mumbai Edition) on DoraHacks  
**Prize Pool:** 10,000 USDT (5,000 USDT per track)  
**Target Track:** **Track 1: AI Agent Trading (5,000 USDT Prize Pool)**  
**Submission Deadline:** November 1, 2026 at 21:30 IST (UTC+5:30)  
**Demo Day / Winners Announcement:** November 4–5, 2026  
**Author / Team:** Ishant Panchal (`Ishant5436` / `ishant.p@somaiya.edu` / Mumbai, India)  
**Project Name:** `Somnia-DreamDEX-Agent` — Volatility-Gated High-Throughput Trading Agent  
**Repository:** [https://github.com/Ishant5436/somnia-dreamdex-agent](https://github.com/Ishant5436/somnia-dreamdex-agent)  
**Verified Smart Contract:** `0xc0219209598d4d3A86ff0CcCcC531d623b51F36D` (Tx `0x79df1813e2ce54afa4c014ac4c7e2cc358a89a0a789c5adb4b1700593182e657`)  

---

## 1. Project Overview & Trading Thesis

Most decentralized algorithmic trading agents suffer from the "Microstructure Churn Trap": in consolidation regimes, retail indicators trigger high-frequency whipsaws where taker fees, spread slippage, and gas drag inevitably bleed trading capital.

`Somnia-DreamDEX-Agent` eliminates churn by implementing a quantitative **Parkinson Realized Volatility Filter**:
- **Consolidation Lockout:** When rolling realized volatility drops below the empirical regime expansion threshold ($\sigma_{\text{Parkinson}} < 15\text{ bps}$), the agent enters a strict $100\%$ FLAT state.
- **Directional Momentum Expansion:** The agent deploys capital into binary outcome contracts and perps positions ONLY during confirmed volatility expansion regimes.
- **Sub-Millisecond Price Envelopes:** Employs an $O(1)$ sliding monotonic extrema deque to compute exact rolling high/low envelopes without scanning history.

---

## 2. Quantitative Algorithms & Data Structures

| Algorithmic Component | Time Complexity | Space Complexity | Quantitative Role |
| :--- | :--- | :--- | :--- |
| **Parkinson Volatility Estimator** | $O(1)$ per tick | $O(W)$ window | Uses continuous high-low log-spread kernel; achieves $5\times$ variance efficiency over discrete close-to-close returns. |
| **Monotonic Extrema Deque** | Amortized $O(1)$ | $O(W)$ bounded | Dual monotonic double-ended queue tracking rolling extrema across arbitrary tick windows. |
| **Signal Deadband Filter** | $O(1)$ | $O(1)$ | Prevents flip-flop execution around zero-bound inflection points. |
| **Non-Reentrant Router Contract** | $O(1)$ | $O(1)$ | Atomic settlement, proportional payout distribution, and emergency cancellation liveness fallbacks. |

---

## 3. Deterministic Safety Invariants (Power of 10)

- **Control Flow:** Zero recursion, zero goto, hard bounded loops.
- **Function Bounds:** All functions $\le 60$ lines of code.
- **Assertion Density:** Minimum $\ge 2$ assertions per routine.
- **Memory Safety:** Zero dynamic heap allocation on the hot trading path after system initialization.

---

## 4. Test Suite Parity & Verification

- **Automated Tests:** 19 / 19 unit, white-box, and black-box tests passing (100% green in 5.54s).
- **Verified On-Chain Contract:** [`0xc0219209598d4d3A86ff0CcCcC531d623b51F36D`](https://shannon-explorer.somnia.network/address/0xc0219209598d4d3A86ff0CcCcC531d623b51F36D).
- **Instant Local Demonstration:** `make demo` runs live tick simulation with visual signal indicators.
