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

from google.adk import Agent
from tools.contract_analyzer import ContractAnalyzer
from utils.config import config

# Initialize tools
rag_tools = ContractAnalyzer()

LEGAL_SYSTEM_PROMPT = """
You are the Legal Analyst Agent.
Your goal is to interpret vendor contracts to find allowable exceptions for procurement.

ENVIRONMENT CONTEXT:
- The Master Supply Agreement is stored in GCS as: 'Master_Supply_Agreement_NVIDIA.pdf'

CRITICAL RULES:
1. You NEVER read whole documents. You use 'analyze_contract_clause' to fetch specific sections.
2. You are looking for 'Exclusivity' clauses (restrictions) and 'Force Majeure' clauses (exceptions).
3. Interpret 'HOLD_LEGAL' status codes based on contract definitions.
"""

legal_agent = Agent(
    name="legal_agent",
    model=config.MODEL_NAME,
    instruction=LEGAL_SYSTEM_PROMPT,
    tools=[rag_tools.analyze_contract_clause],
    output_key="legal_agent_result",
)
