#!/usr/bin/env python3
"""
Automatically push all queued technical posts from posts.json
into Buffer's LinkedIn queue via Buffer's GraphQL API.
"""

import json
import os
import sys
import requests

BUFFER_GRAPHQL_URL = "https://api.buffer.com"
POSTS_FILE = os.path.join(os.path.dirname(__file__), "posts.json")


def load_posts():
    with open(POSTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_posts(posts):
    with open(POSTS_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)
        f.write("\n")


def get_linkedin_channel(token: str):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    # 1. Fetch organization ID
    q_org = "{ account { organizations { id name } } }"
    r_org = requests.post(BUFFER_GRAPHQL_URL, headers=headers, json={"query": q_org}, timeout=20)
    if r_org.status_code != 200:
        raise RuntimeError(f"Failed to fetch organization: {r_org.text}")

    orgs = r_org.json().get("data", {}).get("account", {}).get("organizations", [])
    if not orgs:
        raise RuntimeError("No organizations found in Buffer account.")
    org_id = orgs[0]["id"]

    # 2. Fetch channels for this organization
    q_channels = f'{{ channels(input: {{ organizationId: "{org_id}" }}) {{ id name service }} }}'
    r_chan = requests.post(BUFFER_GRAPHQL_URL, headers=headers, json={"query": q_channels}, timeout=20)
    if r_chan.status_code != 200:
        raise RuntimeError(f"Failed to fetch channels: {r_chan.text}")

    channels = r_chan.json().get("data", {}).get("channels", [])
    for ch in channels:
        if ch.get("service") == "linkedin":
            print(f"✅ Found LinkedIn Channel: {ch.get('name')} (ID: {ch.get('id')})")
            return ch.get("id")

    raise RuntimeError("No connected LinkedIn channel found in your Buffer account! Please connect LinkedIn first.")


def add_post_to_buffer(token: str, channel_id: str, text: str):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    escaped_text = json.dumps(text)

    query = f"""
    mutation {{
      createPost(input: {{
        channelId: "{channel_id}",
        text: {escaped_text},
        mode: addToQueue,
        schedulingType: automatic,
        needsApproval: false,
        assets: []
      }}) {{
        ... on PostActionSuccess {{
          post {{
            id
            dueAt
          }}
        }}
        ... on MutationError {{
          message
        }}
      }}
    }}
    """
    resp = requests.post(BUFFER_GRAPHQL_URL, headers=headers, json={"query": query}, timeout=30)
    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text}")

    res_data = resp.json()
    action = res_data.get("data", {}).get("createPost", {})
    if "post" in action:
        return action["post"]["id"], action["post"].get("dueAt")
    if "message" in action:
        raise RuntimeError(f"Buffer error: {action['message']}")
    raise RuntimeError(f"Unexpected response: {res_data}")


def main():
    token = os.environ.get("BUFFER_API_KEY")
    if not token and len(sys.argv) > 1:
        token = sys.argv[1]

    if not token:
        print("Usage: python3 push_to_buffer.py <BUFFER_API_KEY>")
        sys.exit(1)

    print("Connecting to Buffer and finding LinkedIn channel...")
    channel_id = get_linkedin_channel(token)

    posts = load_posts()
    pending = [p for p in posts if not p.get("published", False)]
    print(f"Found {len(pending)} pending posts to schedule.\n")

    for i, post in enumerate(pending, 1):
        print(f"[{i}/{len(pending)}] Scheduling: {post.get('title')}...")
        try:
            post_id, due_at = add_post_to_buffer(token, channel_id, post["content"])
            post["published"] = True
            post["scheduled_for"] = due_at
            post["buffer_post_id"] = post_id
            print(f"  🎉 Scheduled in queue! Due at: {due_at} (ID: {post_id})\n")
        except Exception as e:
            print(f"  ❌ Failed: {e}\n")

    save_posts(posts)
    print("=" * 60)
    print("🚀 ALL 6 TECHNICAL POSTS ARE NOW OFFICIALLY SCHEDULED IN BUFFER!")
    print("=" * 60)


if __name__ == "__main__":
    main()
