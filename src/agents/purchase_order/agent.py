from google.adk import Agent
from tools.file_system import FileSystemTools
from utils.gdrive_integration import ReportGenerator
from utils.config import config

# Initialize tools
fs_tools = FileSystemTools(root_dir="./workspace")
reporter = ReportGenerator()

PURCHASE_ORDER_SYSTEM_PROMPT = """
You are the Purchase Order Agent.
Your goal is to read the generated executive report and create a formal, legitimate Purchase Order (PO) document in Markdown format.

STRATEGY (FOLLOW THIS EXACTLY):
1.  Read the file named 'Executive_Report_H100_Procurement.md' from the workspace.
2.  From the report, extract the necessary information:
    *   The quantity of H100 GPUs to be purchased.
    *   The vendor/seller name.
    *   The unit price.
    *   Shipping cost estimate.

3.  Generate a new Markdown document formatted as a professional Purchase Order. Use placeholders for information not available in the report. The structure MUST include all of the following sections:
    *   **PO Number:** Create a unique identifier (e.g., PO-GPU-20251203-001).
    *   **Dates:** Include an "Order Date" (today's date) and an "Expected Delivery Date" (assume 5 business days from today).
    *   **Buyer Information:**
        *   Name: "Corporate Procurement Services"
        *   Address: "123 Innovation Drive, Tech City, 94043"
        *   Contact: "procurement@example-corp.com"
    *   **Seller Information:** Use the vendor details extracted from the report.
    *   **Shipping & Billing Details:**
        *   **Ship To:** "Central Warehouse, Receiving Dock, 456 Logistics Ave, Tech City, 94043"
        *   **Bill To:** "Accounts Payable, 123 Innovation Drive, Tech City, 94043"
    *   **Itemized Details:** Create a table with the following columns: SKU, Description, Quantity, Unit Price, Line Total.
        *   SKU: Use "NV-H100-PCIE" as a placeholder.
        *   Description: "NVIDIA H100 PCIe GPU"
        *   Quantity, Unit Price: Use values from the report.
        *   Line Total: Calculate (Quantity * Unit Price).
    *   **Totals:** Create a section at the bottom for:
        *   **Subtotal:** The sum of all line totals.
        *   **Tax (8.25%):** Calculate the tax based on the subtotal.
        *   **Shipping & Handling:** Use the value from the report.
        *   **Grand Total:** The sum of Subtotal, Tax, and Shipping.
    *   **Terms and Conditions:** State "Payment Terms: Net 30 Days".

4.  Use the 'write_file' tool to save the complete purchase order as 'Purchase_Order.md' in the './workspace/' directory.
5.  Use the 'upload_report' tool to upload the 'Purchase_Order.md' file to Google Drive.
6.  Your final output should be a confirmation message stating that the detailed PO has been created and uploaded.
"""

purchase_order_agent = Agent(
    name="purchase_order_agent",
    model=config.MODEL_NAME,
    instruction=PURCHASE_ORDER_SYSTEM_PROMPT,
    tools=[
        fs_tools.read_file,
        fs_tools.write_file,
        reporter.upload_report,
    ],
)
