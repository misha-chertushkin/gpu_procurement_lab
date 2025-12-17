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

import os
import logging
from dotenv import load_dotenv
from google.adk.agents import Agent

from assets.utils.agents import get_remote_agents, retrieve_agent_cards
from assets.config import config


load_dotenv()


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


agent_card_bucket_name = os.getenv('A2A_CARD_BUCKET_NAME', 'unset')


# Agent
def create_agent():
    """
    Factory function to create the root agent.
    """
    # TODO (Task 3.1): Redacted the get_remote_agents function call.
    # This forces the student to understand the discovery process,
    # where agent metadata ('cards') is used to create remote proxy objects.
    remote_agents = []
    log.info(f"Remote agents: {remote_agents}")

    # Dynamically construct the description and instructions from remote agents
    instructions = [
        "Always use the most relevant tool or sub-agent to respond to user utterances.\n\n"
        "Tools:\n\n",
        "   N/A\n\n\n",
        "Sub-Agents:\n\n",
    ]

    # TODO (Task 3.2): Redacted the for loop that dynamically builds the agent's prompt.
    # This tests the concept of creating adaptive prompts that reflect runtime capabilities.

    instruction = "\n".join(instructions) + "\nStart by greeting the user and asking how you can help them today."

    # TODO (Task 3.3): Redacted the sub_agents=[*remote_agents] parameter.
    # This requires the student to understand how to dynamically register the discovered agent proxies with the orchestrator.
    return Agent(
        name="root_agent",
        model=config.MODEL_NAME,
        description=(
            "A helpful AI agent that orchestrates and executes tasks across its sub-agents"
        ),
        instruction=instruction,
        sub_agents=[],
    )

root_agent = create_agent()
