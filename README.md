# 🚀 LinkedIn Auto-Publisher (100% Serverless & Autonomous)

Autonomous, cloud-native LinkedIn post publisher powered by **GitHub Actions** and the **Official LinkedIn REST API**.

Zero infrastructure cost, zero maintenance, and 100% compliant with LinkedIn Terms of Service.

---

## 🏗️ Architecture

```
givemehat/linkedin-auto-publisher
   ├── posts.json                        # Queue of high-signal technical posts
   ├── publish.py                        # LinkedIn official REST API publisher
   ├── get_linkedin_urn.py               # One-click script to fetch your Person URN
   └── .github/workflows/schedule.yml   # CRON runner (Every Tue & Thu at 10:00 AM IST)
```

---

## ⚡ 3-Step One-Time Setup Guide

### Step 1: Create a LinkedIn Developer App & Get Access Token (3 Mins)

1. Open [LinkedIn Developer Portal](https://www.linkedin.com/developers/apps) and click **Create App**.
2. Fill in:
   - **App Name:** `Personal Auto Publisher` (or anything you like)
   - **LinkedIn Page:** Link your college page, your project page, or create a quick test page.
3. In the **Products** tab of your app, request access to:
   - **Share on LinkedIn** (Provides `w_member_social`)
   - **Sign In with LinkedIn using OpenID Connect** (Provides `openid`, `profile`)
4. Go to **Auth** tab:
   - Under **OAuth 2.0 Tools**, click **Token Generator** (or use OAuth authorization URL).
   - Select scopes: `openid`, `profile`, `w_member_social`.
   - Click **Generate Token** and copy the Access Token.

---

### Step 2: Get your LinkedIn Person URN

Run the included helper script on your terminal:

```bash
export LINKEDIN_ACCESS_TOKEN="your_copied_token_here"
python3 get_linkedin_urn.py
```

It will print your exact URN, for example:
```
Your LinkedIn Person URN is: urn:li:person:abcdef12345
```

---

### Step 3: Add Secrets to your GitHub Repository

1. Push this project to a new private repository on GitHub: `givemehat/linkedin-auto-publisher`.
2. In GitHub, go to **Settings ➔ Secrets and variables ➔ Actions**.
3. Add two repository secrets:
   - `LINKEDIN_ACCESS_TOKEN`: The token you generated in Step 1.
   - `LINKEDIN_AUTHOR_URN`: `urn:li:person:<your-id>` from Step 2.
4. Go to **Settings ➔ Actions ➔ General ➔ Workflow permissions**:
   - Select **Read and write permissions** (so the action can commit back the updated `posts.json`).
   - Click **Save**.

---

## 🧪 Testing Immediately

You don't need to wait until Tuesday!
1. In your GitHub repo, go to the **Actions** tab.
2. Select **Scheduled LinkedIn Post Publisher** workflow on the left.
3. Click **Run workflow ➔ Run workflow**.
4. Within 30 seconds, it will publish the first post to your LinkedIn profile and mark it as `published: true` in `posts.json`!

---

## 📝 Adding New Posts

Whenever you build a new project or learn something new, simply append an entry to `posts.json`:

```json
{
  "id": "post-07-new-project",
  "title": "Title here",
  "tags": ["FullStack", "DevOps"],
  "published": false,
  "published_at": null,
  "content": "Your post text here..."
}
```

The system handles the rest autonomously.
