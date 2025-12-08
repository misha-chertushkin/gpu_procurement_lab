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
import json
from dotenv import load_dotenv
from google.cloud.storage import Client
from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from a2a.client.transports.jsonrpc import JsonRpcTransport
from a2a.types import AgentCard
import aiohttp
from typing import List, Dict, Any
from httpx import AsyncClient
import google.auth
import google.auth.transport.requests
import google.oauth2.id_token
from urllib.parse import urlparse
from assets.config import config


load_dotenv()


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def get_id_token(url: str):
    """Retrieves an ID token for a given URL audience."""
    parsed_url = urlparse(url)
    audience = f"{parsed_url.scheme}://{parsed_url.netloc}"
    auth_request = google.auth.transport.requests.Request()
    id_token = google.oauth2.id_token.fetch_id_token(auth_request, audience)
    return id_token


gcs_a2a_bucket = os.getenv('AGENT_CARD_BUCKET_URI', 'unset')
agent_card_bucket_name = gcs_a2a_bucket.replace("gs://", "")


# BEGIN RUNTIME-PATCH
# Ensures Authorization Bearer token is refreshed for every request.
async def new_jsonrpc_send_request(
    self,
    rpc_request_payload: dict[str, Any],
    http_kwargs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    A temporary override for JsonRpcTransport._send_request that uses aiohttp.
    """
    log.info(f"Using custom aiohttp _send_request for URL: {self.url}")

    final_kwargs = http_kwargs or {}
    
    # Correctly merge base headers from the client with request-specific headers
    final_headers = dict(self.httpx_client.headers.items())
    request_headers = final_kwargs.pop('headers', {})
    final_headers.update(request_headers)

    # Ensure fresh token used for all requests.
    stripped_url = self.url.replace(':443', '')
    final_headers["Authorization"] = f"Bearer {get_id_token(stripped_url)}"

    async with aiohttp.ClientSession() as session:
        async with session.post(
            self.url, 
            json=rpc_request_payload, 
            headers=final_headers, 
            **final_kwargs
        ) as response:
            response.raise_for_status()
            return await response.json()

JsonRpcTransport._send_request = new_jsonrpc_send_request
log.info("JsonRpcTransport._send_request has been successfully monkey-patched to use aiohttp.")
# END RUNTIME-PATCH


def get_gcs_cards() -> List[Dict[str, Any]]:
    """
    Downloads all files from a GCS bucket, assuming they are JSON,
    and converts them into a list of Python dictionaries.

    Returns:
        A list where each item is a dictionary parsed from a file.
        Files that are not valid JSON will be skipped.
    """
    # Initialize the GCS client
    storage_client = Client(project=config.PROJECT_ID)
        
    # Get the bucket object
    bucket = storage_client.bucket(agent_card_bucket_name)
        
    # List all blobs (files) in the bucket
    blobs = bucket.list_blobs()
    all_cards = []
    log.info(f"Fetching files from bucket '{agent_card_bucket_name}'...")

    for blob in blobs:
        try:
            json_string = blob.download_as_string()
            agent_card = json.loads(json_string)
            all_cards.append(agent_card)
        except json.JSONDecodeError:
            log.error(f"Could not decode JSON from {blob.name}. Skipping file.")
        except Exception as e:
            log.error(f"An error occurred with {blob.name}: {e}. Skipping file.")
        
    return all_cards

def retrieve_agent_cards() -> List[AgentCard]:
    try:
        agent_cards = []
        cards_payload = get_gcs_cards()
        log.info(f"GCS CARDS PAYLOAD: {cards_payload}")
        for card in cards_payload:
            agent_cards.append(
                AgentCard.model_validate(card)
            )
        return agent_cards
    except Exception as e:
        log.error(f"Encountered an error when attempting to retrieve agent card from gs://{agent_card_bucket_name}: {e}")
        raise e

def get_remote_agents(agent_cards: List[AgentCard]) -> List[RemoteA2aAgent]:
    """
    Creates a RemoteA2aAgent for each agent card, ensuring each agent
    has its own httpx.AsyncClient with correct auth headers.
    """
    global _async_clients
    remote_agents = []

    for card in agent_cards:
        no_port_url = ':'.join(card.url.split(':')[:-1]) # remove the port
        url = no_port_url + AGENT_CARD_WELL_KNOWN_PATH
        log.info(f"URL for Agent Card: {url}")

        headers = {
            "Authorization": f"Bearer {get_id_token(url)}",
            "x-goog-user-project": config.PROJECT_ID,
        }

        httpx_client = AsyncClient(headers=headers)
        remote_agent = RemoteA2aAgent(
            name=card.name,
            description=card.description,
            agent_card=card,
            httpx_client=httpx_client
        )

        remote_agents.append(remote_agent)

    return remote_agents
