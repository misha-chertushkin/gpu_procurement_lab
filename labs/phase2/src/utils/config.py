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
import logging
import google.auth
from google.cloud import secretmanager
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConfigLoader:
    """
    Handles the logic of fetching config from:
    1. Environment Variables
    2. Google Secret Manager
    3. Google Auth Defaults (for Project ID)
    """

    def __init__(self):
        self._project_id = self._determine_project_id()
        self._secret_client = None  # Lazy init

    def _determine_project_id(self) -> str:
        """
        Tries to find the project ID from Env Vars, then Google Auth.
        """
        # 1. Check Env Var
        pid = os.getenv("GOOGLE_CLOUD_PROJECT")
        if pid:
            return pid

        # 2. Check Google Auth Default
        try:
            _, pid = google.auth.default()
            logger.info(f"Project ID detected via Google Auth: {pid}")
            return pid
        except Exception as e:
            logger.warning(f"Could not detect Project ID via Auth: {e}")

        # 3. Fallback (Only if absolutely necessary)
        return "your-fallback-project-id"

    def _get_secret(self, secret_id: str, version_id: str = "latest") -> str | None:
        """Fetches a secret from Google Cloud Secret Manager."""
        if not self._project_id:
            return None

        try:
            if not self._secret_client:
                self._secret_client = secretmanager.SecretManagerServiceClient()

            name = (
                f"projects/{self._project_id}/secrets/{secret_id}/versions/{version_id}"
            )
            response = self._secret_client.access_secret_version(request={"name": name})
            return response.payload.data.decode("UTF-8")
        except Exception as e:
            logger.debug(f"Secret '{secret_id}' not found in GSM: {e}")
            return None

    def get(self, key: str, default: str = None, secret_name: str = None) -> str:
        """
        Priority:
        1. Environment Variable
        2. Secret Manager (if secret_name provided)
        3. Default Value
        """
        # 1. Env Var
        value = os.getenv(key)
        if value:
            return value

        # 2. Secret Manager
        if secret_name:
            secret_val = self._get_secret(secret_name)
            if secret_val:
                logger.info(f"Loaded '{key}' from Secret Manager ('{secret_name}')")
                return secret_val

        # 3. Default
        if default:
            return default

        raise ValueError(f"Configuration missing for {key}. Checked Env and Secrets.")


# Instantiate the loader once
_loader = ConfigLoader()


# --- The Public Configuration Object ---
class ProjectConfig:
    # Infrastructure
    PROJECT_ID: str = _loader._project_id
    REGION: str = _loader.get("GOOGLE_CLOUD_REGION", "us-central1")

    # BigQuery Assets
    DATASET_ID: str = _loader.get("BIGQUERY_DATASET", "gpu_procurement_db")
    TABLE_INVENTORY: str = _loader.get("TABLE_INVENTORY", "LEGACY_INV_MAIN_V2")
    TABLE_CATALOG: str = _loader.get("TABLE_CATALOG", "REF_CATALOG_DUMP")

    # GCS Assets
    BUCKET_NAME: str = _loader.get(
        "GCS_BUCKET_NAME",
        default=f"{_loader._project_id}-gpu-procurement-docs",  # Good default naming convention
    )

    # Mock API (Cloud Run Service)
    # We default to localhost, but allow overriding via Secret/Env for the deployed URL
    API_BASE_URL: str = _loader.get(
        "MOCK_API_URL",
        default="http://localhost:8080",
        secret_name="GPU_PROCUREMENT_API_URL",
    )

    # Model Configuration
    MODEL_NAME: str = _loader.get("MODEL_NAME", default="gemini-3-pro-preview")


# Singleton instance
config = ProjectConfig()
