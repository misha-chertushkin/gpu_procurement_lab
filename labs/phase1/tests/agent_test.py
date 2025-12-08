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
        347
    ),
]


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
def test_run(qty, run_number):
    log.info(f"[🚀 System]: Launching test run {run_number}...")
    log.info(f"[📝 Qty]: {qty}")
    log.info(f"[☁️ Project]: {PROJECT_ID}, Region: {LOCATION}")

    _, _ = google.auth.default()
    _ = genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location=LOCATION,
    )

    asyncio.run(run_agent(qty))
    