"""
WSGI config for core project — Vercel Serverless Entry Point.

Vercel's @vercel/python runtime looks for an `app` variable in this file.
It exposes the Django WSGI application as both `application` and `app`.

On every cold start, this module also runs `collectstatic` so that
WhiteNoise can serve admin/DRF static assets from within the lambda.
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

# Initialise the Django WSGI application FIRST (sets up settings, apps, etc.)
from django.core.wsgi import get_wsgi_application  # noqa: E402

application = get_wsgi_application()

# ── Cold-start: collect static files into /tmp so WhiteNoise can serve them ──
# Vercel lambdas have a read-only filesystem except for /tmp.
# We only run this once per cold start; subsequent requests reuse the container.
try:
    from django.core.management import call_command

    call_command("collectstatic", "--no-input", verbosity=0)
except Exception:
    # If collectstatic fails (e.g. no DB yet), the API still works — only
    # the admin panel / DRF browsable-API CSS will be missing.
    pass

# Vercel looks for `app`
app = application
