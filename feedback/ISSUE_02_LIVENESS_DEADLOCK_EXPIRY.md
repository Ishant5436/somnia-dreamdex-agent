# Bug Report: Missing Permissionless Resolution Creates Liveness Deadlock Beyond Market Expiry

**Target:** `DreamDEXRouter.sol` (Oracle / Operator Lifecycle)  
**Severity:** Major  
**Area:** Smart Contracts / Liveness & Capital Availability  
**Author:** Ishant Panchal (`Ishant5436` / `ishant.p@somaiya.edu`)  

---

## 1. Summary
`resolveMarket` is strictly gated to `onlyOwner` with no permissionless expiry fallback. If the contract owner loses access to their private key or experiences an extended outage after a market expires, 100% of deposited funds across both pools are permanently frozen with zero user recourse.

---

## 2. Technical Root Cause
- `expiryTimestamp` is recorded upon market creation and enforced to prevent new deposits (`require(block.timestamp <= market.expiryTimestamp)`).
- However, after `block.timestamp > market.expiryTimestamp`, no mechanism exists to allow participants or third-party keepers to trigger emergency cancellation or settlement if the owner does not call `resolveMarket`.
- Because `owner` is immutable and cannot be rotated, an owner key loss permanently incapacitates all unresolved markets.

---

## 3. Steps to Reproduce
1. User A and User B deposit into LONG and SHORT pools respectively.
2. The market passes `expiryTimestamp`.
3. The owner address becomes unresponsive or offline.
4. Users attempt to call `claimPayout`: reverts with `MARKET_NOT_RESOLVED`.
5. Users have no function to cancel the expired market or request their principal back.
6. Result: All deposited funds remain locked indefinitely.

---

## 4. Expected vs. Actual Behavior
- **Expected:** If a market remains unresolved after a grace period past `expiryTimestamp` (e.g., `block.timestamp > expiryTimestamp + 3 days`), any participant should be able to trigger emergency cancellation (`outcome = 3`), returning capital to original depositors.
- **Actual:** Zero permissionless fallback exists; funds depend 100% on a centralized transaction from `owner`.

---

## 5. Verified Remediation
Add an `emergencyResolveExpiredMarket` function:
```solidity
function emergencyResolveExpiredMarket(bytes32 marketId) external nonReentrant {
    Market storage market = markets[marketId];
    require(market.marketId != bytes32(0), "INVALID_MARKET");
    require(!market.isResolved, "ALREADY_RESOLVED");
    require(block.timestamp > market.expiryTimestamp + 3 days, "GRACE_PERIOD_ACTIVE");

    market.isResolved = true;
    market.outcome = 3; // CANCELLED -> enables 100% refunds

    emit MarketResolved(marketId, 3, block.timestamp);
}
```
Formally validated via automated test suite in `tests/test_whitebox.py`.
