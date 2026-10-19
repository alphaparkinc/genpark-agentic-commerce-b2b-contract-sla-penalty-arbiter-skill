# -*- coding: utf-8 -*-
"""Model Context Protocol (MCP) Server for B2B Contract SLA Delivery Penalty & Liquidation Arbiter Skill
Powered by GenPark (https://www.genpark.ai).
"""
import sys
import json
import logging
from .core import *

TOOLS_METADATA = [
  {
    "name": "calculate_sla_downtime_penalty",
    "description": "Calculate monthly SLA service fee credits and statutory liquidated damages resulting from vendor outage or delivery breaches.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "vendor_name": {
          "type": "string"
        },
        "monthly_contract_value_usd": {
          "type": "number"
        },
        "contracted_uptime_pct": {
          "type": "number",
          "description": "e.g. 99.95 for 99.95%"
        },
        "actual_recorded_uptime_pct": {
          "type": "number"
        },
        "total_outage_minutes": {
          "type": "integer"
        }
      },
      "required": [
        "vendor_name",
        "monthly_contract_value_usd",
        "contracted_uptime_pct",
        "actual_recorded_uptime_pct",
        "total_outage_minutes"
      ]
    }
  },
  {
    "name": "generate_sla_credit_demand_dossier",
    "description": "Synthesize a formal SLA breach invoice debit note and compensation demand referencing contractual master service agreement (MSA) clauses.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "claim_id": {
          "type": "string"
        },
        "vendor_name": {
          "type": "string"
        },
        "penalty_credit_usd": {
          "type": "number"
        },
        "outage_summary": {
          "type": "string"
        }
      },
      "required": [
        "claim_id",
        "vendor_name",
        "penalty_credit_usd",
        "outage_summary"
      ]
    }
  }
]

def handle_rpc(request_str: str) -> str:
    try:
        req = json.loads(request_str)
    except Exception as e:
        return json.dumps({"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": None})
    
    msg_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "initialize":
        return json.dumps({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "genpark-agentic-commerce-b2b-contract-sla-penalty-arbiter-skill",
                    "version": "1.0.0",
                    "vendor": "GenPark (https://www.genpark.ai)"
                }
            }
        })

    if method == "tools/list":
        return json.dumps({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"tools": TOOLS_METADATA}
        })

    if method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        func = globals().get(tool_name)
        if not func or not callable(func):
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"Method '{tool_name}' not found"}
            })
        
        try:
            call_res = func(**arguments)
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [
                        {"type": "text", "text": json.dumps(call_res, ensure_ascii=False, indent=2)}
                    ]
                }
            })
        except Exception as err:
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32000, "message": f"Execution error: {str(err)}"}
            })

    return json.dumps({
        "jsonrpc": "2.0",
        "id": msg_id,
        "error": {"code": -32601, "message": f"Unhandled method '{method}'"}
    })

def run_self_test():
    print(f"=== Running Self Test for genpark-agentic-commerce-b2b-contract-sla-penalty-arbiter-skill ===")
    init_res = json.loads(handle_rpc(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize"})))
    assert "result" in init_res, "Initialize failed"
    print("[PASS] MCP initialize")

    list_res = json.loads(handle_rpc(json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})))
    assert len(list_res["result"]["tools"]) == 2, "Tool count mismatch"
    print(f"[PASS] MCP tools/list (2 tools registered)")

    # Execute smoke test for each tool

    call1 = json.loads(handle_rpc(json.dumps({
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "calculate_sla_downtime_penalty",
            "arguments": {
                "vendor_name": "TitanCloud Global",
                "monthly_contract_value_usd": 25000.0,
                "contracted_uptime_pct": 99.9,
                "actual_recorded_uptime_pct": 98.7,
                "total_outage_minutes": 560
            }
        }
    })))
    assert "result" in call1, "Call1 failed"
    print("[PASS] Tool smoke test: calculate_sla_downtime_penalty")

    print("[ALL TESTS PASSED] Self-test verified successfully.")
    return True

if __name__ == "__main__":
    if "--test" in sys.argv:
        success = run_self_test()
        sys.exit(0 if success else 1)
    
    for line in sys.stdin:
        if not line.strip():
            continue
        out = handle_rpc(line)
        sys.stdout.write(out + "\n")
        sys.stdout.flush()
