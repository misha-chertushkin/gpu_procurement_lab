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


gcs_a2a_bucket = os.getenv('AGENT_CARD_BUCKET_URI')


# Agent
def create_agent():
    """
    Factory function to create the root agent.
    """
    agent_cards = retrieve_agent_cards()
    remote_agents = get_remote_agents(agent_cards=agent_cards)
    log.info(f"Remote agents: {remote_agents}")

    all_agents = remote_agents

    # Dynamically construct the description and instructions from remote agents
    instructions = [
        "Always use the most relevant tool or sub-agent to respond to user utterances.\n\n"
        "Tools:\n\n",
        "   N/A\n\n\n",
        "Sub-Agents:\n\n",
    ]

    for i, agent in enumerate(all_agents):
        instructions.append(
            f"{i+1}. **{agent.name}**: Use this agent when you need: {agent.description}.\n"
        )

    instruction = "\n".join(instructions) + "\nStart by greeting the user and asking how you can help them today."

    return Agent(
        name="root_agent",
        model=config.MODEL_NAME,
        description=(
            "A helpful AI agent that orchestrates and executes tasks across its sub-agents"
        ),
        instruction=instruction,
        sub_agents=[*all_agents],
    )
