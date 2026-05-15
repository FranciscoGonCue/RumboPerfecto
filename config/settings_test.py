"""
Ajustes para `manage.py test`: SQLite en memoria (sin cliente MySQL).

Uso:
  python manage.py test --settings=config.settings_test
"""

from .settings import *  # noqa: F401, F403

INSTALLED_APPS = list(INSTALLED_APPS) + ["tests.apps.TestsConfig"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
