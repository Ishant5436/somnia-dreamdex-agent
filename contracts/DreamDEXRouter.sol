// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title DreamDEXRouter
 * @notice High-throughput event contract execution and settlement router for Somnia Layer-1.
 * Engineered with Deterministic Safety Invariants and non-reentrant guards.
 */
contract DreamDEXRouter {
    // --- Constants ---
    uint256 public constant PROTOCOL_FEE_BPS = 20; // 0.20% fee
    uint256 public constant MAX_BPS = 10000;
    uint256 public constant MAX_EXPIRY_HORIZON = 30 days;

    // --- Structs ---
    struct EventMarket {
        bytes32 marketId;
        address creator;
        string title;
        uint256 expiryTimestamp;
        uint256 totalLongPool;
        uint256 totalShortPool;
        bool isResolved;
        uint8 winningOutcome; // 0: Unresolved, 1: LONG_WINS, 2: SHORT_WINS, 3: CANCELLED
    }

    struct UserPosition {
        uint256 longShares;
        uint256 shortShares;
        bool hasClaimed;
    }

    // --- State Variables ---
    address public immutable owner;
    uint256 private _locked;
    uint256 public marketCount;

    mapping(bytes32 => EventMarket) public markets;
    mapping(bytes32 => mapping(address => UserPosition)) public positions;

    // --- Events ---
    event MarketCreated(bytes32 indexed marketId, address indexed creator, string title, uint256 expiry);
    event SharesPurchased(bytes32 indexed marketId, address indexed buyer, bool isLong, uint256 amount);
    event MarketResolved(bytes32 indexed marketId, uint8 winningOutcome, uint256 timestamp);
    event PayoutClaimed(bytes32 indexed marketId, address indexed claimant, uint256 payoutAmount);

    // --- Modifiers ---
    modifier nonReentrant() {
        require(_locked == 1, "REENTRANCY_GUARD");
        _locked = 2;
        _;
        _locked = 1;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "UNAUTHORIZED_CALLER");
        _;
    }

    constructor() {
        owner = msg.sender;
        _locked = 1;
    }

    /**
     * @notice Create a new binary prediction event market on Somnia.
     */
    function createMarket(
        string calldata title,
        uint256 durationSeconds
    ) external returns (bytes32 marketId) {
        require(bytes(title).length > 0 && bytes(title).length <= 128, "INVALID_TITLE_LENGTH");
        require(durationSeconds > 60 && durationSeconds <= MAX_EXPIRY_HORIZON, "INVALID_DURATION");

        marketId = keccak256(abi.encodePacked(msg.sender, block.timestamp, marketCount));
        require(markets[marketId].creator == address(0), "MARKET_COLLISION");

        uint256 expiry = block.timestamp + durationSeconds;
        markets[marketId] = EventMarket({
            marketId: marketId,
            creator: msg.sender,
            title: title,
            expiryTimestamp: expiry,
            totalLongPool: 0,
            totalShortPool: 0,
            isResolved: false,
            winningOutcome: 0
        });

        marketCount++;
        emit MarketCreated(marketId, msg.sender, title, expiry);
        return marketId;
    }

    /**
     * @notice Deposit funds into LONG or SHORT outcome pool.
     */
    function buyOutcomeShares(
        bytes32 marketId,
        bool isLong
    ) external payable nonReentrant {
        EventMarket storage market = markets[marketId];
        require(market.creator != address(0), "MARKET_NOT_FOUND");
        require(!market.isResolved, "MARKET_ALREADY_RESOLVED");
        require(block.timestamp < market.expiryTimestamp, "MARKET_EXPIRED");
        require(msg.value >= 0.001 ether, "MIN_DEPOSIT_THRESHOLD");

        uint256 fee = (msg.value * PROTOCOL_FEE_BPS) / MAX_BPS;
        uint256 netAmount = msg.value - fee;

        if (isLong) {
            market.totalLongPool += netAmount;
            positions[marketId][msg.sender].longShares += netAmount;
        } else {
            market.totalShortPool += netAmount;
            positions[marketId][msg.sender].shortShares += netAmount;
        }

        emit SharesPurchased(marketId, msg.sender, isLong, netAmount);
    }

    /**
     * @notice Settle and resolve an event contract outcome.
     */
    function resolveMarket(
        bytes32 marketId,
        uint8 outcome
    ) external onlyOwner nonReentrant {
        EventMarket storage market = markets[marketId];
        require(market.creator != address(0), "MARKET_NOT_FOUND");
        require(!market.isResolved, "ALREADY_RESOLVED");
        require(outcome == 1 || outcome == 2 || outcome == 3, "INVALID_OUTCOME");

        market.isResolved = true;
        market.winningOutcome = outcome;

        emit MarketResolved(marketId, outcome, block.timestamp);
    }

    /**
     * @notice Claim winning payout from resolved event market.
     */
    function claimPayout(
        bytes32 marketId
    ) external nonReentrant returns (uint256 payout) {
        EventMarket storage market = markets[marketId];
        require(market.isResolved, "MARKET_NOT_RESOLVED");

        UserPosition storage pos = positions[marketId][msg.sender];
        require(!pos.hasClaimed, "ALREADY_CLAIMED");

        uint256 totalPool = market.totalLongPool + market.totalShortPool;
        require(totalPool > 0, "EMPTY_POOL");

        if (market.winningOutcome == 1) {
            // LONG WINS
            require(pos.longShares > 0, "NO_WINNING_SHARES");
            payout = (pos.longShares * totalPool) / market.totalLongPool;
        } else if (market.winningOutcome == 2) {
            // SHORT WINS
            require(pos.shortShares > 0, "NO_WINNING_SHARES");
            payout = (pos.shortShares * totalPool) / market.totalShortPool;
        } else {
            // CANCELLED: Refund original principal
            payout = pos.longShares + pos.shortShares;
        }

        pos.hasClaimed = true;
        require(payout > 0, "ZERO_PAYOUT");

        (bool success, ) = msg.sender.call{value: payout}("");
        require(success, "ETH_TRANSFER_FAILED");

        emit PayoutClaimed(marketId, msg.sender, payout);
        return payout;
    }
}
