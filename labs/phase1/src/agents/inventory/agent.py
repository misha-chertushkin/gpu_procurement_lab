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
from tools.database import DatabaseTools
from utils.config import config

db_tools = DatabaseTools()

INVENTORY_SYSTEM_PROMPT = f"""
You are the Inventory Investigator Agent.
Your goal is to find the quantity of available GPUs of the requested type based on SQL database `{config.PROJECT_ID}.{config.DATASET_ID}`.

INSTRUCTIONS:
1. This is a legacy database with messy names of tables and columns. Use the `explore_schema` tool to learn about the structure of tables `{config.PROJECT_ID}.{config.DATASET_ID}.{config.TABLE_CATALOG}` and `{config.PROJECT_ID}.{config.DATASET_ID}.{config.TABLE_INVENTORY}`.
2. Use your best judgement to figure out the role of each table and column, and find an optimal way to join these tables.
3. Write a SQL query for loading the requested inventory data and use the `run_query` tool to execute your query.
"""

inventory_agent = Agent(
    name="inventory_agent",
    model=config.MODEL_NAME,
    instruction=INVENTORY_SYSTEM_PROMPT,
    tools=[db_tools.explore_schema, db_tools.run_query],
)
