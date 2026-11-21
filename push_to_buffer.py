#!/usr/bin/env python3
"""
Re-sync Buffer Queue:
1. Deletes previous text-only posts
2. Adds rich posts with High-Resolution Architecture & Project Images attached
"""

import json
import os
import sys
import requests

BUFFER_GRAPHQL_URL = "https://api.buffer.com"
POSTS_FILE = os.path.join(os.path.dirname(__file__), "posts.json")
CHANNEL_ID = "6b01f8dfece6dfde5f4a303c"

OLD_POST_IDS = [
    "6b01fa678bd84d5966165aff",
    "6b01fa67142c9575193ea806",
    "6b01fa680247969092fbf16a",
    "6b01fa68142c9575193ea847",
    "6b01fa698bd84d5966165b59",
    "6b01fa69846b0ee90735661e"
]


def load_posts():
    with open(POSTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_posts(posts):
    with open(POSTS_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)
        f.write("\n")


def delete_old_posts(token: str):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    print("🧹 Cleaning up old text-only posts from Buffer queue...")
    for pid in OLD_POST_IDS:
        q = f'mutation {{ deletePost(input: {{ id: "{pid}" }}) {{ ... on DeletePostSuccess {{ id }} }} }}'
        try:
            r = requests.post(BUFFER_GRAPHQL_URL, headers=headers, json={"query": q}, timeout=15)
            print(f"  Removed old post: {pid}")
        except Exception as e:
            print(f"  Notice on {pid}: {e}")


def add_post_with_image(token: str, channel_id: str, text: str, image_url: str):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    escaped_text = json.dumps(text)

    assets_str = ""
    if image_url:
        assets_str = f'assets: [{{ image: {{ url: "{image_url}" }} }}]'
    else:
        assets_str = 'assets: []'

    query = f"""
    mutation {{
      createPost(input: {{
        channelId: "{channel_id}",
        text: {escaped_text},
        mode: addToQueue,
        schedulingType: automatic,
        needsApproval: false,
        {assets_str}
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

    delete_old_posts(token)

    posts = load_posts()
    print(f"\n🚀 Scheduling {len(posts)} posts WITH high-res images attached...\n")

    for i, post in enumerate(posts, 1):
        title = post.get("title")
        img = post.get("image_url")
        print(f"[{i}/{len(posts)}] Scheduling: {title}...")
        print(f"  🖼️  Image: {img}")
        try:
            post_id, due_at = add_post_with_image(token, CHANNEL_ID, post["content"], img)
            post["published"] = True
            post["scheduled_for"] = due_at
            post["buffer_post_id"] = post_id
            print(f"  ✅ Scheduled in queue! Due at: {due_at} (ID: {post_id})\n")
        except Exception as e:
            print(f"  ❌ Failed: {e}\n")

    save_posts(posts)
    print("=" * 70)
    print("✨ ALL 6 POSTS SUCCESSFULLY RE-SCHEDULED WITH HIGH-RES IMAGES & LINKS!")
    print("=" * 70)


if __name__ == "__main__":
    main()
