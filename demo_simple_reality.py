#!/usr/bin/env python3
"""
Zero-Config Developer Experience: 1-Line Import
===============================================
Demonstrates using Bartholomew with zero configuration:
No DIDs, no key management, no policy files, no dashboards.
"""

import sys
import os

sys.path.insert(0, os.path.abspath("pypi_package"))

# The exact 1-line developer experience:
from bartholomew_eval import reality

def run():
    print("=" * 80)
    print("BARTHOLOMEW: 1-LINE ZERO-CONFIG DEVELOPER EXPERIENCE")
    print("=" * 80)

    # 1. Observe
    print("\n[1] reality.observe()")
    state = reality.observe()
    print(f"    -> Accessible nodes: {state['accessible_nodes']}")

    # 2. Act (Blocked action)
    print("\n[2] reality.act('cat /etc/shadow', '/etc/shadow', 'fs:read')")
    r1 = reality.act("cat /etc/shadow", "/etc/shadow", "fs:read")
    print(f"    -> Decision : {r1['decision']}")
    print(f"    -> Reason   : {r1['reason']}")
    print(f"    -> State    : {r1['observed_state']}")

    # 3. Act (Allowed safe action)
    print("\n[3] reality.act('write /workspace/app/config.json', '/workspace/app/config.json', 'fs:write')")
    r2 = reality.act("write /workspace/app/config.json", "/workspace/app/config.json", "fs:write")
    print(f"    -> Decision : {r2['decision']}")
    print(f"    -> Executed : {r2['executed']}")
    print(f"    -> State    : {r2['observed_state']}")

    # 4. Discover
    print("\n[4] reality.discover('test:run')")
    peers = reality.discover("test:run")
    print(f"    -> Available peers: {list(peers['available_peers'].keys())}")

    print("\n" + "=" * 80)
    print("SUCCESS: Pure execution facts returned with zero developer configuration.")
    print("=" * 80)

if __name__ == "__main__":
    run()
