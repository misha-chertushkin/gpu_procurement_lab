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
import pytest

import asyncio
import logging

from typing import AsyncGenerator
from google.adk.events.event import Event
from google.adk.agents import parallel_agent

from dotenv import load_dotenv
import google.auth
from google import genai
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from opentelemetry import trace
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.sdk.trace import export
from opentelemetry.sdk.trace import TracerProvider

from agents.commander.agent import root_agent

# Configure Logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("google_adk").setLevel(logging.DEBUG)
logging.getLogger("httpx").setLevel(logging.WARNING)


# --- BEGIN MONKEY PATCH ---
async def _merge_agent_run_patched(
    agent_runs: list[AsyncGenerator[Event, None]],
) -> AsyncGenerator[Event, None]:
    """Merges the agent run event generator.

    This implementation guarantees for each agent, it won't move on until the
    generated event is processed by upstream runner.

    Args:
        agent_runs: A list of async generators that yield events from each agent.

    Yields:
        Event: The next event from the merged generator.
    """
    sentinel = object()
    queue = asyncio.Queue()

    # Agents are processed in parallel.
    # Events for each agent are put on queue sequentially.
    async def process_an_agent(events_for_one_agent):
        try:
            async for event in events_for_one_agent:
                resume_signal = asyncio.Event()
                await queue.put((event, resume_signal))
                # Wait for upstream to consume event before generating new events.
                await resume_signal.wait()
        finally:
            # Mark agent as finished.
            await queue.put((sentinel, None))

    async with asyncio.TaskGroup() as tg:
        for events_for_one_agent in agent_runs:
            tg.create_task(process_an_agent(events_for_one_agent))

        sentinel_count = 0
        # Run until all agents finished processing.
        try:
            while sentinel_count < len(agent_runs):
                event, resume_signal = await queue.get()
                # Agent finished processing.
                if event is sentinel:
                    sentinel_count += 1
                else:
                    yield event
                    # Signal to agent that it should generate next event.
                    resume_signal.set()
        except GeneratorExit:
            pass # Gracefully exit when the generator is closed.


parallel_agent._merge_agent_run = _merge_agent_run_patched
# --- END MONKEY PATCH ---


load_dotenv()


parameterized_test_data = [
    (
        "Start the investigation. Find me 500 H100s."
    ),
]


PROJECT_ID = os.getenv("PROJECT_ID", "unset")
LOCATION = os.getenv("LOCATION", "us-central1")
MAX_STEPS = int(os.getenv("MAX_STEPS", 30))

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "1"
os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID
os.environ["GOOGLE_CLOUD_LOCATION"] = LOCATION

os.environ["OTEL_SERVICE_NAME"] = "labs-phase1"
os.environ["OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED"] = "true"
os.environ["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] = "true"
#os.environ["ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS"] = "false"

provider = TracerProvider()
processor = export.BatchSpanProcessor(
    CloudTraceSpanExporter(project_id=PROJECT_ID)
)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

async def call_agent_async(prompt: str|Content):
    # Initialize the ADK runtime components
    session_service = InMemorySessionService()

    runner = Runner(
        agent=root_agent, app_name="root_agent", session_service=session_service
    )

    # Create a session using the service
    session = await session_service.create_session(
        app_name="root_agent", user_id="default_user"
    )

    # Prepare the input message
    if isinstance(prompt, str):
        message = Content(role="user", parts=[Part(text=prompt)])
    else: # is Content
        message = prompt

    print(f"🛑 [System] Safety Limit set to {MAX_STEPS} steps.")
    step_count = 0

    # Run the agent and print the response
    async for event in runner.run_async(
        session_id=session.id, user_id="default_user", new_message=message
    ):
        step_count += 1
        
        if step_count > MAX_STEPS:
            print(f"\n❌ [System] TERMINATING: Hit max step limit ({MAX_STEPS}).")
            print("   Likely cause: Infinite loop due to recurring tool errors (404/Connection Refused).")
            break  # Force exit

        if event.is_final_response():
            # Check if there is actual text content
            if event.content and event.content.parts:
                print(f"\n🤖 [{root_agent.name}]: {event.content.parts[0].text}")
            else:
                print("\n🤖 [{root_agent.name}]: (Returned final response with no text)")
            break 
            
        # If it's not final, the agent is thinking/calling tools
        print(f"   ⚙️ [System] Step {step_count}: Processing...")


# Run parameterized tests N times
N = int(os.getenv("TEST_COUNT", 1))
@pytest.mark.parametrize(
    "run_number",
    range(N),
)
@pytest.mark.parametrize(
    "prompt",
    parameterized_test_data,
)
def test_run(prompt, run_number):
    print(f"🚀 [root_agent] Launching test run {run_number}...")
    print(f"📝 Prompt: {prompt}")

    _, _ = google.auth.default()
    print(f"☁️ Project: {PROJECT_ID}, Region: {LOCATION}")

    _ = genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location=LOCATION,
    )

    asyncio.run(call_agent_async(prompt))
    