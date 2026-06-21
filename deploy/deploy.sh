#!/usr/bin/env bash
# Pull latest code, install deps, migrate, collect static, restart gunicorn.
# Usage:  ./deploy/deploy.sh prod   |   ./deploy/deploy.sh staging
set -euo pipefail

ENV="${1:?Usage: deploy.sh <prod|staging>}"
case "$ENV" in
  prod)    ROOT=/var/www/borderless-hub-app-backend-prod;    SERVICE=gunicorn-hub-prod ;;
  staging) ROOT=/var/www/borderless-hub-app-backend-test; SERVICE=gunicorn-hub-staging ;;
  *) echo "Unknown env: $ENV (use prod|staging)"; exit 1 ;;
esac

APP="$ROOT/hub-app-backend"
PY="$ROOT/venv/bin/python"
PIP="$ROOT/venv/bin/pip"

echo ">> Deploying $ENV from $APP"
cd "$APP"
git pull --ff-only
"$PIP" install -r requirements.txt
"$PY" manage.py migrate --noinput
"$PY" manage.py collectstatic --noinput
sudo systemctl restart "$SERVICE"
echo ">> Done. $(systemctl is-active "$SERVICE")"
