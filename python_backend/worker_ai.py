import time
import requests
import uuid
import random
import os

API_BASE = os.getenv("API_BASE", "https://acn-fastapi-backend-444129982305.us-central1.run.app")
NODE_ID = "SUPER_AI_WORKER_" + str(uuid.uuid4())[:8]

def register():
    try:
        requests.post(f"{API_BASE}/api/nodes/start", json={"node_id": NODE_ID}, timeout=5)
    except Exception as e:
        print(f"[Worker Start Error]: {e}")

def get_marketplace():
    try:
        res = requests.get(f"{API_BASE}/api/marketplace", timeout=5)
        return res.json() if res.ok else []
    except Exception as e:
        print(f"[Marketplace Fetch Error]: {e}")
        return []

def bid(task):
    score = round(random.uniform(7.5, 9.9), 2)
    try:
        requests.post(
            f"{API_BASE}/api/marketplace/bid",
            json={"task_id": task["id"], "bid": {"node": NODE_ID, "score": score}},
            timeout=5
        )
    except Exception as e:
        print(f"[Bid Error]: {e}")

def assign(task_id):
    try:
        requests.post(f"{API_BASE}/api/marketplace/assign", json={"task_id": task_id}, timeout=5)
    except Exception as e:
        print(f"[Assign Error]: {e}")

def run(task_id):
    try:
        res = requests.post(f"{API_BASE}/api/worker/run", json={"task_id": task_id}, timeout=5)
        if res.ok:
            data = res.json()
            print(f"[SUCCESS] AI Worker Executed Task '{task_id}'! Earned: ${data.get('earned', 0.0)} USD")
    except Exception as e:
        print(f"[Run Error]: {e}")

def create_sample_task():
    types = ["gpu", "compute", "docker", "wasm", "automation"]
    task_type = random.choice(types)
    try:
        requests.post(
            f"{API_BASE}/api/tasks/create",
            json={"name": f"AI Autonomous {task_type.upper()} Job", "type": task_type, "complexity": 2.0},
            timeout=5
        )
    except Exception as e:
        print(f"[Task Create Error]: {e}")

def main():
    print(f"[AI WORKER ENGINE] Started! Node ID: {NODE_ID}")
    register()
    
    # Run continuous earnings loop
    for cycle in range(5):
        create_sample_task()
        tasks = get_marketplace()

        for t in tasks:
            if isinstance(t, dict) and t.get("status") == "open":
                task_id = t.get("id")
                if task_id:
                    bid(t)
                    assign(task_id)
                    run(task_id)

        time.sleep(1)

if __name__ == "__main__":
    main()
