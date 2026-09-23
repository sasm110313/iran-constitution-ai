#!/usr/bin/env bash
# ==============================================================================
# 🚀 اسکریپت نصب و راه‌اندازی خودکار سامانه حقوقی قانون اساسی بر روی سرور
# دامنه هدف: iran-constitution.acadeo.ir
# ==============================================================================

set -e

DOMAIN="iran-constitution.acadeo.ir"
APP_DIR="/var/www/iran-constitution-ai"
API_KEY="apikey_20341ef74446864ceaa363b376da413038_d070ce2dc3cbca67c6eb2230d791754d859e6122e1d34f7ea465356eda6eb8c4"
REPO_URL="https://github.com/USERNAME/iran-constitution-ai.git" # آدرس مخزن گیت‌هاب شما

echo "=== ۱. بروزرسانی و نصب پیش‌نیازهای سیستم ==="
sudo apt-get update -y
sudo apt-get install -y python3 python3-venv python3-pip git nginx certbot python3-certbot-nginx

echo "=== ۲. آماده‌سازی مسیر پروژه ==="
sudo mkdir -p "$APP_DIR"
sudo chown -R $USER:$USER "$APP_DIR"

if [ -d "$APP_DIR/.git" ]; then
    echo "در حال بروزرسانی سورس کد از گیت‌هاب..."
    cd "$APP_DIR"
    git pull origin main || git pull origin master || true
else
    echo "در حال کلون کردن پروژه..."
    if git clone "$REPO_URL" "$APP_DIR"; then
        cd "$APP_DIR"
    else
        echo "⚠️ اگر مخزن هنوز عمومی نشده است، فایل‌های پروژه را مستقیماً در $APP_DIR کپی کنید."
        cd "$APP_DIR"
    fi
fi

echo "=== ۳. ساخت محیط مجازی پایتون (venv) و نصب پکیج‌ها ==="
python3 -m venv "$APP_DIR/venv"
"$APP_DIR/venv/bin/pip" install --upgrade pip
"$APP_DIR/venv/bin/pip" install flask httpx gunicorn

echo "=== ۴. تنظیم سرویس Systemd (اجرا در پس‌زمینه) ==="
cat <<EOF | sudo tee /etc/systemd/system/iran-constitution.service > /dev/null
[Unit]
Description=Iran Constitution AI Legal Search Engine Service
After=network.target

[Service]
User=$USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
Environment="TYPESAFE_API_KEY=$API_KEY"
Environment="SERVER_MODE=1"
ExecStart=$APP_DIR/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 app:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable iran-constitution
sudo systemctl restart iran-constitution

echo "=== ۵. تنظیم کانفیگ Nginx ویژه دامنه $DOMAIN ==="
cat <<EOF | sudo tee /etc/nginx/sites-available/$DOMAIN > /dev/null
server {
    listen 80;
    server_name $DOMAIN;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# فعال‌سازی کانفیگ بدون آسیب به سایر سایت‌ها
sudo ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

echo "=== ۶. دریافت گواهی امنیتی SSL (Certbot) ==="
if command -v certbot &> /dev/null; then
    sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos --register-unsafely-without-email || echo "⚠️ دریافت گواهی SSL نیازمند ست بودن دقیق DNS دامنه می‌باشد."
fi

echo "=========================================================="
echo "✅ نصب و راه‌اندازی با موفقیت انجام شد!"
echo "🌐 آدرس دامنه: https://$DOMAIN"
echo "=========================================================="
