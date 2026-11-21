#!/usr/bin/env python3
"""
Add Kaggle ML / Computer Vision engineering post into Buffer
"""

import json
import requests

BUFFER_GRAPHQL_URL = "https://api.buffer.com"
token = "8dQRo-4e4FdSybDCP6HvnX3DHURrrkI_LtuC1xwG5WO"
channel_id = "6b01f8dfece6dfde5f4a303c"

content = """The biggest lesson learned from training Computer Vision & ML models across Kaggle and real-world edge hardware:

High validation accuracy on static datasets rarely survives real-world deployment.

Here are 3 reproducible ML practices that helped me move beyond notebook accuracy:

1. Data Leakage in Preprocessing:
Never fit scalers, encoders, or augmentations across your full dataset prior to the cross-validation split. Information leakage can easily inflate validation metrics by 8–15%, only to collapse during testing.

2. Distribution Shift in Computer Vision:
Clean benchmark frames from public datasets hide real-world noise: lens flare, compression artifacts, and low frame rates. If your CV pipeline doesn't augment for blur and lighting variation, it will fail in production.

3. Quantization Aware Training (QAT):
Moving from FP32 to INT8 isn't just `model.tflite` export. Post-training quantization often causes severe edge-case accuracy drops. Evaluating calibration datasets with representative real-world samples is essential for edge deployment.

Machine learning isn't just about tuning hyperparameters—it's about building robust, reproducible pipelines that don't break under noise.

My Kaggle profile: https://www.kaggle.com/sirrajnish

Always happy to connect with students and developers working on applied AI, computer vision, and reproducible ML systems. My DMs are open to discuss.

#MachineLearning #ComputerVision #Kaggle #DeepLearning #DataScience #AIResearch"""

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
