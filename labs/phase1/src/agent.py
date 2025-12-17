import json
from google import genai
from google.genai import types
from assets.config import config
from assets.tools.api import LogisticsTools
from assets.tools.database import DatabaseTools
from assets.tools.file_system import FileSystemTools
from assets.tools.contract_analyzer import ContractAnalyzer
from assets.tools.gdrive_integration import GoogleDrive

PROMPT = f'''
<task>
Find [number_of_gpus] H100 GPUs and upload the Executive Report and Purchase Order.
</task>

<response_format>
Respond with a brief summary of your research steps and calculation. Explain everything in simple terms, without unnecessary jargon.
</response_format>

<instructions>
# TODO (Task 1.1): Redact the explicit tool names from the instructions to challenge the student to identify the correct tools.
1. Start by finding the quantity of GPUs available in stock using our database `{config.PROJECT_ID}.{config.DATASET_ID}`. 
    - This is a legacy database with messy names of tables and columns. Use the appropriate tool to learn about the structure of tables `{config.PROJECT_ID}.{config.DATASET_ID}.{config.TABLE_CATALOG}` and `{config.PROJECT_ID}.{config.DATASET_ID}.{config.TABLE_INVENTORY}`.
    - Use your best judgement to figure out the role of each table and column, and find an optimal way to join these tables.
    - Write a SQL query for loading the requested inventory data including the status and use the appropriate tool to execute your query.
    - Capture the status of GPUs that you found (some of them can be in Quarantine in which case you will have to confirm their availability in the legal contract).
2. Analyze the Master Supply Agreement to confirm that the GPUs available in stock can be used.
    - The Master Supply Agreement is stored in GCS as: 'Master_Supply_Agreement_NVIDIA.pdf'
    - You must use the appropriate tool to extract relevant information from this document.
    - Start by analyzing the 'Exclusivity' clauses (restrictions) and 'Force Majeure' clauses (exceptions) in parallel.
3. Analyze the Warehouse Policy Manual to confirm interpretation of inventory data.
    - The Warehouse Policy Manual is stored in GCS as: 'Warehouse_Policy_Manual_1998.pdf'
    - You must use the appropriate tool to extract relevant information from this document.
    - Start by analyzing inventory codes and descriptions.
4. Obtain the latest spot price for any remaining GPUs that should be purchased on the marketplace, including shipping estimates.
    - Use the appropriate tool to find the market price per GPU.
    - Use the appropriate tool to quote the shipping cost.
5. Generate the Executive Report. 
    - Write a brief explanation of your finding and calculations.  Include all legal clause identifiers (1, 7.B, 3A) in the references.
        # TODO (Task 1.2): The structure of the Executive Report has been redacted. 
        # The student should analyze the requirements and generate a suitable report.
    - Use the appropriate tool to save the report to `Executive_Report.md`.
    - Upload the report to Google Drive using the appropriate tool. 
6. Generate the Purchase Order in Markdown format.
    - Use information from the Executive Report generated in Step 4.
    - Generate the purchase order in Markdown format, with placeholders for information that is not available.
    - Use the appropriate tool to save the purchase order to `Purchase_Order.md`.
    - Upload purchase to Google Drive using the appropriate tool. 
    - The purchase order must have the following structure:
        ```
        *   **PO Number:** Create a unique identifier (e.g., PO-GPU-20251203-001).
        *   **Dates:** Include an "Order Date" (today's date) and an "Expected Delivery Date" (assume 5 business days from today).
        *   **Buyer Information:** Include the name, address, and email.
        *   **Seller Information:** Use the vendor details extracted from the report.
        *   **Shipping & Billing Details:** Provide "Ship to" and "Bill to" addresses.
        *   **Itemized Details:** Create a table with the following columns: SKU, Description, Quantity, Unit Price, Total Price.
        *   **Totals:** Create a section at the bottom with Subtotal, 8.25% tax, shipping cost, and grand total.
        *   **Terms and Conditions:** Explain our Net 30 policy.
        ```
6. Respond to the user with a concise summary of your findings and the location of Executive Report and the Purchase Order.
</instructions>
'''

def run_agent(number_of_gpus: int) -> None:
    '''Solve the task of finding GPUs using a single prompt with function calling (no ADK)'''

    client = genai.Client(vertexai=True, project=config.PROJECT_ID, location=config.REGION)
    logistics = LogisticsTools()
    database = DatabaseTools()
    filesystem = FileSystemTools()
    contract = ContractAnalyzer()
    google_drive = GoogleDrive()
    prompt = [types.Content(role="user", parts=[types.Part(text=PROMPT.replace('[number_of_gpus]', str(number_of_gpus)))])]
    trajectory = []
    while True:
        response = client.models.generate_content(
            model=config.MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction='',
                # TODO (Task 1.3): Redacted the list of tools.
                # The student should inspect the imported tool classes and assemble the complete list of tool functions to provide to the model.
                tools=[],
                tool_config=types.ToolConfig(function_calling_config=types.FunctionCallingConfig(mode=types.FunctionCallingConfigMode.VALIDATED)),
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
            )
        )
        assert response.candidates, f'invalid response: {response.model_dump_json(indent=4)}'
        assert response.candidates[0].finish_reason == types.FinishReason.STOP, f'bad finish_reason: {response.candidates[0].finish_reason}'
        fc_parts = [part for part in response.candidates[0].content.parts if part.function_call]
        if not fc_parts:
            print(f'\n{"="*80}\nrun_agent executed {len(trajectory)} inferences:')
            print(json.dumps(trajectory, indent=4))
            print(f'Final Agent Response:\n{response.text}')
            break
        prompt.append(response.candidates[0].content) # Send back the function calls with thought_signature
        function_calls = []
        function_responses = []
        for fc_part in fc_parts:
            args = fc_part.function_call.args
            function_calls.append({fc_part.function_call.name: str(args)})
            # TODO (Task 1.4): Redacted the match/case block.
            # This is a core concept of how tool-using agents execute tasks.
            # The student should implement the logic to dispatch the model's function calls to the correct Python tool functions.
            result = ""
            # TODO (Task 1.5): Redacted the line that wraps the tool's output.
            # This tests the student's knowledge of the specific library syntax for returning tool results to the model.
            function_responses.append("PLACEHOLDER")
        prompt.append(types.Content(role="tool", parts=function_responses))
        trajectory.append({f'Inference #{len(trajectory)+1}': function_calls[0] if len(function_calls)==1 else function_calls})

if __name__ == "__main__":
    run_agent(345)