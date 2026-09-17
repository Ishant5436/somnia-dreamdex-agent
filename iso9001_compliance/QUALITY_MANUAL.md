# Software Quality Management System (QMS) Manual: Somnia DreamDEX Agent
## Conforming to ISO/DIS 9001:2026 (Draft International Standard)

---

### 1. Scope & Application
This Quality Manual formalizes the Software Quality Management System (QMS) policies, procedures, and deterministic controls implemented across `somnia-dreamdex-agent`. It governs automated market making, extreme value filtering, and smart contract interaction on the Somnia EVM testnet under **ISO/DIS 9001:2026**.

---

### 2. Clause 4: Context of the Organization & Digital Infrastructure
- **4.1 Technological Context:** The agent operates on high-speed Somnia EVM testnet infrastructure (Chain ID 50311, sub-second block times) using Python 3.14 async runtimes and Solidity 0.8.20 smart contracts.
- **4.2 Stakeholder Expectations:** Somnia Hackathon evaluators, liquidity pools, and traders require zero reentrancy risks, deterministic volatility gating, bounded slippage, and zero floating-point NaN drift.
- **4.3 Scope of the QMS:** Covers all Python algorithmic trading logic (`agent_bot.py`), mathematical indicators (`indicators.py`), RPC client wrappers (`somnia_client.py`), and Solidity contracts (`DreamDEXRouter.sol`).
- **4.4 Automated Quality Pipeline:** Quality controls are defined as executable targets within [`Makefile`](file:///Users/ishantpanchal/somnia-dreamdex-agent/Makefile).

---

### 3. Clause 5: Leadership & Quality Culture
- **5.1 Leadership & Commitment:** Engineering enforces the **Zero Completion Claims Without Verification** policy. No strategy or deployment is certified without 100% automated test coverage.
- **5.2 Quality Policy:** Dedicated to mathematical indicator precision, chop-regime capital preservation, smart contract reentrancy immunity, and clean telemetry.
- **5.3 Roles & Responsibilities:** Automated pytest suites, whitebox invariant checks, and EVM contract guards serve as objective quality checkpoints.

---

### 4. Clause 6: Planning & Risk-Based Thinking
- **6.1 Actions to Address Risks & Opportunities:** The QMS maintains an active [`RISK_REGISTER.md`](file:///Users/ishantpanchal/somnia-dreamdex-agent/iso9001_compliance/RISK_REGISTER.md) evaluating failure modes like chop-regime churn, NaN price drift, smart contract reentrancy, and pool drain attacks.
- **6.2 Quality Objectives:**
  - *Chop Gating:* Zero order execution when Parkinson volatility drops below the minimum regime threshold.
  - *Numerical Safety:* 100% rejection of NaN prices, zero division, or negative volatility values.
  - *Contract Safety:* Zero reentrancy vulnerabilities and deterministic proportionality in pool payouts.

---

### 5. Clause 7: Support & Tool Qualification
- **7.1 Resources & Qualified Compilers:**
  - Python Runtime: Python 3.14 with pytest, web3.py, and ruff.
  - Solidity Tooling: Solc 0.8.20 with OpenZeppelin security contracts (`ReentrancyGuard`).
- **7.2 Documentation & Guides:** Documented in [`README.md`](file:///Users/ishantpanchal/somnia-dreamdex-agent/README.md) and [`DORAHACKS_SUBMISSION.md`](file:///Users/ishantpanchal/somnia-dreamdex-agent/DORAHACKS_SUBMISSION.md).
- **7.5 Documented Information:** Deployment receipts (`deployment_receipt.json`), test records, and event logs are systematically archived.

---

### 6. Clause 8: Operational Planning and Control (Software V&V)
- **8.1 Verification and Validation Protocol:**
  - *Verification (Unit & Indicators):* Exact mathematical verification of Parkinson High-Low volatility estimators and monotonic deque sliding min/max.
  - *Whitebox Invariants:* Bound verification of confidence score ceilings ($[0.0, 1.0]$) and trend deadbands.
  - *Smart Contract Validation:* Liquidity router mathematical checks and reentrancy protections.
- **8.7 Non-conforming Output Control:** Any NaN metric or out-of-bound signal triggers immediate execution rejection.

---

### 7. Clause 9: Performance Evaluation
- **9.1 Monitoring & Measurement:** Continuous event log tracing on Somnia testnet via `scripts/watch_testnet_events.py`.
- **9.2 Internal Audit:** Automated QMS audit executed via [`scripts/audit_iso9001_compliance.py`](file:///Users/ishantpanchal/somnia-dreamdex-agent/scripts/audit_iso9001_compliance.py).

---

### 8. Clause 10: Continual Improvement
- **10.1 Non-conformity and Corrective Action:** Failed signals or RPC connection drops trigger automatic retry mechanisms with exponential backoff.
- **10.2 Continual Improvement Cycle:** Regular calibration of deadbands and volatility cutoffs to match Somnia testnet gas dynamics.
