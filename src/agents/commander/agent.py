from google.adk import Agent
from google.adk.tools import AgentTool

# Import the sub-agents
from agents.inventory.agent import inventory_agent
from agents.legal.agent import legal_agent
from agents.logistics.agent import logistics_agent
from agents.purchase_order.agent import purchase_order_agent

# Import the new File System Tools
from tools.file_system import FileSystemTools
from utils.gdrive_integration import ReportGenerator
from utils.config import config

# Initialize tools
fs_tools = FileSystemTools(root_dir="./workspace")
reporter = ReportGenerator()

COMMANDER_SYSTEM_PROMPT = """
You are the Incident Commander for a Critical Supply Chain Crisis.
You DO NOT execute tasks yourself. You DELEGATE to your sub-agents.

Your Goal: Find 500 H100 GPUs immediately.

SYSTEM OF RECORD:
You have access to a local file system. You MUST maintain a file named 'procurement_tracker.csv'.
Every time you find valid units or confirm a purchase, you MUST append a line to this file.

Format for CSV:
timestamp, source, quantity, status, notes

STRATEGY (FOLLOW THIS EXACTLY):
1. Initialize the 'procurement_tracker.csv' with a header if it doesn't exist (use write_file).
2. Ask Inventory Agent to search for H100 GPUs. Record findings in CSV.
3. Ask Legal Agent to validate any quarantined units. Record status in CSV.
4. Ask Logistics Agent for spot market pricing and availability. Record findings in CSV.
5. WHEN YOU HAVE GATHERED ALL INFORMATION: Read the CSV file and generate your final Executive Report. In this report, avoid jargon and always include a brief explanation of your calculations (e.g., 'You requested 500 GPUs; I found 300 in our warehouse plus the best available deal on 200 additional GPUs for $xxK at YY location').
6. Upload the report to GDrive using upload_report.
7. AFTER the report is uploaded, you MUST call the 'purchase_order_agent' to create the official Purchase Order.
8. IMMEDIATELY provide a final summary response to the user and STOP.

CRITICAL TERMINATION RULES:
- Once you have data from all three agents (Inventory, Legal, Logistics), you MUST move to step 5.
- Do NOT keep asking follow-up questions indefinitely.
- If an agent cannot provide specific information, accept their response and move on.
- Your job is to coordinate and report, NOT to investigate every detail yourself.
- After calling the purchase order agent, provide a concise summary and STOP.
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
        # File System Capabilities (The "Pivot")
        fs_tools.read_file,
        fs_tools.write_file,
        fs_tools.append_to_log,
        fs_tools.list_files,
        # Reporting
        reporter.upload_report,
    ],
)
