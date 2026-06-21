-- Create the production and staging databases + users.
-- Run as the postgres superuser:
--     sudo -u postgres psql -f deploy/postgres-setup.sql
-- IMPORTANT: replace the two CHANGE_ME passwords before running.

-- ── Production ───────────────────────────────────────────────
CREATE USER borderless_hub_prod_user WITH PASSWORD 'CHANGE_ME_PROD';
CREATE DATABASE borderless_hub_prod_db OWNER borderless_hub_prod_user;

-- ── Staging ──────────────────────────────────────────────────
CREATE USER borderless_hub_test_user WITH PASSWORD 'CHANGE_ME_STAGING';
CREATE DATABASE borderless_hub_test_db OWNER borderless_hub_test_user;

-- Recommended session defaults for Django on both roles.
ALTER ROLE borderless_hub_prod_user SET client_encoding TO 'utf8';
ALTER ROLE borderless_hub_prod_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE borderless_hub_prod_user SET timezone TO 'UTC';

ALTER ROLE borderless_hub_test_user SET client_encoding TO 'utf8';
ALTER ROLE borderless_hub_test_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE borderless_hub_test_user SET timezone TO 'UTC';

-- PostgreSQL 15+: the public schema is locked down by default. Grant it.
\connect borderless_hub_prod_db
GRANT ALL ON SCHEMA public TO borderless_hub_prod_user;

\connect borderless_hub_test_db
GRANT ALL ON SCHEMA public TO borderless_hub_test_user;
