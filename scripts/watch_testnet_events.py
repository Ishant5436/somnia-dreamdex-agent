#!/usr/bin/env python3
"""
Somnia Shannon Testnet Live Settlement & Event Telemetry Daemon
Monitors DreamDEXRouter (0x8a0f48e912f3e66a57487c3482cc80e56674a678)
on Somnia Shannon Layer-1 Testnet (Chain ID 50312).
"""

import sys
import os
import time
import json
import urllib.request
import urllib.error

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.agent_bot import DreamDEXAgent
from src.indicators import ParkinsonVolatility, SlidingMonotonicExtremum

RPC_URL = "https://dream-rpc.somnia.network"
CONTRACT_ADDRESS = "0x8a0f48e912f3e66a57487c3482cc80e56674a678"
CHAIN_ID = 50312


def rpc_call(method: str, params: list = None, timeout: float = 3.0) -> dict:
    """Execute raw JSON-RPC query against Somnia Shannon RPC."""
    payload = json.dumps({
        "jsonrpc": "2.0",
        "method": method,
        "params": params or [],
        "id": 1
    }).encode("utf-8")
    
    req = urllib.request.Request(
        RPC_URL,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "DreamDEX-Agent/1.0"}
    )
    
    try:
        t0 = time.time()
        with urllib.request.urlopen(req, timeout=timeout) as response:
            t1 = time.time()
            data = json.loads(response.read().decode("utf-8"))
            data["latency_ms"] = round((t1 - t0) * 1000.0, 2)
            return data
    except Exception as e:
        return {"error": str(e), "latency_ms": 0.0}


def probe_somnia_testnet() -> dict:
    """Probes Somnia Shannon Testnet block height, chain ID, and contract state."""
    block_res = rpc_call("eth_blockNumber")
    block_num = int(block_res.get("result", "0x0"), 16) if "result" in block_res else None

    code_res = rpc_call("eth_getCode", [CONTRACT_ADDRESS, "latest"])
    has_code = "result" in code_res and len(code_res["result"]) > 2

    # Initialize Parkinson Volatility & Agent
    agent = DreamDEXAgent(agent_address=CONTRACT_ADDRESS, rpc_url=RPC_URL)
    pv = ParkinsonVolatility(window_size=15)
    
    # Simulate current BTC/USD high-low volatility
    vol_bps = pv.volatility_bps(high=78450.0, low=77900.0)
    decision = agent.evaluate_event_contract(
        market_title="BTC Breakout > $78,000",
        current_vol_bps=vol_bps,
        trend_signal=0.55
    )

    telemetry = {
        "network": "Somnia Shannon Layer-1 Testnet",
        "chain_id": CHAIN_ID,
        "contract_address": CONTRACT_ADDRESS,
        "block_height": block_num,
        "contract_verified": has_code,
        "rpc_latency_ms": block_res.get("latency_ms", 0.0),
        "realized_volatility_bps": round(vol_bps, 2),
        "active_decision": decision,
        "timestamp": int(time.time()),
        "status": "HEALTHY" if has_code else "RPC_FALLBACK"
    }
    return telemetry


if __name__ == "__main__":
    print("[SOMNIA] Probing Shannon Layer-1 Testnet...")
    telemetry = probe_somnia_testnet()
    print(json.dumps(telemetry, indent=2))
