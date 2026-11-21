#!/usr/bin/env python3
"""
Helper script to fetch your LinkedIn Person URN / Member ID using your Access Token.
Usage:
  export LINKEDIN_ACCESS_TOKEN="your_token_here"
  python3 get_linkedin_urn.py
"""

import os
import sys
import requests

token = os.environ.get("LINKEDIN_ACCESS_TOKEN")
if not token:
    print("Please set LINKEDIN_ACCESS_TOKEN environment variable first:")
    print("  export LINKEDIN_ACCESS_TOKEN='AQX...'")
    sys.exit(1)

# Try userinfo endpoint (OpenID Connect compliant)
headers = {"Authorization": f"Bearer {token}"}
resp = requests.get("https://api.linkedin.com/v2/userinfo", headers=headers)

if resp.status_code == 200:
    data = resp.json()
    sub = data.get("sub")
    name = data.get("name", "User")
    print("\n✅ Success!")
    print(f"Logged in as: {name}")
    print(f"Your LinkedIn Person URN is: urn:li:person:{sub}")
    print(f"\nSet this in your GitHub Secret LINKEDIN_AUTHOR_URN: urn:li:person:{sub}")
    sys.exit(0)

# Fallback to /v2/me endpoint
resp2 = requests.get("https://api.linkedin.com/v2/me", headers=headers)
if resp2.status_code == 200:
    data2 = resp2.json()
    person_id = data2.get("id")
    print("\n✅ Success!")
    print(f"Your LinkedIn Person URN is: urn:li:person:{person_id}")
    print(f"\nSet this in your GitHub Secret LINKEDIN_AUTHOR_URN: urn:li:person:{person_id}")
    sys.exit(0)

print(f"❌ Failed to fetch user info. HTTP {resp.status_code}: {resp.text}", file=sys.stderr)
sys.exit(1)
