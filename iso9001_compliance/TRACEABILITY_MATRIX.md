# ISO/DIS 9001:2026 Bidirectional Traceability Matrix: Somnia DreamDEX Agent

This matrix establishes forward and backward traceability between market making requirements, source code, test cases, and verifiable evidence artifacts.

---

## 1. Traceability Mapping

| Requirement ID | Requirement Specification | Test Case ID | Test Implementation | Target Source Component | Verifiable Evidence Artifact |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **REQ-SD-001** | High-Low Parkinson realized volatility estimator with zero spread resilience | `TC-IND-01` | [`test_indicators.py`](file:///Users/ishantpanchal/somnia-dreamdex-agent/tests/test_indicators.py#L10) | [`indicators.py`](file:///Users/ishantpanchal/somnia-dreamdex-agent/src/indicators.py) | Pytest execution log |
| **REQ-SD-002** | Monotonic deque sliding window extremum calculation | `TC-IND-02` | [`test_indicators.py`](file:///Users/ishantpanchal/somnia-dreamdex-agent/tests/test_indicators.py#L30) | [`indicators.py`](file:///Users/ishantpanchal/somnia-dreamdex-agent/src/indicators.py) | Pytest execution log |
| **REQ-SD-003** | Volatility chop gating blocking trading in flat markets | `TC-AGT-01` | [`test_agent.py`](file:///Users/ishantpanchal/somnia-dreamdex-agent/tests/test_agent.py#L18) | [`agent_bot.py`](file:///Users/ishantpanchal/somnia-dreamdex-agent/src/agent_bot.py) | Pytest execution log |
| **REQ-SD-004** | Momentum expansion bullish breakout signal generation | `TC-AGT-02` | [`test_agent.py`](file:///Users/ishantpanchal/somnia-dreamdex-agent/tests/test_agent.py#L32) | [`agent_bot.py`](file:///Users/ishantpanchal/somnia-dreamdex-agent/src/agent_bot.py) | Pytest execution log |
| **REQ-SD-005** | Momentum expansion bearish breakdown signal generation | `TC-AGT-03` | [`test_agent.py`](file:///Users/ishantpanchal/somnia-dreamdex-agent/tests/test_agent.py#L48) | [`agent_bot.py`](file:///Users/ishantpanchal/somnia-dreamdex-agent/src/agent_bot.py) | Pytest execution log |
| **REQ-SD-006** | Simulated execution and order logging lifecycle | `TC-AGT-04` | [`test_agent.py`](file:///Users/ishantpanchal/somnia-dreamdex-agent/tests/test_agent.py#L65) | [`agent_bot.py`](file:///Users/ishantpanchal/somnia-dreamdex-agent/src/agent_bot.py) | Pytest execution log |
| **REQ-SD-007** | Strict assertion defense against NaN volatility or invalid trend bounds | `TC-WB-01` | [`test_whitebox.py`](file:///Users/ishantpanchal/somnia-dreamdex-agent/tests/test_whitebox.py#L45) | [`agent_bot.py`](file:///Users/ishantpanchal/somnia-dreamdex-agent/src/agent_bot.py) | Pytest execution log |
| **REQ-SD-008** | Confidence score boundary verification ($[0.0, 1.0]$ ceiling and floor) | `TC-WB-02` | [`test_whitebox.py`](file:///Users/ishantpanchal/somnia-dreamdex-agent/tests/test_whitebox.py#L35) | [`agent_bot.py`](file:///Users/ishantpanchal/somnia-dreamdex-agent/src/agent_bot.py) | Pytest execution log |
| **REQ-SD-009** | Proportional payout mathematics in DEX router | `TC-WB-03` | [`test_whitebox.py`](file:///Users/ishantpanchal/somnia-dreamdex-agent/tests/test_whitebox.py#L55) | [`DreamDEXRouter.sol`](file:///Users/ishantpanchal/somnia-dreamdex-agent/contracts/DreamDEXRouter.sol) | Pytest execution log |
| **REQ-SD-010** | Blackbox end-to-end demo execution walkthrough | `TC-BB-01` | [`test_blackbox.py`](file:///Users/ishantpanchal/somnia-dreamdex-agent/tests/test_blackbox.py#L10) | Entire Agent Bot | Pytest execution log |

---

## 2. Verification Coverage
- **Total Tracked Requirements:** 10
- **Automated Verification Coverage:** 100% (16 passed unit and whitebox tests)
