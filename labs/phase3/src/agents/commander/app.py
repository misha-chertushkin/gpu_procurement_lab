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

import os
from dotenv import load_dotenv
import logging

from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.a2a.utils.agent_card_builder import AgentCardBuilder

from .agent import create_agent
from assets.utils.agents import build_and_publish_agent_card


load_dotenv()


project_id = os.getenv('PROJECT_ID', 'unset')
location = os.getenv('LOCATION', 'unset')
service_port = int(os.getenv('LOCAL_SERVICE_PORT', '8081'))
gcs_a2a_bucket = os.getenv('A2A_CARD_BUCKET_URI', 'unset')


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


protocol = "http"
host = "127.0.0.1"
port = service_port
rpc_url = f"{protocol}://{host}:{port}/"
global a2a_card
a2a_card = None 
root_agent = create_agent()


app = to_a2a(agent=root_agent, host=host, port=port, protocol="http")
@app.on_event("startup")
async def lifespan_startup():
    """Builds the agent card and stores it in a global variable on startup."""
    global a2a_card
    card_builder = AgentCardBuilder(
        agent=root_agent,
        rpc_url=rpc_url,
    )
    a2a_card = await build_and_publish_agent_card(
        card_builder=card_builder,
        gcs_bucket_uri=gcs_a2a_bucket,
        agent=root_agent,
    )
    log.info("A2A agent started and published successfully")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=service_port)
