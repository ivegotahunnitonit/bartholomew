gcloud compute scp "C:\Users\User\.gemini\antigravity-ide\brain\6cf891cf-9b1e-41d8-b43d-556f8ef27ef7\store_token.sh" acn-supernode-gateway:store_token.sh --zone=us-central1-a

gcloud compute ssh acn-supernode-gateway --zone=us-central1-a --command="chmod +x store_token.sh && ./store_token.sh"

# Remove any leaked GitHub tokens

gcloud compute scp "C:\Users\User\.gemini\antigravity-ide\brain\6cf891cf-9b1e-41d8-b43d-556f8ef27ef7\remove_leaked_tokens.sh" acn-supernode-gateway:remove_leaked_tokens.sh --zone=us-central1-a

gcloud compute ssh acn-supernode-gateway --zone=us-central1-a --command="chmod +x remove_leaked_tokens.sh && ./remove_leaked_tokens.sh"

# Audit bounty ledger

gcloud compute scp "C:\Users\User\.gemini\antigravity-ide\brain\6cf891cf-9b1e-41d8-b43d-556f8ef27ef7\audit_bounty.py" acn-supernode-gateway:audit_bounty.py --zone=us-central1-a

gcloud compute ssh acn-supernode-gateway --zone=us-central1-a --command="python3 ./audit_bounty.py"

# Run existing tasks in parallel

gcloud compute scp "C:\Users\User\.gemini\antigravity-ide\brain\6cf891cf-9b1e-41d8-b43d-556f8ef27ef7\parallelize_tasks.sh" acn-supernode-gateway:parallelize_tasks.sh --zone=us-central1-a

gcloud compute ssh acn-supernode-gateway --zone=us-central1-a --command="chmod +x parallelize_tasks.sh && ./parallelize_tasks.sh"
