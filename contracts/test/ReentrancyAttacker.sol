// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title ReentrancyAttacker
 * @notice Test-only helper contract for tests/test_whitebox.py's reentrancy
 * attack test. Not part of the deployed protocol. Attempts a single
 * reentrant call back into claimPayout from inside its receive() fallback,
 * exactly the classic reentrancy pattern nonReentrant guards defend against.
 */
interface IDreamDEXRouter {
    function buyOutcomeShares(bytes32 marketId, bool isLong) external payable;
    function claimPayout(bytes32 marketId) external returns (uint256);
}

contract ReentrancyAttacker {
    IDreamDEXRouter public immutable router;
    bytes32 public targetMarketId;

    uint256 public reentrantCallCount;
    bool public reentrancyReverted;
    uint256 public totalReceived;

    constructor(address routerAddress) {
        router = IDreamDEXRouter(routerAddress);
    }

    function buyShares(bytes32 marketId, bool isLong) external payable {
        router.buyOutcomeShares{value: msg.value}(marketId, isLong);
    }

    function attackClaim(bytes32 marketId) external {
        targetMarketId = marketId;
        router.claimPayout(marketId);
    }

    receive() external payable {
        totalReceived += msg.value;
        // Attempt exactly one reentrant claim, wrapped in try/catch so a
        // *sophisticated* attacker (one who anticipates and swallows the
        // guard's revert) still can't extract a second payout -- the
        // stronger claim than "a naive attacker's whole tx reverts".
        if (reentrantCallCount == 0) {
            reentrantCallCount++;
            try router.claimPayout(targetMarketId) returns (uint256) {
                // Reaching here means the guard failed to block reentrancy.
            } catch {
                reentrancyReverted = true;
            }
        }
    }
}
