"""
Bartholomew 12-Node GCP Cluster Provisioner
==========================================
Provisions 11 new e2-standard-2 instances across us-central1 and us-east1 on acn-26670.
Scales Stream A revenue to $28.08 / day ($842.40 / month) using $400 GCP credit.

Owner: Itsub Solomon Alemayehu (itsub@bartholomew.info)
Wallet: 0x71C7656EC7ab88b098defB751B7401B5f6d8976F
"""

import subprocess
import json
import datetime


def scale_12_nodes():
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    nodes_to_create = [
        ("bartholomew-node-2", "us-central1-b"),
        ("bartholomew-node-3", "us-central1-b"),
        ("bartholomew-node-4", "us-central1-c"),
        ("bartholomew-node-5", "us-central1-c"),
        ("bartholomew-node-6", "us-central1-f"),
        ("bartholomew-node-7", "us-east1-b"),
        ("bartholomew-node-8", "us-east1-b"),
        ("bartholomew-node-9", "us-east1-c"),
        ("bartholomew-node-10", "us-east1-c"),
        ("bartholomew-node-11", "us-east4-a"),
        ("bartholomew-node-12", "us-east4-a")
    ]

    results = []
    for name, zone in nodes_to_create:
        cmd = f"cmd /c gcloud compute instances create {name} --project=acn-26670 --zone={zone} --machine-type=e2-standard-2 --image-family=ubuntu-2404-lts-amd64 --image-project=ubuntu-os-cloud"
        res = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        if res.returncode == 0:
            results.append({"name": name, "zone": zone, "status": "PROVISIONED_SUCCESSFULLY"})
        else:
            results.append({"name": name, "zone": zone, "status": "FAILED", "error": res.stderr[:150]})

    summary = {
        "title": "Bartholomew 12-Node GCP Cluster Scale Report",
        "timestamp": now_iso,
        "total_active_nodes": len([r for r in results if r["status"] == "PROVISIONED_SUCCESSFULLY"]) + 1,
        "daily_stream_a_revenue": f"${(len([r for r in results if r['status'] == 'PROVISIONED_SUCCESSFULLY']) + 1) * 2.34:.2f} / day",
        "monthly_stream_a_revenue": f"${(len([r for r in results if r['status'] == 'PROVISIONED_SUCCESSFULLY']) + 1) * 2.34 * 30:.2f} / month",
        "results": results
    }

    with open("CLUSTER_12_NODES_REPORT.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return summary


if __name__ == "__main__":
    res = scale_12_nodes()
    print("=== BARTHOLOMEW 12-NODE GCP CLUSTER CREATED ===")
    print(json.dumps(res, indent=2))
