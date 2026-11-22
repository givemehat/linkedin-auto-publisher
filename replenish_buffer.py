#!/usr/bin/env python3
"""
Autonomous Buffer Queue Replenisher:
- Checks currently scheduled post count in Buffer.
- If Buffer has free slots (< 10), finds the next unpublished post from posts.json.
- Schedules it with its exact scheduled date (Monday/Wednesday/Friday 09:00 AM IST).
- Updates posts.json with the resulting Buffer post ID.
"""

import json
import os
import sys
import urllib.request

TOKEN = os.environ.get("BUFFER_API_KEY", "8dQRo-4e4FdSybDCP6HvnX3DHURrrkI_LtuC1xwG5WO")
CHANNEL_ID = "6b01f8dfece6dfde5f4a303c"
POSTS_FILE = os.path.join(os.path.dirname(__file__), "posts.json")
BUFFER_GRAPHQL_URL = "https://api.buffer.com"


def run_graphql(query: str):
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
    }
    req = urllib.request.Request(
        BUFFER_GRAPHQL_URL,
        data=json.dumps({"query": query}).encode("utf-8"),
        headers=headers,
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_active_buffer_posts(posts):
    active_count = 0
    for p in posts:
        pid = p.get("buffer_post_id")
        if not pid:
            continue
        q = f'query {{ post(input: {{ id: "{pid}" }}) {{ id status dueAt }} }}'
        try:
            res = run_graphql(q)
            post_data = res.get("data", {}).get("post")
            if post_data and post_data.get("status") == "scheduled":
                active_count += 1
        except Exception:
            pass
    return active_count


def schedule_next_post(post):
    text = json.dumps(post["content"])
    due_at = post["scheduled_for"]
    img = post.get("image_url")
    assets_str = f'assets: [{{ image: {{ url: "{img}" }} }}]' if img else "assets: []"

    mutation = f"""
    mutation {{
      createPost(input: {{
        channelId: "{CHANNEL_ID}",
        text: {text},
        mode: customScheduled,
        dueAt: "{due_at}",
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
        ... on LimitReachedError {{
          message
        }}
      }}
    }}
    """
    res = run_graphql(mutation)
    action = res.get("data", {}).get("createPost", {})
    if "post" in action:
        return action["post"]["id"], action["post"].get("dueAt")
    if "message" in action:
        raise RuntimeError(f"Buffer Error: {action['message']}")
    raise RuntimeError(f"Unexpected response: {res}")


def main():
    if not os.path.exists(POSTS_FILE):
        print(f"Error: {POSTS_FILE} not found.")
        sys.exit(1)

    with open(POSTS_FILE, "r", encoding="utf-8") as f:
        posts = json.load(f)

    active_count = get_active_buffer_posts(posts)
    print(f"Current scheduled posts active in Buffer queue: {active_count}/10")

    if active_count >= 10:
        print("Buffer queue is currently at full capacity (10/10). No replenishment needed right now.")
        return

    slots_available = 10 - active_count
    print(f"Slots available in Buffer queue: {slots_available}")

    updated = False
    for p in posts:
        if slots_available <= 0:
            break
        if not p.get("published"):
            print(f"Pushing next queued post: {p['title']} (Due: {p.get('scheduled_human_ist')})...")
            try:
                buf_id, due = schedule_next_post(p)
                p["published"] = True
                p["buffer_post_id"] = buf_id
                slots_available -= 1
                updated = True
                print(f"  Successfully scheduled into Buffer! ID: {buf_id}")
            except Exception as e:
                print(f"  Failed: {e}")
                break

    if updated:
        with open(POSTS_FILE, "w", encoding="utf-8") as f:
            json.dump(posts, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print("Updated posts.json saved.")


if __name__ == "__main__":
    main()
