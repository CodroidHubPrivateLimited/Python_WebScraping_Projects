#!/usr/bin/env bash
set -e

apt-get update
# Try modern package names first; fallback for older images.
apt-get install -y chromium chromium-driver || apt-get install -y chromium-browser
