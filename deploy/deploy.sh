#!/usr/bin/env bash
# Pull latest code, install deps, migrate, collect static, restart gunicorn.
# Run as root (e.g. `sudo deploy.sh staging`): the repo + Python steps are
# executed as $APP_USER, only the service restart needs root.
# Usage:  ./deploy/deploy.sh prod   |   ./deploy/deploy.sh staging
set -euo pipefail

ENV="${1:?Usage: deploy.sh <prod|staging>}"
APP_USER="${APP_USER:-hub}"
case "$ENV" in
  prod)    ROOT=/var/www/borderless-hub-app-backend-prod;    SERVICE=gunicorn-hub-prod ;;
  staging) ROOT=/var/www/borderless-hub-app-backend-test;    SERVICE=gunicorn-hub-staging ;;
  *) echo "Unknown env: $ENV (use prod|staging)"; exit 1 ;;
esac

APP="$ROOT"
VENV="$ROOT/venv"

run() { sudo -u "$APP_USER" "$@"; }

echo ">> Deploying $ENV from $APP (as $APP_USER)"
run git -C "$APP" pull --ff-only
run "$VENV/bin/pip" install -r "$APP/requirements.txt"
run "$VENV/bin/python" "$APP/manage.py" migrate --noinput
run "$VENV/bin/python" "$APP/manage.py" collectstatic --noinput
systemctl restart "$SERVICE"
echo ">> Done. $(systemctl is-active "$SERVICE")"
