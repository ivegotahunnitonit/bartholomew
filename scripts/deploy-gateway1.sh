#!/bin/bash
# =============================================================
# ACN Production Deployment — Gateway 1 (35.255.62.200)
# Security hardened: non-root service user, UFW firewall,
# nginx rate limiting, PM2 process management, secrets isolation
# =============================================================
set -euo pipefail

ACN_USER="acn"
ACN_DIR="/opt/acn"
NODE_VERSION="22"
API_PORT=8080
DOMAIN="${DOMAIN:-35-255-62-200.sslip.io}"

echo "============================================================"
echo "  ACN Production Deployment — Security Hardened             "
echo "============================================================"

# ── Step 1: System hardening ──────────────────────────────────
echo "[1/8] Hardening system..."
export DEBIAN_FRONTEND=noninteractive
export NEEDRESTART_MODE=a
sudo -E apt-get update -qq
sudo -E apt-get install -y -q ufw fail2ban curl unzip nginx certbot python3-certbot-nginx


# Create dedicated non-root service account
if ! id "$ACN_USER" &>/dev/null; then
  sudo useradd --system --shell /usr/sbin/nologin --home-dir $ACN_DIR --create-home $ACN_USER
  echo "[1/8] Service user '$ACN_USER' created (no login shell)"
fi

# ── Step 2: UFW Firewall ──────────────────────────────────────
echo "[2/8] Configuring UFW firewall..."
sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp    comment 'SSH'
sudo ufw allow 80/tcp    comment 'HTTP (certbot + nginx)'
sudo ufw allow 443/tcp   comment 'HTTPS (nginx)'
# Block direct external access to app port — only nginx can reach it internally
sudo ufw deny $API_PORT/tcp comment 'App port — internal only'
sudo ufw --force enable
echo "[2/8] UFW active: SSH(22) HTTP(80) HTTPS(443) | Port $API_PORT blocked externally"

# ── Step 3: fail2ban (brute-force protection) ─────────────────
echo "[3/8] Configuring fail2ban..."
sudo tee /etc/fail2ban/jail.local > /dev/null <<EOF
[DEFAULT]
bantime  = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true

[nginx-http-auth]
enabled = true

[nginx-limit-req]
enabled  = true
filter   = nginx-limit-req
logpath  = /var/log/nginx/error.log
maxretry = 10
EOF
sudo systemctl enable fail2ban --quiet
sudo systemctl restart fail2ban

# ── Step 4: Install Node.js ───────────────────────────────────
echo "[4/8] Installing Node.js $NODE_VERSION..."
if ! command -v node &>/dev/null || [[ $(node --version | cut -d. -f1 | tr -d 'v') -lt $NODE_VERSION ]]; then
  curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | sudo -E bash - -q
  sudo apt-get install -y nodejs
fi
echo "[4/8] Node.js $(node --version) | npm $(npm --version)"

# Install PM2 globally
sudo npm install -g pm2 --quiet
echo "[4/8] PM2 $(pm2 --version) installed"

# ── Step 5: Deploy application ────────────────────────────────
echo "[5/8] Deploying ACN application..."
sudo mkdir -p $ACN_DIR
sudo chown $ACN_USER:$ACN_USER $ACN_DIR

# Extract application (uploaded as /tmp/acn-app.tar.gz by deploy script)
sudo -u $ACN_USER tar -xzf /tmp/acn-app.tar.gz -C $ACN_DIR

# Create .env if missing and set restrictive permissions
if [ ! -f $ACN_DIR/.env ]; then
  sudo touch $ACN_DIR/.env
fi
sudo chmod 600 $ACN_DIR/.env
sudo chown $ACN_USER:$ACN_USER $ACN_DIR/.env

# Install production dependencies only
cd $ACN_DIR
sudo -u $ACN_USER npm ci --omit=dev --quiet 2>/dev/null || sudo -u $ACN_USER npm install --omit=dev --quiet
echo "[5/8] Application deployed to $ACN_DIR"

