"""
Test settings: in-memory sqlite so the suite runs without the production
Postgres credentials. Everything else inherits from the real settings.
"""
import os

os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")
os.environ.setdefault("DEBUG", "True")
os.environ.setdefault("ALLOWED_HOSTS", "*")
os.environ.setdefault("DATABASE_NAME", "unused")
os.environ.setdefault("DATABASE_USER", "unused")
os.environ.setdefault("DATABASE_PASSWORD", "unused")
os.environ.setdefault("DATABASE_HOST", "localhost")
os.environ.setdefault("DATABASE_PORT", "5432")
os.environ.setdefault("PAYSTACK_SECRET_KEY", "sk_test_dummy")
os.environ.setdefault("API_KEY", "dummy")

from hub_auth.settings import *  # noqa: E402,F401,F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
