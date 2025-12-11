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
import re
import csv
from dotenv import load_dotenv
import google.auth
from google import genai
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.utils.context_utils import Aclosing
from google.genai.types import Content, Part

from opentelemetry import trace
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.sdk.trace import export
from opentelemetry.sdk.trace import TracerProvider

from agents.a2a_root.agent import root_agent

# Configure Logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("google_adk").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger(__name__)


load_dotenv()


parameterized_test_data = [
    (
        "Find me 500 H100s ASAP"
    ),
]

global report_path
global tracker_path
report_path = "./workspace/gdrive_sync/Executive_Report.md"
tracker_path = "./workspace/procurement_tracker.csv"


PROJECT_ID = os.getenv("PROJECT_ID", "unset")
LOCATION = os.getenv("LOCATION", "us-central1")
MAX_STEPS = int(os.getenv("MAX_STEPS", 100))

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

    log.info(f"[🛑 System] Safety Limit set to {MAX_STEPS} steps.")
    step_count = 0

    # Run the agent and print the response
    async with Aclosing(runner.run_async(
        session_id=session.id, user_id="default_user", new_message=message
    )) as agen:
        async for event in agen:
            step_count += 1
            
            if step_count > MAX_STEPS:
                log.error(f"[❌ System] TERMINATING: Hit max step limit ({MAX_STEPS}).")
                break  # Force exit

            if event.is_final_response():
                # Check if there is actual text content
                if event.content and event.content.parts:
                    log.info(f"[🤖 {event.author}]: {event.content.parts[0].text}")
                else:
                    log.info(f"[🤖 {event.author}]: (Returned final response with no text)")
                
            # If it's not final, the agent is thinking/calling tools
            log.info(f"[⚙️  System] Step {step_count}: Processing...")


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
class TestAgentRun:
    report_content = ""
    tracker_rows = []
        

    @pytest.mark.order(1)
    def test_run_agent(self, prompt, run_number):
        log.info(f"[🚀 System]: Launching test run {run_number}...")
        log.info(f"[📝 Prompt]: {prompt}")
        log.info(f"[☁️ Project]: {PROJECT_ID}, Region: {LOCATION}")

        global report_path
        global tracker_path

        _, _ = google.auth.default()
        _ = genai.Client(
            vertexai=True,
            project=PROJECT_ID,
            location=LOCATION,
        )

        # Clean temp resources
        if os.path.exists(report_path):
            os.remove(report_path)

        if os.path.exists(tracker_path):
            os.remove(tracker_path)

        asyncio.run(call_agent_async(prompt))

        if not os.path.exists(report_path):
            pytest.fail("CRITICAL: Report not found. Connectivity to GDrive failed.")
        with open(report_path, "r") as f:
            TestAgentRun.report_content = f.read()

        if not os.path.exists(tracker_path):
            pytest.fail("CRITICAL: Procurement Tracker CSV not found. Agent failed to maintain state.")
        with open(tracker_path, "r") as f:
            reader = csv.reader(f)
            TestAgentRun.tracker_rows = list(reader)

    @pytest.mark.order(2)
    def test_inventory_units(self, prompt, run_number):
        """Did it find the 300 units in LEGACY_INV_MAIN_V2 with LOC_BIN_HEX='55'?"""
        has_count = "300" in TestAgentRun.report_content
        assert has_count, "FAIL: Report did not mention finding 300 units."

    @pytest.mark.order(3)
    def test_inventory_loc_bin_hex(self, prompt, run_number):
        """Did it find LOC_BIN_HEX='55'?"""
        lower_content = TestAgentRun.report_content.lower()
        has_loc = ("55" in lower_content
            or "legal" in lower_content
            or "on hold" in lower_content
            or "quarantine" in lower_content
            or "hold legal" in lower_content
            or "legal hold" in lower_content)
        assert has_loc, "FAIL: Report did not identify the Quarantine/Hex-55 location."

    @pytest.mark.order(4)
    def test_legal_justification(self, prompt, run_number):
        """Did it cite Clause 7.B from the Nvidia contract?"""
        lower_content = TestAgentRun.report_content.lower()
        has_clause = ("7.b" in lower_content
                      or "7b" in lower_content
                      or "7(b)" in lower_content
                      or "force majeure" in lower_content
                      or "section 7" in lower_content)
        assert has_clause, "FAIL: Legal justification (Clause 7.B / Force Majeure) missing."

    @pytest.mark.order(5)
    def test_procurement_recommendation(self, prompt, run_number):
        """Did it recommend buying ONLY 200 units from the spot market?"""
        procurement_regex = r"(?:purchase|order|buy|procure|source|requirement of|recommend\s+(?:to\s+)?purchasing|purchase\s+order\s+for)\s.*?\b(\d+)\b\s.*?(?:H100|units)"
        buy_matches = re.findall(procurement_regex, TestAgentRun.report_content.lower())
        is_correct_amount = ("200" in buy_matches) and all(m == "200" for m in buy_matches)

        assert is_correct_amount, f"FAIL: Recommendation was not ONLY 200 units. Found: {buy_matches}"

    @pytest.mark.order(6)
    def test_tracker_integrity(self, prompt, run_number):
        """Validates the CSV structure and content."""
        header = [h.strip().lower() for h in TestAgentRun.tracker_rows[0]]
        assert "source" in header, "FAIL: CSV missing 'source' column"
        assert "quantity" in header, "FAIL: CSV missing 'quantity' column"

        found_internal = False
        for row in TestAgentRun.tracker_rows:
            row_str = str(row).lower().replace('-', ' ').replace('_', ' ')
            if "300" in row_str and (
                    "internal" in row_str
                    or "legal" in row_str
                    or "on hold" in row_str
                    or "quarantine" in row_str
                    or "hold legal" in row_str
                    or "legal hold" in row_str
                ):
                found_internal = True
                break
        assert found_internal, "FAIL: Tracker does not record the release of 300 internal units."

        found_spot = False
        for row in TestAgentRun.tracker_rows:
            row_str = str(row).lower()
            if "250" in row_str and ("spot" in row_str or "market" in row_str or "reseller" in row_str):
                found_spot = True
                break
        assert found_spot, "FAIL: Tracker does not record the availability of 250 spot units."

