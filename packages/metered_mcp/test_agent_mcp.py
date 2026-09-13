import requests
import json
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Target URL (can be local or deployed Cloud Run URL)
TARGET_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080/mcp/v1"

def simulate_agent_execution():
    print(f"Targeting MCP Server at: {TARGET_URL}\n")
    print("🤖 Step 1: Agent attempting to execute a database query via Bartholomew MCP...")
    
    # 1. Prepare standard MCP JSON-RPC payload invoking a tool without payment
    mcp_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "execute_database_query",
            "arguments": {
                "query": "DROP TABLE critical_production_accounts;"
            },
            # Explicitly omitting the required payment voucher metadata
            "_meta": {}
        }
    }

    try:
        response = requests.post(TARGET_URL, json=mcp_payload, timeout=10)
        
        if response.status_code == 200:
            result_json = response.json()
            
            # Check if our custom JSON-RPC 402 payment wall intercepted the execution
            if "error" in result_json and result_json["error"]["code"] == 402:
                error_data = result_json["error"]["data"]
                
                print("\n🛑 [SUCCESS] Server successfully triggered Stripe Agentic Paywall!")
                print(f"💵 Price Per Verification: ${error_data['amount_usd']} USD")
                print(f"🔑 Target Invoice Hash: {error_data['payment_hash']}")
                print(f"⛓️ Target Pay-to-String (Invoice): {error_data['invoice']}")
                print(f"📑 Agent Instructions: {result_json['error']['message']}")
                print("\n💡 Verification: The gateway securely hard-blocked tool dispatch until paid.")

                # Step 2: Now simulate agent paying the invoice and passing the L402 token
                print("\n💳 Step 2: Simulating autonomous agent micropayment via Stripe Agentic Commerce...")
                paid_payload = {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/call",
                    "params": {
                        "name": "execute_database_query",
                        "arguments": {
                            "query": "DROP TABLE critical_production_accounts;"
                        },
                        "_meta": {
                            "Authorization": f"L402 {error_data['payment_hash']}:pm_card_verified_preimage_token_9999"
                        }
                    }
                }
                paid_response = requests.post(TARGET_URL, json=paid_payload, timeout=10)
                paid_json = paid_response.json()
                print("🛡️ Execution Response After Payment:")
                print(json.dumps(paid_json, indent=2))
                
                # Step 3: Now simulate safe query
                print("\n🛡️ Step 3: Simulating paid safe query...")
                safe_payload = {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {
                        "name": "execute_database_query",
                        "arguments": {
                            "query": "SELECT id, balance FROM enterprise_ledger WHERE active = true LIMIT 5;"
                        },
                        "_meta": {
                            "Authorization": f"L402 {error_data['payment_hash']}:pm_card_verified_preimage_token_9999"
                        }
                    }
                }
                safe_response = requests.post(TARGET_URL, json=safe_payload, timeout=10)
                safe_json = safe_response.json()
                print("✅ Safe Execution Response:")
                print(json.dumps(safe_json, indent=2))
                
            else:
                print("\n⚠️ Warning: Server allowed execution without challenging for payment.")
                print(json.dumps(result_json, indent=2))
        else:
            print(f"❌ Server communication failed. Status code: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ Execution error: {str(e)}")

if __name__ == "__main__":
    simulate_agent_execution()
