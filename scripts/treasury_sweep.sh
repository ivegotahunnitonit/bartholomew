#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════════════
#  Bartholomew Treasury Sweep — Lightning → Electrum Cold Wallet
#  Runs on the GCP albyhub VM via cron.
#
#  What it does:
#    1. Checks spendable lightning balance via hub-cli
#    2. If balance > SWEEP_THRESHOLD_SATS, initiates a swap-out
#       (lightning → on-chain) to the user's Electrum cold wallet
#    3. Logs every sweep attempt to /opt/albyhub/logs/sweeps.log
#
#  Setup (one-time, on the GCP VM):
#    chmod +x /opt/albyhub/scripts/treasury_sweep.sh
#    crontab -e
#    # Add: 0 0 * * * /opt/albyhub/scripts/treasury_sweep.sh
# ══════════════════════════════════════════════════════════════════

set -euo pipefail

# ── Config ────────────────────────────────────────────────────────
HUB_URL="${HUB_URL:-http://localhost:8029}"
HUB_TOKEN_FILE="${HUB_TOKEN_FILE:-$HOME/.hub-cli/token.jwt}"

# Minimum spendable sats before a sweep fires.
# Keeps a small reserve (5k sats) for routing fees on future invoices.
SWEEP_THRESHOLD_SATS="${SWEEP_THRESHOLD_SATS:-50000}"
RESERVE_SATS="${RESERVE_SATS:-5000}"

# !! IMPORTANT: Set this to your Electrum cold wallet receive address !!
# Generate a fresh address in Electrum: Wallet → Receive → copy address
COLD_WALLET_ADDRESS="${COLD_WALLET_ADDRESS:-}"

LOG_DIR="/opt/albyhub/logs"
LOG_FILE="$LOG_DIR/sweeps.log"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# ── Helpers ───────────────────────────────────────────────────────
log() { mkdir -p "$LOG_DIR"; echo "[$TIMESTAMP] $*" | tee -a "$LOG_FILE"; }
die() { log "ERROR: $*"; exit 1; }

hub_cli() {
  npx -y @getalby/hub-cli@0.6.0 -u "$HUB_URL" "$@"
}

# ── Preflight ─────────────────────────────────────────────────────
[[ -z "$COLD_WALLET_ADDRESS" ]] && die "COLD_WALLET_ADDRESS is not set. Edit this script or export the env var."
[[ ! -f "$HUB_TOKEN_FILE" ]] && die "Hub token not found at $HUB_TOKEN_FILE. Run: hub-cli unlock --save"

log "=== Treasury Sweep Starting ==="

# ── 1. Get balances ───────────────────────────────────────────────
BALANCES_JSON=$(hub_cli get-balances 2>/dev/null) || die "Failed to fetch balances"
LIGHTNING_SATS=$(echo "$BALANCES_JSON" | jq -r '.lightning.totalSpendable // 0' 2>/dev/null) || die "Failed to parse lightning balance"

log "Spendable lightning balance: ${LIGHTNING_SATS} sats"
log "Sweep threshold:             ${SWEEP_THRESHOLD_SATS} sats"

# ── 2. Check threshold ────────────────────────────────────────────
if (( LIGHTNING_SATS < SWEEP_THRESHOLD_SATS )); then
  log "Balance below threshold — no sweep needed. Exiting."
  exit 0
fi

# ── 3. Compute sweep amount (leave reserve) ───────────────────────
SWEEP_AMOUNT=$(( LIGHTNING_SATS - RESERVE_SATS ))
log "Sweeping ${SWEEP_AMOUNT} sats → ${COLD_WALLET_ADDRESS}"

# ── 4. Execute swap-out (lightning → on-chain cold wallet) ────────
SWAP_RESULT=$(hub_cli swap-out --amount "$SWEEP_AMOUNT" --destination "$COLD_WALLET_ADDRESS" 2>&1) || {
  log "Swap-out FAILED: $SWAP_RESULT"
  exit 1
}

SWAP_ID=$(echo "$SWAP_RESULT" | jq -r '.id // "unknown"' 2>/dev/null)
SWAP_STATE=$(echo "$SWAP_RESULT" | jq -r '.state // "unknown"' 2>/dev/null)

log "Swap initiated — ID: ${SWAP_ID} | State: ${SWAP_STATE}"
log "=== Sweep Complete ==="
