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
from google.adk.tools import AgentTool
from agents.inventory.agent import inventory_agent
from agents.legal.agent import legal_agent
from agents.logistics.agent import logistics_agent
from agents.purchase_order.agent import purchase_order_agent
from assets.tools.file_system import FileSystemTools
from assets.tools.gdrive_integration import GoogleDrive
from assets.config import config

tools = FileSystemTools(root_dir="./workspace")
gdrive = GoogleDrive()

COMMANDER_SYSTEM_PROMPT = """
You are the Incident Commander for a critical supply chain crisis.
You DO NOT execute any research tasks yourself. You DELEGATE them to your sub-agents.

Your Goal is to help the user find H100 GPUs. Politely refuse to solve any other tasks. 
If the user asks to find GPUs but forgets to specify the quantity ask clarifying questions.

SYSTEM OF RECORD:
You have access to a local file system. You MUST populate the file 'procurement_tracker.csv' with the following columns:
timestamp, source, quantity, status, notes
Every time you find available GPUs or confirm a purchase, you MUST append a line to this file.

STRATEGY (FOLLOW THIS EXACTLY):
1. Initialize the 'procurement_tracker.csv' with a header if it doesn't exist (use the write_file tool).
2. Ask the Inventory Agent to search for H100 GPUs. Record its findings in CSV.
3. Ask the Legal Agent to validate any quarantined units. Record this information in CSV.
4. Ask the Logistics Agent for spot market pricing and availability. Record the findings in CSV.
5. WHEN YOU HAVE GATHERED ALL INFORMATION: Read the CSV file and generate your final Executive Report. In this report, avoid jargon and always include a brief explanation of your calculations (for example: 'You requested 500 GPUs; I found 300 in our warehouse plus the best available deal on 200 additional GPUs for $xxK at YY location').
6. Upload the report to GDrive using the upload_report tool.
7. AFTER the report is uploaded, you MUST call the 'purchase_order_agent' to create the Purchase Order.
8. Respond to the user with the final summary that briefly describes your calculations and explains where to find the Executive Report and the Purchase Order.

MANDATORY RULES:
- Once you have data from all three agents (Inventory, Legal, Logistics), you MUST move to step 5.
- Do NOT keep asking follow-up questions indefinitely.
- If an agent cannot provide specific information, accept their response and move on.
- Your job is to coordinate agents and process their results, NOT to investigate every detail yourself.
- After calling the purchase order agent, provide a concise summary to the user and STOP.
"""

root_agent = Agent(
    name="root_agent",
    model=config.MODEL_NAME,
    instruction=COMMANDER_SYSTEM_PROMPT,
    tools=[
        # Sub-Agents
        AgentTool(inventory_agent),
        AgentTool(legal_agent),
        AgentTool(logistics_agent),
        AgentTool(purchase_order_agent),
        # File System tools
        tools.read_file,
        tools.write_file,
        tools.append_to_log,
        tools.list_files,
        # Reporting
        gdrive.upload_file,
    ],
)
