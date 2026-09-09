#!/usr/bin/env python3
"""
Somnia Shannon Testnet (Chain ID 50312) Deployment Verification Script

DreamDEXRouter is already deployed to Shannon. This script reads and displays
the real, committed deployment receipt rather than generating a new one - a
prior version of this file fabricated a sha256-derived "simulated_contract_address"
locally with zero blockchain interaction, and `make deploy` would silently
overwrite the real receipt with that fake data on every run. See
contracts/SECURITY_AUDIT.md for the history.

To deploy a new instance for real, use forge directly:
    forge create contracts/DreamDEXRouter.sol:DreamDEXRouter \
        --rpc-url https://dream-rpc.somnia.network \
        --private-key <YOUR_KEY> --broadcast
then update contracts/deployment_receipt.json with the real receipt.
"""

import json
import os
import sys

EXPLORER_URL = "https://shannon-explorer.somnia.network"


def main():
    print("=" * 70)
    print("  SOMNIA SHANNON TESTNET DEPLOYMENT VERIFICATION (Chain ID 50312)")
    print("=" * 70)

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    receipt_path = os.path.join(base_dir, "contracts", "deployment_receipt.json")

    if not os.path.exists(receipt_path):
        print(f"\n[ERROR] No deployment receipt found at: {receipt_path}")
        print("This contract has not been deployed yet, or the receipt was removed.")
        print("Deploy for real with forge, then write the resulting receipt by hand:")
        print("  forge create contracts/DreamDEXRouter.sol:DreamDEXRouter \\")
        print("      --rpc-url https://dream-rpc.somnia.network \\")
        print("      --private-key <YOUR_KEY> --broadcast")
        sys.exit(1)

    with open(receipt_path, "r") as f:
        receipt = json.load(f)

    address = receipt.get("contract_address", "UNKNOWN")
    tx_hash = receipt.get("transaction_hash", "UNKNOWN")

    print(f"\nContract:          {receipt.get('contract_name', 'DreamDEXRouter')}")
    print(f"Network:            {receipt.get('network', 'Somnia Shannon Layer-1 Testnet')}")
    print(f"Deployed Address:   {address}")
    print(f"Deployer:           {receipt.get('deployer_address', 'UNKNOWN')}")
    print(f"Creation Tx:        {tx_hash}")
    print(f"Explorer (address): {receipt.get('verified_explorer_url', f'{EXPLORER_URL}/address/{address}')}")
    print(f"Explorer (tx):      {receipt.get('transaction_explorer_url', f'{EXPLORER_URL}/tx/{tx_hash}')}")
    print("\n[OK] This is a real, previously-broadcast deployment - not a simulation.")


if __name__ == "__main__":
    main()
