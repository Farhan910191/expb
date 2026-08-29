"""
WSGI config for core project — Vercel Serverless Entry Point.

Vercel's @vercel/python runtime looks for an `app` variable in this file.
It exposes the Django WSGI application as both `application` and `app`.
"""

import os
import sys
from pathlib import Path

# Ensure the project root (backend/) is on sys.path so Django can find
# the 'core' and 'expenses' packages regardless of how Vercel sets cwd.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

from django.core.wsgi import get_wsgi_application  # noqa: E402

application = get_wsgi_application()
app = application  # Vercel looks for `app`
