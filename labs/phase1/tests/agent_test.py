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


from opentelemetry import trace
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.sdk.trace import export
from opentelemetry.sdk.trace import TracerProvider


from agent import run_agent


# Configure Logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("google_adk").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger(__name__)




load_dotenv()




parameterized_test_data = [
   (
       500
   ),
]


global report_path
report_path = "./workspace/gdrive_sync/Executive_Report.md"




PROJECT_ID = os.getenv("PROJECT_ID", "unset")
LOCATION = os.getenv("LOCATION", "us-central1")
MAX_STEPS = int(os.getenv("MAX_STEPS", 100))


provider = TracerProvider()
processor = export.BatchSpanProcessor(
   CloudTraceSpanExporter(project_id=PROJECT_ID)
)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)




# Run parameterized tests N times
N = int(os.getenv("TEST_COUNT", 1))
@pytest.mark.parametrize(
   "run_number",
   range(N),
)
@pytest.mark.parametrize(
   "qty",
   parameterized_test_data,
)
class TestAgentRun:
   report_content = ""
   tracker_rows = []
      


   @pytest.mark.order(1)
   def test_run_agent(self, qty, run_number):
       log.info(f"[🚀 System]: Launching test run {run_number}...")
       log.info(f"[📝 Qty]: {qty}")
       log.info(f"[☁️ Project]: {PROJECT_ID}, Region: {LOCATION}")


       global report_path


       _, _ = google.auth.default()
       _ = genai.Client(
           vertexai=True,
           project=PROJECT_ID,
           location=LOCATION,
       )


       # Clean temp resources
       if os.path.exists(report_path):
           os.remove(report_path)




       run_agent(500)


       if not os.path.exists(report_path):
           pytest.fail("CRITICAL: Report not found. Connectivity to GDrive failed.")
       with open(report_path, "r") as f:
           TestAgentRun.report_content = f.read()




   @pytest.mark.order(2)
   def test_inventory_units(self, qty, run_number):
       """Did it find the 300 units in LEGACY_INV_MAIN_V2 with LOC_BIN_HEX='55'?"""
       has_count = "300" in TestAgentRun.report_content
       assert has_count, "FAIL: Report did not mention finding 300 units."


   @pytest.mark.order(3)
   def test_inventory_loc_bin_hex(self, qty, run_number):
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
   def test_legal_justification(self, qty, run_number):
       """Did it cite Clause 7.B from the Nvidia contract?"""
       lower_content = TestAgentRun.report_content.lower()
       has_clause = ("7.b" in lower_content
                     or "7" in lower_content
                     or "7." in lower_content
                     or "7 ." in lower_content
                     or "7b" in lower_content
                     or "7(b)" in lower_content
                     or "force majeure" in lower_content
                     or "section 7" in lower_content)
       assert has_clause, "FAIL: Legal justification (Clause 7.B / Force Majeure) missing."


   @pytest.mark.order(5)
   def test_procurement_recommendation(self, qty, run_number):
       """Did it recommend buying 200 units from the spot market?"""
       procurement_regex = r"(?:purchase|order|buy|procure|units|source|requirement of|recommend\s+(?:to\s+)?purchasing|purchase\s+order\s+for)\s.*?\b(\d+)\b\s.*?(?:H100|units)"
       buy_matches = re.findall(procurement_regex, TestAgentRun.report_content.lower())
       is_correct_amount = ("200" in buy_matches)


       assert is_correct_amount, f"FAIL: Recommendation was not 200 units. Found: {buy_matches}"


