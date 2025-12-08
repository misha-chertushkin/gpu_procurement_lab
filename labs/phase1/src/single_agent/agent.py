from google import genai
from google.genai import types
from utils.config import config
from tools.api import LogisticsTools
from tools.database import DatabaseTools
from tools.file_system import FileSystemTools
from tools.contract_analyzer import ContractAnalyzer

PROMPT = f'''
<task>
Find [number_of_gpus] H100 GPUs and upload the Executive Report and Purchase Order.
</task>

<response_format>
Respond with a brief summary of your research steps and calculation. Explain everything in simple terms, without unnecessary jargon.
</response_format>

<instructions>
1. Start by finding the quantity of GPUs available in stock using our database `{config.PROJECT_ID}.{config.DATASET_ID}`. 
    - This is a legacy database with messy names of tables and columns. Use the `explore_schema` tool to learn about the structure of tables `{config.PROJECT_ID}.{config.DATASET_ID}.{config.TABLE_CATALOG}` and `{config.PROJECT_ID}.{config.DATASET_ID}.{config.TABLE_INVENTORY}`.
    - Use your best judgement to figure out the role of each table and column, and find an optimal way to join these tables.
    - Write a SQL query for loading the requested inventory data including the status and use the `run_query` tool to execute your query.
    - Capture the status of GPUs that you found (some of them can be in Quarantine in which case you will have to confirm their availability in the legal contract).
2. Analyze the Master Supply Agreement to confirm that the GPUs available in stock can be used.
    - The Master Supply Agreement is stored in GCS as: 'Master_Supply_Agreement_NVIDIA.pdf'
    - You must use the tool `analyze_contract_clause` to extract relevant information from this document.
    - Find the 'Exclusivity' clauses (restrictions) and 'Force Majeure' clauses (exceptions).
    - Interpret the 'HOLD_LEGAL' status codes based on the contract definitions.
3. Obtain the latest spot price for any remaining GPUs that should be purchased on the marketplace, including shipping estimates.
    - Use the tool `fetch_spot_prices` to find the market price per GPU.
    - Use the tool `estimate_shipping` to quote the shipping cost.
4. Generate the Executive Report. 
    - Write a brief explanation of your finding and calculations.
    - The structure of the Executive Report must follow this example:
```
# Executive Report
1. You requested [number_of_GPUs] H100 GPUs; 
2. I found [number_of_available_GPUs_in_stock] in our warehouse that are available based on [brief analysis of Master Supply Agreement]
3. The remaining [number_of_GPUs_] GPUs can be ordered on the marketplace from [vendor name] for $[total amount]K total including shipping.
```
    - Use the 'write_file' tool to save the repoert to `./workspace/Executive_Report.md`.
    - Upload the report to Google Drive using the `upload_report` tool. 
5. Generate the Purchase Order in Markdown format.
    - Use information from the Executive Report generated in Step 4.
    - Generate the purchase order in Markdown format, with placeholders for information that is not available.
    - Use the 'write_file' tool to save the purchase order to `./workspace/Purchase_Order.md`.
    - Upload purchase to Google Drive using the `upload_report` tool. 
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
    '''Solve the task of finding GPUs without ADK (using a single prompt with tools)'''

    logistics = LogisticsTools()
    database = DatabaseTools()
    filesystem = FileSystemTools()
    contract = ContractAnalyzer()
    prompt = [types.Content(role="user", parts=[types.Part(text=PROMPT.replace('[number_of_gpus]', str(number_of_gpus)))])]

    client = genai.Client(vertexai=True, project=config.PROJECT_ID, location=config.REGION)
    while True:
        response = client.models.generate_content(
            model=config.MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction='',
                tools=[
                    logistics.fetch_spot_prices,
                    logistics.estimate_shipping,
                    database.explore_schema,
                    database.run_query,
                    filesystem.read_file,
                    filesystem.write_file,
                    filesystem.append_to_log,
                    filesystem.list_files,
                    contract.analyze_contract_clause,
                ],
                tool_config=types.ToolConfig(function_calling_config=types.FunctionCallingConfig(mode=types.FunctionCallingConfigMode.VALIDATED)),
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
            )
        )
        fc_parts = [part for part in response.candidates[0].content.parts if part.function_call]
        if not fc_parts:
            print(f'find_gpus_wihtout_adk got final response: \n{response.text}')
            break
        prompt.append(response.candidates[0].content) # Send back the function calls with thought_signature
        if len(fc_parts) == 1:
            print(f'Single function call')
        else:
            print(f'Parallel function call ({len(fc_parts)} functions)')
        function_responses = []
        for fc_part in fc_parts:
            args = fc_part.function_call.args
            print(f'Calling function {fc_part.function_call.name} with args={args}')
            match fc_part.function_call.name:
                case 'fetch_spot_prices': result = logistics.fetch_spot_prices(args['chip_type'])
                case 'estimate_shipping': result = logistics.estimate_shipping(args['origin'], args['destination'])
                case 'explore_schema': result = database.explore_schema(args['table_name'])
                case 'run_query': result = database.run_query(args['sql_query'])
                case 'read_file': result = filesystem.read_file(args['filename'])
                case 'write_file': result = filesystem.write_file(args['filename'], args['content'])
                case 'append_to_log': result = filesystem.append_to_log(args['filename'], args['content'])
                case 'list_files': result = filesystem.list_files()
                case 'analyze_contract_clause': result = contract.analyze_contract_clause(args['doc_name'], args['clause_type'])
                case _: raise ValueError(f"Unrecognized function_call.name: {fc_part}")
            function_responses.append(types.Part.from_function_response(name=fc_part.function_call.name, response={'result': result}))
        prompt.append(types.Content(role="tool", parts=function_responses))
        print(f'Prompt now has {len(prompt)} parts.') 

if __name__ == "__main__":
    run_agent(345)