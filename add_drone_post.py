#!/usr/bin/env python3
"""
Add Drone Neural Docking project with Himanshu to Buffer queue
"""

import json
import requests

BUFFER_GRAPHQL_URL = "https://api.buffer.com"
token = "8dQRo-4e4FdSybDCP6HvnX3DHURrrkI_LtuC1xwG5WO"
channel_id = "6b01f8dfece6dfde5f4a303c"

content = """Most autonomous drones rely on optical cameras and fiducial markers (like AprilTags) for landing pad docking.

While accurate under ideal lighting, cameras create major bottlenecks on lightweight micro-aerial platforms:
- 5W–15W compute power drain on companion computers (Raspberry Pi/Jetson).
- Optical failure in low-light, dust, prop-wash, or lens occlusion.
- Added payload weight that severely shortens flight endurance.

Together with Himanshu Patel, we built a camera-free TinyML alternative:

🛸 Efficient Multi-Sensor Neural Docking:
Instead of heavy cameras, we instrumented the airframe with 4 directional infrared (IR) proximity sensors feeding an ultra-compact feedforward neural network.

⚙️ The Engineering Constraints:
- Quantized down to 8-bit integers (INT8) running on bare-metal microcontrollers (ESP32 / ARM Cortex-M).
- Flash footprint under 3 KB (<3 KB!).
- Power consumption under 300 mW (nearly 95% reduction in power compared to companion computers).

Open-source code, hardware architecture, and firmware benchmarks:
https://github.com/givemehat/efficient-neural-docking

Always open to connect with developers building at the intersection of TinyML, embedded robotics, and edge AI.

#TinyML #EmbeddedSystems #Robotics #Drones #EdgeAI #OpenSource #DeepLearning"""

img_url = "https://raw.githubusercontent.com/givemehat/efficient-neural-docking/main/figs/drone_docking_system.jpeg"

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
    assets: [{{ image: {{ url: "{img_url}" }} }}]
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
