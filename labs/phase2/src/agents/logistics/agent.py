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

from google.adk import Agent
from tools.api import LogisticsTools
from utils.config import config

tools = LogisticsTools()

LOGISTICS_SYSTEM_PROMPT = """
You are the Logistics Manager.
Your goal is to find real-time pricing and shipping estimates from the external market.
"""

def create_agent():
    """
    Factory function to create the logistics agent.
    """
    return Agent(
        name="logistics_agent",
        model=config.MODEL_NAME,
        instruction=LOGISTICS_SYSTEM_PROMPT,
        description="Agent for fetching price quotes from the API.",
        tools=[tools.fetch_spot_prices, tools.estimate_shipping],
        output_key="logistics_agent_result",
    )
