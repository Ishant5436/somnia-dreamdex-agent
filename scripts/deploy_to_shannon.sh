#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$ROOT_DIR/.deployer.env"
RPC_URL="https://dream-rpc.somnia.network"
EXPLORER_URL="https://shannon-explorer.somnia.network"
CHAIN_ID="50312"

if [ ! -f "$ENV_FILE" ]; then
    echo "[-] Error: $ENV_FILE does not exist. Run wallet generation first."
    exit 1
fi

DEPLOYER_ADDRESS=$(grep "Address:" "$ENV_FILE" | awk '{print $2}')
PRIVATE_KEY=$(grep -i "Private key:" "$ENV_FILE" | awk '{print $3}')

echo "=============================================================================="
echo "          SOMNIA SHANNON TESTNET ON-CHAIN CONTRACT DEPLOYMENT ENGINE          "
echo "=============================================================================="
echo "• Network          : Somnia Shannon Layer-1 Testnet (Chain ID $CHAIN_ID)"
echo "• RPC URL          : $RPC_URL"
echo "• Explorer         : $EXPLORER_URL"
echo "• Deployer Wallet  : $DEPLOYER_ADDRESS"
echo ""

echo "[1/3] Checking testnet STT gas balance..."
BALANCE_WEI=$(cast balance "$DEPLOYER_ADDRESS" --rpc-url "$RPC_URL" 2>/dev/null || echo "0")

if [ "$BALANCE_WEI" = "0" ] || [ -z "$BALANCE_WEI" ]; then
    echo "[-] Balance is 0 STT. Gas is required to deploy to Somnia Shannon."
    echo ""
    echo "👉 Please claim free testnet STT tokens for this address:"
    echo "   Wallet: $DEPLOYER_ADDRESS"
    echo "   Faucet: https://testnet.somnia.network/ or Discord (#dev-chat)"
    echo ""
    echo "Once tokens arrive, re-run this script: bash scripts/deploy_to_shannon.sh"
    exit 1
fi

echo "[SUCCESS] Gas detected: $BALANCE_WEI wei STT available."
echo ""
echo "[2/3] Compiling and deploying DreamDEXRouter.sol via Foundry..."
DEPLOY_OUTPUT=$(forge create "$ROOT_DIR/contracts/DreamDEXRouter.sol:DreamDEXRouter" \
    --rpc-url "$RPC_URL" \
    --private-key "$PRIVATE_KEY" \
    --json)

CONTRACT_ADDR=$(echo "$DEPLOY_OUTPUT" | jq -r '.deployedTo // empty')
TX_HASH=$(echo "$DEPLOY_OUTPUT" | jq -r '.transactionHash // empty')

if [ -z "$CONTRACT_ADDR" ]; then
    echo "[-] Deployment failed. Output:"
    echo "$DEPLOY_OUTPUT"
    exit 1
fi

echo "[SUCCESS] Deployed Contract Address: $CONTRACT_ADDR"
echo "[SUCCESS] Transaction Hash:          $TX_HASH"
echo ""

echo "[3/3] Updating deployment receipt with on-chain metadata..."
RECEIPT_FILE="$ROOT_DIR/contracts/deployment_receipt.json"

cat <<RECEIPT_EOF > "$RECEIPT_FILE"
{
  "network": "Somnia Shannon Layer-1 Testnet",
  "chain_id": $CHAIN_ID,
  "contract_name": "DreamDEXRouter",
  "contract_address": "$CONTRACT_ADDR",
  "deployer_address": "$DEPLOYER_ADDRESS",
  "transaction_hash": "$TX_HASH",
  "solidity_version": "^0.8.20",
  "optimization": true,
  "runs": 200,
  "invariants": {
    "reentrancy_guard": "Single-Slot Mutex Lock (slot _status)",
    "fee_accounting": "Segregated totalProtocolFees accumulator (20 BPS)",
    "oracle_settlement": "Atomic owner/oracle binary state resolution",
    "payout_math": "Proportional pari-mutuel payout distribution"
  },
  "verified_explorer_url": "$EXPLORER_URL/address/$CONTRACT_ADDR",
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
RECEIPT_EOF

echo "[SUCCESS] Deployment receipt saved to $RECEIPT_FILE"
echo "Explorer Verification Link: $EXPLORER_URL/address/$CONTRACT_ADDR"
echo "=============================================================================="