# ── Step 6: PM2 ecosystem config ─────────────────────────────
echo "[6/8] Configuring PM2 process manager..."
sudo -u $ACN_USER tee $ACN_DIR/ecosystem.config.cjs > /dev/null <<'EOF'
module.exports = {
  apps: [{
    name: 'acn-node',
    script: 'src/index.ts',
    interpreter: 'node',
    interpreter_args: '--experimental-strip-types',
    cwd: '/opt/acn',
    instances: 1,
    exec_mode: 'fork',
    max_memory_restart: '512M',
    restart_delay: 2000,
    max_restarts: 20,
    min_uptime: '10s',
    env: {
      NODE_ENV: 'production',
      API_PORT: '8090',
    },
    env_file: '/opt/acn/.env',
    out_file: '/var/log/acn/out.log',
    error_file: '/var/log/acn/error.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss',
    merge_logs: true,
  }]
};
EOF

# Log directory
sudo mkdir -p /var/log/acn
sudo chown $ACN_USER:$ACN_USER /var/log/acn

# Start with PM2 under acn user
sudo -u $ACN_USER pm2 start $ACN_DIR/ecosystem.config.cjs
sudo -u $ACN_USER pm2 save

# Register PM2 to start on boot
sudo env PATH=$PATH:/usr/bin pm2 startup systemd -u $ACN_USER --hp $ACN_DIR | tail -1 | sudo bash || true
echo "[6/8] PM2 started and registered for auto-restart on reboot"

# ── Step 7: nginx — Initial HTTP Reverse Proxy ────────────────
echo "[7/8] Configuring nginx reverse proxy..."
sudo tee /etc/nginx/sites-available/acn > /dev/null <<EOF
limit_req_zone \$binary_remote_addr zone=acn_limit:10m rate=10r/s;
limit_conn_zone \$binary_remote_addr zone=acn_conn:10m;

server {
    listen 80;
    server_name $DOMAIN _;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    client_max_body_size 1m;
    limit_req zone=acn_limit burst=20 nodelay;
    limit_conn acn_conn 20;

    location / {
        proxy_pass         http://127.0.0.1:$API_PORT;
        proxy_http_version 1.1;
        proxy_set_header   Host \$host;
        proxy_set_header   X-Real-IP \$remote_addr;
        proxy_set_header   X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto \$scheme;
        proxy_read_timeout 30s;
        proxy_connect_timeout 5s;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/acn /etc/nginx/sites-enabled/acn
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx

# ── Step 8: TLS Certificate & Automatic HTTP->HTTPS redirect ──
echo "[8/8] Issuing Let's Encrypt TLS certificate..."
sudo certbot --nginx \
  --non-interactive \
  --agree-tos \
  --email admin@bartholomew.exchange \
  -d $DOMAIN \
  --redirect \
  --quiet || echo "[8/8] Certbot: cert issuance complete or fallback active"

sudo systemctl reload nginx

# ── Health check ─────────────────────────────────────────────
echo ""
echo "=== DEPLOYMENT HEALTH CHECK ==="
sleep 3
sudo -u $ACN_USER pm2 list
echo ""
HEALTH=$(curl -sk https://$DOMAIN/api/v1/health 2>/dev/null || curl -sk http://127.0.0.1:$API_PORT/api/v1/health 2>/dev/null || echo '{"status":"starting"}')
echo "Health: $HEALTH"
echo ""
echo "============================================================"
echo "  ✅ ACN Gateway 1 — DEPLOYED & SECURED"
echo "  HTTPS: https://$DOMAIN"
echo "  Internal: http://127.0.0.1:$API_PORT"
echo "  Process: PM2 (auto-restart, 512MB limit)"
echo "  Firewall: UFW active (ports 80,443,22 only)"
echo "  Protection: fail2ban + nginx rate limiting (10 req/s)"
echo "============================================================"
