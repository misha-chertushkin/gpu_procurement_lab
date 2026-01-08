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

from google.adk.agents import Agent
import os
from google import genai
from dotenv import load_dotenv

from assets.config import config

load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID", "unset")
LOCATION = os.getenv("LOCATION", "us-central1")


genai_client = genai.Client(
    vertexai=True,
    project=PROJECT_ID,
    location=LOCATION,
)

COMMANDER_SYSTEM_PROMPT = """
You are the Incident Commander for a Critical Supply Chain Crisis.
You DELEGATE to your sub-agents and tools as needed.

Your Goal: Find 500 H100 GPUs immediately and upload the report.

SYSTEM OF RECORD:
You have access to a local file system. You MUST maintain a file named 'procurement_tracker.csv'.

Format for CSV:
timestamp, source, quantity, status, notes

STRATEGY (FOLLOW THIS EXACTLY):
1. Ask Source GPUs Agent to search for H100 GPUs.
2. Respond to the user with the final summary that briefly describes your calculations and explains where to find the Executive Report and Purchase Order.

CRITICAL TERMINATION RULES:
- Do NOT keep asking follow-up questions indefinitely.
- If an agent cannot provide specific information, accept their response and move on.
- Your job is to coordinate and report, NOT to investigate every detail yourself.
- After uploading the report, provide a concise summary and STOP.
"""

# TODO: Implement a multi-agent solution that parallelizes isolated steps from phase 1.
# DO NOT CHANGE THE NAME OF THE AGENT BELOW.  It will be used in the headless and live
# tests.  Add the relevant components to the root_agent to complete the implemntation.
#
# See https://google.github.io/adk-docs/agents/workflow-agents/parallel-agents/#full-example-parallel-web-research for help.

root_agent = Agent(
    name="root_agent",
    model=config.MODEL_NAME,
    instruction=COMMANDER_SYSTEM_PROMPT,
    sub_agents=[]
)
