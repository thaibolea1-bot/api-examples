# -*- coding: utf-8 -*-
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from absl.testing import absltest


class UnitTests(absltest.TestCase):

    def test_models_list(self):
        # [START models_list]
        from google import genai

        client = genai.Client()

        print("List of models that support generateContent:\n")
        for m in client.models.list():
            for action in m.supported_actions:
                if action == "generateContent":
                    print(m.name)

        print("List of models that support embedContent:\n")
        for m in client.models.list():
            for action in m.supported_actions:
                if action == "embedContent":
                    print(m.name)
        # [END models_list]

    def test_models_get(self):
        # [START models_get]
        from google import genai

        client = genai.Client()
        model_info = client.models.get(model="gemini-3.8-flash")
        print(model_info)
        # [END models_get]


if __name__ == "__main__":
    absltest.main()
# Installation:
# pip install google-genai

import os
from google import genai
from google.genai import types

# 2. Initialize the GenAI Client (reads GEMINI_API_KEY from environment)
client = genai.Client()

# 3. Build GenerateContentConfig
config = types.GenerateContentConfig(
    temperature=1.30,
    top_p=0.98,
    top_k=60,
    candidate_count=1,
    max_output_tokens=2500,
    presence_penalty=0.60,
    frequency_penalty=0.40,
    system_instruction="You are an inventive speculative fiction author. Explore vivid metaphors and original concepts.",
    safety_settings=[
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        ),
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
            threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        ),
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
            threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        ),
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        ),
    ],
)

# 4. Generate Content
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Generate 5 unexpected sci-fi novel premises involving time distortion and acoustic archaeology.",
    config=config,
)

print("=== Raw Generated Output ===")
print(response.text)
