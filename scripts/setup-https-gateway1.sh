#!/bin/bash
# ACN HTTPS Setup — Gateway 1 (35.255.62.200)
# Uses sslip.io free DNS: 35-255-62-200.sslip.io -> 35.255.62.200
# Let's Encrypt issues a real trusted TLS cert for this domain.

set -e

DOMAIN="35-255-62-200.sslip.io"
EMAIL="admin@bartholomew.exchange"
ACN_PORT=8090

echo "=== [1/4] Installing nginx + certbot ==="
sudo apt-get update -qq
sudo apt-get install -y nginx certbot python3-certbot-nginx

echo "=== [2/4] Writing nginx reverse-proxy config ==="
sudo tee /etc/nginx/sites-available/acn <<EOF
server {
    listen 80;
    server_name $DOMAIN;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        proxy_pass http://127.0.0.1:$ACN_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_read_timeout 30s;
        proxy_connect_timeout 5s;
        # Security
        proxy_hide_header X-Powered-By;
        add_header Strict-Transport-Security "max-age=31536000" always;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/acn /etc/nginx/sites-enabled/acn
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx

echo "=== [3/4] Issuing Let's Encrypt TLS certificate ==="
sudo certbot --nginx \
  --non-interactive \
  --agree-tos \
  --email $EMAIL \
  -d $DOMAIN \
  --redirect

echo "=== [4/4] Verifying HTTPS endpoint ==="
curl -sI https://$DOMAIN/api/v1/health | head -5

echo ""
echo "==================================================="
echo "  HTTPS LIVE: https://$DOMAIN"
echo "  All traffic encrypted. Real trusted TLS cert."
echo "==================================================="
