#!/usr/bin/env python3
"""
Add replacement student guidance post into Buffer
"""

import json
import requests

BUFFER_GRAPHQL_URL = "https://api.buffer.com"
token = "8dQRo-4e4FdSybDCP6HvnX3DHURrrkI_LtuC1xwG5WO"
channel_id = "6b01f8dfece6dfde5f4a303c"

content = """If I could give one piece of practical advice to students and juniors building projects for software engineering roles:

Stop building isolated tutorial clones.

When senior engineers and tech teams look at your GitHub, what actually stands out isn't another Netflix UI clone or generic CRUD app. It’s how you handle real engineering constraints:

1. State & Data Integrity: Instead of just dumping JSON to a database, think about transactions, schema migrations, and what happens when two users touch the same record concurrently.
2. Authorization over Authentication: Anyone can implement a basic login. The real engineering begins with granular access control—whether via Role-Based Access Control (RBAC) or Row-Level Security (RLS) directly at the database engine level.
3. Observability & Edge Cases: Does your backend fail silently with generic 500 errors, or do you have structured logging, error boundaries, and strict runtime input validation (like Pydantic or Zod)?

You don't need 20 tutorial repositories on your profile. 2 deeply thought-out systems with clean architectural decisions, Dockerized setups, and reproducible READMEs will take you significantly further.

Always happy to connect and help juniors or fellow developers navigating their tech journey. If you are building something interesting or want honest feedback on your system architecture, feel free to drop a DM—always open to discuss.

#SoftwareEngineering #SystemDesign #FullStack #CareerAdvice #StudentDevelopers #Mentorship"""

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
}

escaped_text = json.dumps(content)

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

r = requests.post(BUFFER_GRAPHQL_URL, headers=headers, json={"query": query})
print("Result:", r.json())
