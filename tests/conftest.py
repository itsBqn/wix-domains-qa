import os
import uuid
from pathlib import Path

import requests
from dotenv import load_dotenv

# Secrets come only from .env. They are never printed.
load_dotenv(Path(__file__).parent.parent / ".env")

API_URL = "https://www.wixapis.com/domain-search/v2/check-domain-availability"


def auth_headers():
    return {
        "Authorization": os.environ["WIX_API_KEY"],
        "wix-account-id": os.environ["WIX_ACCOUNT_ID"],
    }


def check_domain(domain, headers=None):
    """One GET to check-domain-availability. domain=None sends no domain parameter."""
    if headers is None:
        headers = auth_headers()
    params = {} if domain is None else {"domain": domain}
    return requests.get(API_URL, headers=headers, params=params, timeout=15)


def random_domain():
    """A long random .com name. Almost certainly free (a point-in-time answer)."""
    return "qa-" + uuid.uuid4().hex[:20] + ".com"
