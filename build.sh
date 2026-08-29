#!/usr/bin/env bash
# ──────────────────────────────────────────────
# Build Script — Run locally BEFORE deploying to Vercel
# ──────────────────────────────────────────────
# This script collects static files and runs migrations.
#
# Usage (from the backend/ directory):
#   chmod +x build.sh && ./build.sh
#
# After running, commit the staticfiles/ directory so Vercel
# can bundle them into the serverless function.
# ──────────────────────────────────────────────
set -o errexit

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "📁 Collecting static files..."
python manage.py collectstatic --no-input

echo "🗄️  Running migrations..."
python manage.py migrate

echo "✅ Build complete! Don't forget to commit staticfiles/"
