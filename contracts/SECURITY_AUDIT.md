# DreamDEXRouter.sol — Security Audit

**Scope:** `contracts/DreamDEXRouter.sol` (197 lines, Solidity `^0.8.20`)
**Method:** Manual line-by-line review, plus a real reentrancy attack executed against the actual compiled bytecode on a local EVM (`anvil`) — not a Python reimplementation of the contract's arithmetic.

---

## Summary

The reentrancy guard, checks-effects-interactions ordering, and fee accounting are all correctly implemented and were verified two ways: manual review, and by actually attacking the deployed bytecode with a malicious contract. The two real findings below are not reentrancy bugs — they're about what happens when the owner is unavailable, and about ETH sent outside the normal deposit flow.

**A note on prior verification of this contract:** before this audit, this repository's only router-related test (`test_whitebox_router_payout_proportional_math`) reimplemented the payout formula in pure Python — it never compiled or executed the Solidity. `scripts/deploy_somnia_testnet.py` computes a `sha256`-derived "simulated_contract_address" rather than performing a real deployment. As far as this audit could determine, this was the first time `DreamDEXRouter.sol` was actually compiled and run on an EVM. That matters specifically for the reentrancy question: reentrancy is a property of EVM call semantics during an external call, and cannot be proven or disproven by re-deriving arithmetic in a different language.

---

## 1. Reentrancy Guard — verified correct, with an important methodology note

`_locked` (line 35) is a single `uint256` storage slot, initialized to `1` in the constructor, guarded by:

```solidity
modifier nonReentrant() {
    require(_locked == 1, "REENTRANCY_GUARD");
    _locked = 2;
    _;
    _locked = 1;
}
```

This is the standard 1↔2 (not 0/1) mutex pattern — using two non-zero values avoids the extra gas cost of a zero-to-nonzero `SSTORE` on every lock/unlock cycle. Applied to `buyOutcomeShares`, `resolveMarket`, `claimPayout`, and `withdrawFees`. Correctly implemented.

**I did not stop at reading the code.** I compiled the real contract with `solc 0.8.20` (exact match to the pragma), deployed it to a real local EVM via `anvil`, deployed a purpose-built `ReentrancyAttacker.sol` (`contracts/test/ReentrancyAttacker.sol`) alongside it, and had the attacker actually attempt to re-enter `claimPayout` from its `receive()` fallback mid-payout. Result: the reentrant call reverts with `REENTRANCY_GUARD`, and the attacker receives exactly one payout — confirmed on-chain, not inferred from source reading.

**Validating the test itself mattered as much as the result.** My first version of this test passed against the real contract — and then, when I deliberately removed the guard from `claimPayout` to confirm the test would catch a real vulnerability, it *still passed*. That was a false negative in my test's economic setup, not evidence of safety: the attacker held 100% of the winning pool, so a single legitimate payout already drained nearly the entire contract balance, and a second exploit attempt failed from plain insufficient balance — not from anything blocking it. I corrected the test to have several other depositors hold most of the winning pool (so the attacker's own share, and thus a potential double-payout, is small relative to available contract balance), then re-validated:

| Scenario | Result |
|---|---|
| Real contract (guard + correct CEI ordering) | Attack blocked [PASS] |
| Guard removed, CEI ordering unchanged | Attack blocked [PASS] (CEI alone sufficient) |
| Guard present, CEI ordering deliberately violated (`hasClaimed` moved after the external call) | Attack blocked [PASS] (guard alone sufficient) |
| **Both removed simultaneously** | **Attack succeeds — test correctly fails and reports it** [FAIL]→test catches it |

This is genuine defense-in-depth: `claimPayout` is protected by two independent mechanisms (the mutex, and correct effects-before-interaction ordering), and my test now provably distinguishes a contract that has this protection from one that doesn't, rather than passing regardless.

The test is checked in as `tests/test_whitebox.py::test_whitebox_reentrancy_attack_blocked_by_guard`. It requires `solc` and `anvil` on `PATH` and skips gracefully if they're unavailable.

## 2. Checks-Effects-Interactions

Both functions that make external calls follow correct CEI ordering:

- **`claimPayout`** (line 145): `pos.hasClaimed = true` (line 170) is set *before* `msg.sender.call{value: payout}("")` (line 173). A reentrant call sees `hasClaimed == true` and reverts on `require(!pos.hasClaimed)`, independent of the mutex (see §1).
- **`withdrawFees`** (line 184): `totalProtocolFees = 0` (line 187) is set before `owner.call{value: amountToWithdraw}("")` (line 189). Same protection.

One stylistic note, not a bug: in `claimPayout`, `require(payout > 0, "ZERO_PAYOUT")` (line 171) executes *after* `pos.hasClaimed = true` (line 170). If that require fails, the whole transaction reverts, which rolls back the `hasClaimed` write too — so this is safe by Solidity's atomicity, just not a textbook "all checks, then all effects" ordering. Worth tidying for readability, not a functional issue.

## 3. Fee Accounting

`fee = (msg.value * PROTOCOL_FEE_BPS) / MAX_BPS` = `msg.value * 20 / 10000` = 0.20% exactly, matching the documented constant. Verified: `totalProtocolFees` accumulates only from this calculation, is fully isolated from `totalLongPool`/`totalShortPool` (pools only ever receive `netAmount`, post-fee), and is reset to zero atomically with its own withdrawal. No commingling between user funds and protocol revenue found.

