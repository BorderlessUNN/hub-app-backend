# Deployment Guide — Borderless Hub API

Two environments on one Ubuntu VPS, behind nginx + Cloudflare:

| Env        | Domain                              | Gunicorn | DB                       | Path                  |
|------------|-------------------------------------|----------|--------------------------|-----------------------|
| Production | `api.hub.borderlessunn.xyz`         | :8001    | `borderless_hub_prod_db` | `/srv/hub/prod`       |
| Staging    | `api.test.hub.borderlessunn.xyz`    | :8002    | `borderless_hub_test_db` | `/srv/hub/staging`    |

Stack: Django 5.2 (WSGI) → Gunicorn → nginx → Cloudflare. Python 3.12.

---

## 1. Cloudflare DNS

In the Cloudflare dashboard for `borderlessunn.xyz`, add two **A records** pointing at the VPS IP:

| Type | Name                     | Content (VPS IP) | Proxy        |
|------|--------------------------|------------------|--------------|
| A    | `api.hub`                | `<VPS_IP>`       | DNS only \*  |
| A    | `api.test.hub`           | `<VPS_IP>`       | DNS only \*  |

\* Set proxy to **DNS only (grey cloud)** until certbot has issued certs, then
you may switch to **Proxied (orange)**. If you proxy, set SSL/TLS mode to
**Full (strict)** so Cloudflare ↔ origin stays encrypted with the Let's Encrypt cert.

---

## 2. Server prerequisites (once)

```bash
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3-pip \
    postgresql postgresql-contrib nginx git certbot python3-certbot-nginx

# dedicated unprivileged user to own the app
sudo adduser --system --group --home /srv/hub hub
sudo mkdir -p /srv/hub/prod /srv/hub/staging
sudo chown -R hub:hub /srv/hub
```

---

## 3. PostgreSQL: databases + users

Edit the two passwords in `deploy/postgres-setup.sql`, then:

```bash
sudo -u postgres psql -f deploy/postgres-setup.sql
```

This creates:
- `borderless_hub_prod_user` owning `borderless_hub_prod_db`
- `borderless_hub_test_user` owning `borderless_hub_test_db`

(Default `pg_hba.conf` uses `md5`/`scram` for local TCP, so the app connects over
`localhost:5432` with the password from `.env` — no extra config needed.)

Verify:
```bash
psql "postgresql://borderless_hub_prod_user:<pw>@localhost:5432/borderless_hub_prod_db" -c '\conninfo'
```

---

## 4. Clone code + virtualenv (per environment)

Run for **prod** then repeat for **staging** (swap `prod`→`staging`):

```bash
sudo -u hub -H bash
cd /srv/hub/prod
git clone <REPO_URL> hub-app-backend
python3.12 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r hub-app-backend/requirements.txt
exit
```

---

## 5. Environment file (per environment)

```bash
# production
sudo -u hub cp /srv/hub/prod/hub-app-backend/.env.production.example \
               /srv/hub/prod/hub-app-backend/.env
# staging
sudo -u hub cp /srv/hub/staging/hub-app-backend/.env.staging.example \
               /srv/hub/staging/hub-app-backend/.env
```

Fill each `.env`. Generate a unique `SECRET_KEY` per env:

```bash
/srv/hub/prod/venv/bin/python -c \
  "from django.core.management.utils import get_random_secret_key as g; print(g())"
```

Set `DATABASE_PASSWORD` to match what you put in the SQL, plus `API_KEY`,
`PAYSTACK_SECRET_KEY` (live key for prod, test key for staging), the
`CUSTOM_ADMIN_*` seed values, and the real `CORS_ALLOWED_ORIGINS` /
`CSRF_TRUSTED_ORIGINS` frontend URLs.

> `.env` is git-ignored — it lives only on the server, never commit it.

---

## 6. Migrate, static, seed admin (per environment)

```bash
cd /srv/hub/prod/hub-app-backend
../venv/bin/python manage.py migrate --noinput
../venv/bin/python manage.py collectstatic --noinput
# optional one-time admin seed (max 2 admins enforced by the app)
../venv/bin/python manage.py createadmin "Admin Name" admin@example.com 'StrongPassw0rd!'
```

---

## 7. Gunicorn via systemd

```bash
sudo cp deploy/systemd/gunicorn-hub-prod.service    /etc/systemd/system/
sudo cp deploy/systemd/gunicorn-hub-staging.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now gunicorn-hub-prod gunicorn-hub-staging
systemctl status gunicorn-hub-prod
```

Each service reads its own `.env` via `EnvironmentFile=` and binds to its loopback
port (8001 prod, 8002 staging).

---

## 8. nginx vhosts

```bash
sudo cp deploy/nginx/api.hub.borderlessunn.xyz.conf      /etc/nginx/sites-available/
sudo cp deploy/nginx/api.test.hub.borderlessunn.xyz.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/api.hub.borderlessunn.xyz.conf      /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/api.test.hub.borderlessunn.xyz.conf /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

---

## 9. TLS (Let's Encrypt)

With DNS resolving and proxy set to **DNS only**:

```bash
sudo certbot --nginx \
  -d api.hub.borderlessunn.xyz \
  -d api.test.hub.borderlessunn.xyz
```

certbot rewrites the vhosts to listen on 443 and adds an 80→443 redirect.
Auto-renewal is installed via the certbot systemd timer. After certs exist you may
flip Cloudflare to **Proxied / Full (strict)**.

Django already trusts `X-Forwarded-Proto` (`SECURE_PROXY_SSL_HEADER` in settings),
so HTTPS detection works behind both nginx and Cloudflare.

---

## 10. Verify

```bash
curl -i https://api.hub.borderlessunn.xyz/api/v1/
curl -i https://api.test.hub.borderlessunn.xyz/api/v1/
# Swagger UI:
#   https://api.hub.borderlessunn.xyz/api/v1/docs/
```

---

## 11. Redeploying after code changes

```bash
sudo -u hub /srv/hub/prod/hub-app-backend/deploy/deploy.sh prod
sudo -u hub /srv/hub/staging/hub-app-backend/deploy/deploy.sh staging
```

(`deploy.sh` runs `git pull`, installs deps, migrates, collects static, restarts
gunicorn. It calls `sudo systemctl restart` — allow that for the `hub` user via a
sudoers rule, or run the restart manually as your admin user.)

---

## Troubleshooting

| Symptom                         | Check                                                        |
|---------------------------------|-------------------------------------------------------------|
| 502 Bad Gateway                 | `systemctl status gunicorn-hub-prod`; `journalctl -u gunicorn-hub-prod -n 50` |
| `DisallowedHost`                | `ALLOWED_HOSTS` in that env's `.env`                         |
| CSRF / CORS errors from frontend| `CSRF_TRUSTED_ORIGINS` / `CORS_ALLOWED_ORIGINS` in `.env`    |
| DB auth failed                  | `DATABASE_PASSWORD` vs the SQL; `\du` in psql                |
| Static 404 on admin/DRF UI      | `collectstatic` ran; nginx `alias` path matches `STATIC_ROOT` |
