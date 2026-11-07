# Bug Report: Unaccounted ETH Received via Fallback is Permanently Stuck

**Target:** `DreamDEXRouter.sol` (Treasury & Accounting)  
**Severity:** Normal  
**Area:** Smart Contracts / Accounting & Fund Recovery  
**Author:** Ishant Panchal (`Ishant5436` / `ishant.p@somaiya.edu`)  

---

## 1. Summary
The contract defines an empty payable fallback function `receive() external payable {}`. Any ETH delivered to the contract via direct transfer or `selfdestruct` is not credited to any market pool or protocol fees, leaving it permanently trapped in the contract balance with no recovery mechanism.

---

## 2. Technical Root Cause
- The contract includes:
  ```solidity
  receive() external payable {}
  ```
- Because neither `buyOutcomeShares`, `claimPayout`, nor `withdrawFees` track arbitrary ETH balances, any funds sent directly to the contract address bypass the internal accounting system.
- There is no administrative sweep function to rescue stray ETH.

---

## 3. Steps to Reproduce
1. A user or protocol accidentally sends 0.5 ETH directly to the contract address via `address(router).call{value: 0.5 ether}("")`.
2. The transaction succeeds because `receive()` is payable.
3. Contract balance increases by 0.5 ETH.
4. Neither `totalProtocolFees` nor any market pool increases.
5. The 0.5 ETH cannot be claimed by users or withdrawn by the owner.
6. Result: The 0.5 ETH is permanently stuck.

---

## 4. Expected vs. Actual Behavior
- **Expected:** Either direct transfers should revert by removing the `receive()` function, forcing all ETH through accounted deposit functions, or an owner-only sweep function should allow recovering accidental non-pool funds:
  $$\text{Stray ETH} = \text{address(this).balance} - (\text{totalActivePools} + \text{totalProtocolFees})$$
- **Actual:** Direct ETH is accepted and permanently trapped.

---

## 5. Verified Remediation
Option A (Strict):
Remove `receive() external payable {}` entirely to revert all direct transfers.

Option B (Rescue):
Implement an exact sweep function bounded by tracked protocol liabilities:
```solidity
function rescueStrayETH(address recipient) external onlyOwner nonReentrant {
    require(recipient != address(0), "INVALID_RECIPIENT");
    uint256 trackedBalance = totalProtocolFees;
    // Calculate tracked active pools
    uint256 excess = address(this).balance > trackedBalance ? address(this).balance - trackedBalance : 0;
    require(excess > 0, "NO_EXCESS");
    (bool s, ) = recipient.call{value: excess}("");
    require(s, "TRANSFER_FAILED");
}
```