**Payout math (pari-mutuel formula):** `payout = (userShares * totalPool) / totalPoolOnWinningSide`. Verified safe against overflow (Solidity 0.8's built-in checked arithmetic), safe against division-by-zero (a user can only hold `winningShares > 0` if that side's pool total is also `> 0`, by construction — see `buyOutcomeShares`), and safe against underpayment risk: integer division truncates in the contract's favor, so the sum of all individually-rounded payouts can only ever be *less than or equal to* the pool, never more. The contract cannot be talked into paying out more than it holds via rounding.

## 4. Findings

### Finding 1 — No permissionless or timeout-based market resolution (Medium/High — liveness, not theft)

`resolveMarket` is `onlyOwner`-gated with no expiry-based fallback. `expiryTimestamp` is tracked and *enforced to block new deposits* (`buyOutcomeShares` line 106), but nothing ever uses it to force resolution, cancellation, or a permissionless refund path. If the owner never calls `resolveMarket` for a given market — through negligence, lost keys, or malice — every depositor's funds in that market are **permanently locked with no recourse**. There is no way for users to reclaim their own money even after the market's own stated expiry has passed.

This is a real design gap, not a theoretical one: the contract already has all the information needed (`market.expiryTimestamp`) to offer a fallback, and simply doesn't use it. Recommend adding a permissionless path — e.g., anyone can call a `cancelExpiredMarket` after some grace period past `expiryTimestamp` if still unresolved, triggering outcome `3` (CANCELLED) refund behavior that already exists in `claimPayout`.

### Finding 2 — ETH sent via `receive()` is permanently unrecoverable (Low/Medium)

```solidity
receive() external payable {}
```

The docstring explicitly anticipates ETH arriving this way ("e.g. from selfdestruct"), but any ETH that lands in the contract outside `buyOutcomeShares` is never added to any market's pool and never added to `totalProtocolFees` — it's invisible to both `claimPayout` and `withdrawFees`. Whether from an accidental direct transfer, an intentional donation, or a `selfdestruct`-forced send, that ETH is stuck in the contract forever with no function capable of moving it out. Recommend either rejecting direct transfers (remove `receive()`, forcing all deposits through the accounted path) or adding an owner-gated sweep for exactly this category of stray funds.

### Positive notes

- `owner` is `immutable` with no transfer function — no owner-key-rotation attack surface, though it does mean permanent key loss disables future `resolveMarket`/`withdrawFees` calls (already-resolved markets remain claimable regardless).
- `block.timestamp` usage (expiry checks, `marketId` derivation) is only exposed to the standard few-second miner/validator manipulation window inherent to all EVM chains; given day-scale duration granularity (`durationSeconds > 60`, `MAX_EXPIRY_HORIZON = 30 days`), this isn't practically exploitable here.
- `marketId = keccak256(abi.encodePacked(msg.sender, block.timestamp, marketCount))` — all three inputs are fixed-size types, so `abi.encodePacked`'s known dynamic-type collision ambiguity doesn't apply.

---

## Power of 10 Safety Matrix (adapted for Solidity)

Gerard J. Holzmann's original Power of 10 rules target C; this maps them to the closest meaningful EVM/Solidity equivalent rather than restating them verbatim, and is graded honestly against what was actually verified above — not a blanket pass.

| # | Rule (adapted) | Status | Basis |
|---|---|---|---|
| 1 | Simple control flow — no recursion, no unbounded internal calls | [PASS] Pass | No recursive functions; all control flow is straight-line or single-level `if`/`else` |
| 2 | Bounded loops | [PASS] Pass (vacuous) | Contract contains no loops at all — nothing to bound |
| 3 | No unchecked low-level memory/pointer tricks | [PASS] Pass | No inline assembly, no unsafe casts |
| 4 | Function length reasonable, single responsibility | [PASS] Pass | Longest function (`claimPayout`) is ~35 lines |
| 5 | Assertion / invariant density | ⚠️ Partial | `require()` guards all critical preconditions well, but there is no invariant check for "can this market ever become permanently unclaimable" (see Finding 1) |
| 6 | Minimal, tightly-scoped state | [PASS] Pass | State variables are minimal and each has a single clear owner/purpose |
| 7 | Check all return values / external call results | [PASS] Pass | Both external `.call()` sites check `success` and `require` on it |
| 8 | Reentrancy discipline (CEI + guards) | [PASS] Pass — verified twice | Manual review + real attack against compiled bytecode (§1, §2) |
| 9 | Access control correctness | [PASS] Pass | `onlyOwner` correctly gates `resolveMarket`/`withdrawFees`; no missing modifier found |
| 10 | Fund accounting correctness (no over/under-payment) | ⚠️ Partial | Payout math itself is sound (§3), but Findings 1 and 2 both describe real ETH that can become permanently stuck under specific conditions |

**2 of 10 rows are "Partial," not "Pass"** — both point at the same underlying theme: the contract correctly protects funds *while they're actively claimable*, but has no mechanism for the cases where a market's owner-dependent lifecycle stalls, or where ETH arrives outside the accounted flow.
