"""
MCP Server for Respiratory Inertance & Dynamic Compliance Skill.
Exposes JSON-RPC Model Context Protocol tools for assessing respiratory mechanics, Work of Breathing (WOB), and resonant frequency.
"""

import sys
import json
from typing import Dict, Any
from client import RespiratoryInertanceComplianceClient


def get_tools_manifest() -> Dict[str, Any]:
    return {
        "tools": [
            {
                "name": "evaluate_respiratory_mechanics",
                "description": "Calculates respiratory inertance, dynamic compliance, total Work of Breathing (WOB in J/L), and resonant frequency (f0).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "dynamic_compliance_l_cmh2o": {
                            "type": "number",
                            "description": "Dynamic lung compliance in L/cmH2O (typically 0.050 - 0.100 L/cmH2O)."
                        },
                        "airway_resistance_cmh2o_s_l": {
                            "type": "number",
                            "description": "Total airway resistance in cmH2O*s/L (typically 1.8 - 3.8 cmH2O*s/L)."
                        },
                        "inertance_cmh2o_s2_l": {
                            "type": "number",
                            "description": "Respiratory gas inertance in cmH2O*s^2/L (typically 0.008 - 0.020).",
                            "default": 0.012
                        },
                        "breathing_frequency_bpm": {
                            "type": "number",
                            "description": "Respiratory rate in breaths per minute (e.g. 14.0 bpm).",
                            "default": 14.0
                        },
                        "tidal_volume_l": {
                            "type": "number",
                            "description": "Tidal breath volume in liters (e.g. 0.55 L).",
                            "default": 0.55
                        }
                    },
                    "required": ["dynamic_compliance_l_cmh2o", "airway_resistance_cmh2o_s_l"]
                }
            }
        ]
    }


def handle_request(client: RespiratoryInertanceComplianceClient, req: Dict[str, Any]) -> Dict[str, Any]:
    method = req.get("method")
    params = req.get("params", {})
    req_id = req.get("id")

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": get_tools_manifest()
        }
    elif method == "tools/call":
        name = params.get("name")
        args = params.get("arguments", {})

        if name == "evaluate_respiratory_mechanics":
            res = client.evaluate_respiratory_mechanics(
                dynamic_compliance_l_cmh2o=float(args.get("dynamic_compliance_l_cmh2o", 0.070)),
                airway_resistance_cmh2o_s_l=float(args.get("airway_resistance_cmh2o_s_l", 2.5)),
                inertance_cmh2o_s2_l=float(args.get("inertance_cmh2o_s2_l", 0.012)),
                breathing_frequency_bpm=float(args.get("breathing_frequency_bpm", 14.0)),
                tidal_volume_l=float(args.get("tidal_volume_l", 0.55))
            )
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(res, indent=2)
                        }
                    ]
                }
            }
        else:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": f"Method {name} not found"
                }
            }
    else:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {
                "code": -32600,
                "message": "Invalid request"
            }
        }


def main():
    client = RespiratoryInertanceComplianceClient()
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            resp = handle_request(client, req)
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": str(e)}
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
