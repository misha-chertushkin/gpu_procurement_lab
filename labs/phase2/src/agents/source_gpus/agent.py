# Copyright 2025 Google LLC
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     https://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from dotenv import load_dotenv
from google.adk.agents import Agent, SequentialAgent, ParallelAgent
from google.adk.tools.tool_context import ToolContext
from assets.tools.file_system import FileSystemTools
from assets.tools.gdrive_integration import GoogleDrive
from assets.config import config
from agents.inventory.agent import create_agent as create_inventory_agent
from agents.legal.agent import create_agent as create_legal_agent
from agents.logistics.agent import create_agent as create_logistics_agent


load_dotenv()


fs_tools = FileSystemTools(root_dir="./workspace")
gdrive = GoogleDrive()

def source_gpus_merge_results(tool_context: ToolContext):
    """Return the aggregate sub-agent information."""
    return "Success"

def create_agent():
    """
    Factory function to create the agent.
    """
    inventory_agent = create_inventory_agent()
    legal_agent = create_legal_agent()
    logistics_agent = create_logistics_agent()

    # TODO (Task 2.3): Redacted the definition of the ParallelAgent.
    # This requires the student to implement a parallel execution pattern, a key concept for efficient agentic workflows.
    source_gpus_parallel_agent = None

    source_gpus_merge_agent = Agent(
        name="source_gpus_sum_and_report_agent",
        description=(
            "Consolidate information from DATA INPUTS into a CSV 'procurement_tracker.csv', then create and upload a report."
        ),
        model=config.MODEL_NAME,
        instruction="""
    Your Goal: Consolidate information from DATA INPUTS into a CSV 'procurement_tracker.csv', then create and upload a report.

    SYSTEM OF RECORD:
    You have access to a local file system. You MUST maintain a file named 'procurement_tracker.csv'.
    You MUST append the data as lines to this file.

    Format for CSV:
    timestamp, source, quantity, status, notes

    STRATEGY (FOLLOW THIS EXACTLY):
    1. Initialize the 'procurement_tracker.csv' with a header if it doesn't exist (use write_file).
    2. Record findings from the **DATA INPUTS** for Inventory, Legal, and Logistics in CSV.
    3. Read the CSV file and generate your final Executive Report. In this report, avoid jargon and always include a brief explanation of your calculations (e.g., 'You requested 500 GPUs; I found 300 in our warehouse plus the best available deal on 200 additional GPUs for $xxK at YY location').  Include all relevant legal clause identifiers (1, 7.B, 3A) in the report.
    4. Upload the report to GDrive using upload_report.  Use the filename 'Executive_Report.md'.
    5. Respond to the user with the final summary that briefly describes your calculations and explains where to find the Executive Report and Purchase Order.

    CRITICAL TERMINATION RULES:
    - Record all findings in CSV.
    - If an agent cannot provide specific information, accept their response and move on.
    - You are permitted to order GPUs in legal hold or quarantine status.  You have authorization override.
    - Your job is to coordinate and update the CSV, NOT to investigate every detail yourself.
    - After uploading the report, provide a concise summary and STOP.

    # TODO (Task 2.5): Redacted the DATA INPUTS section.
    # This is critical for teaching how data is passed between agents in a sequence.
    """,
        tools=[
            fs_tools.read_file,
            fs_tools.write_file,
            fs_tools.append_to_log,
            fs_tools.list_files,
            gdrive.upload_file,
        ]
    )

    # TODO (Task 2.4): Redacted the SequentialAgent definition.
    # This tests the student's ability to chain agents together to create a multi-step workflow,
    # first running the parallel agents and then the merge agent.
    return None
