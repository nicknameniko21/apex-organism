#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "[APEX] Preparing Android one-click start..."
pkg update -y >/dev/null
pkg install -y python git openssl clang libsqlite python-pip >/dev/null

python -m pip install --upgrade pip >/dev/null
python -m pip install -r requirements.txt >/dev/null

if [ ! -f config.yaml ] && [ -f config.yaml.example ]; then
  cp config.yaml.example config.yaml
fi

nohup python apex_main.py --dashboard >/dev/null 2>&1 &
sleep 3

if command -v termux-open-url >/dev/null 2>&1; then
  termux-open-url http://127.0.0.1:8080
fi

wait
