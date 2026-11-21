#!/usr/bin/env python3
"""
LinkedIn Auto-Publisher via Official REST API
Reads unpublished posts from posts.json, publishes the next one,
and marks it as published with a UTC timestamp.
"""

import json
import os
import sys
from datetime import datetime, timezone
import requests

POSTS_FILE = os.path.join(os.path.dirname(__file__), "posts.json")


def load_posts():
    if not os.path.exists(POSTS_FILE):
        print(f"Error: {POSTS_FILE} not found.", file=sys.stderr)
        sys.exit(1)
    with open(POSTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_posts(posts):
    with open(POSTS_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)
        f.write("\n")


def get_next_post(posts):
    for post in posts:
        if not post.get("published", False):
            return post
    return None


def format_author_urn(raw_urn: str) -> str:
    raw_urn = raw_urn.strip()
    if raw_urn.startswith("urn:li:person:"):
        return raw_urn
    return f"urn:li:person:{raw_urn}"


def publish_post(access_token: str, author_urn: str, commentary: str):
    """
    Attempts publishing via LinkedIn's official REST Posts API,
    with automatic fallback to v2 ugcPosts if versioning differs.
    """
    author = format_author_urn(author_urn)

    # 1. Try modern /rest/posts API
    rest_url = "https://api.linkedin.com/rest/posts"
    rest_headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
        "LinkedIn-Version": "202401",
    }
    rest_payload = {
        "author": author,
        "commentary": commentary,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }

    print(f"Attempting publish via /rest/posts for author: {author}...")
    response = requests.post(rest_url, headers=rest_headers, json=rest_payload, timeout=30)

    if response.status_code in (200, 201):
        print(f"Successfully published via /rest/posts (Status: {response.status_code})")
        return response.headers.get("x-restli-id", "ok")

    print(f"/rest/posts returned {response.status_code}: {response.text}")
    print("Falling back to /v2/ugcPosts API...")

    # 2. Fallback to classic /v2/ugcPosts API
    ugc_url = "https://api.linkedin.com/v2/ugcPosts"
    ugc_headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }
    ugc_payload = {
        "author": author,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": commentary},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }

    ugc_resp = requests.post(ugc_url, headers=ugc_headers, json=ugc_payload, timeout=30)
    if ugc_resp.status_code in (200, 201):
        print(f"Successfully published via /v2/ugcPosts (Status: {ugc_resp.status_code})")
        data = ugc_resp.json()
        return data.get("id", "ok")

    raise RuntimeError(
        f"Publishing failed. HTTP {ugc_resp.status_code}: {ugc_resp.text}"
    )


def main():
    access_token = os.environ.get("LINKEDIN_ACCESS_TOKEN")
    author_urn = os.environ.get("LINKEDIN_AUTHOR_URN")

    if not access_token or not author_urn:
        print(
            "Error: LINKEDIN_ACCESS_TOKEN and LINKEDIN_AUTHOR_URN environment variables must be set.",
            file=sys.stderr,
        )
        sys.exit(1)

    posts = load_posts()
    next_post = get_next_post(posts)

    if not next_post:
        print("All posts have already been published! Add more to posts.json.")
        return

    post_id = next_post.get("id", "unknown")
    post_title = next_post.get("title", "")
    print(f"Selected post to publish: [{post_id}] - {post_title}")

    try:
        remote_id = publish_post(access_token, author_urn, next_post["content"])
        now_utc = datetime.now(timezone.utc).isoformat()
        next_post["published"] = True
        next_post["published_at"] = now_utc
        next_post["remote_post_id"] = remote_id
        save_posts(posts)
        print(f"Updated posts.json successfully for {post_id} at {now_utc}")
    except Exception as exc:
        print(f"Failed to publish post {post_id}: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
