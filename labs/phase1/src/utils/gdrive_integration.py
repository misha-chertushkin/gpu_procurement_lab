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

import json
import os
import io
import logging
import google.auth
from typing import Dict, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Handles uploading reports to Google Drive.
    Uses Application Default Credentials (ADC) for authentication.
    """

    def __init__(self, folder_id: Optional[str] = None):
        """
        Initialize the ReportGenerator.

        Args:
            folder_id (str, optional): Google Drive folder ID where reports should be uploaded.
            If None, uploads to the root of "My Drive".
        """
        self.folder_id = folder_id
        self.sync_dir = "./gdrive_sync"  # Local backup directory
        os.makedirs(self.sync_dir, exist_ok=True)
        self._service = None

    def _get_drive_service(self):
        """
        Create and return a Google Drive API service instance.
        Uses Application Default Credentials.
        """
        if self._service is not None:
            return self._service

        try:
            # Use Application Default Credentials
            credentials, project = google.auth.default(
                scopes=['https://www.googleapis.com/auth/drive.file']
            )

            self._service = build('drive', 'v3', credentials=credentials)
            logger.info("Successfully authenticated with Google Drive API")
            return self._service

        except Exception as e:
            logger.error(f"Failed to authenticate with Google Drive: {e}")
            raise

    def upload_report(self, filename: str, content: str, metadata: Dict = None) -> str:
        """
        Uploads the Executive Report to Google Drive.

        Args:
            filename (str): The name of the report file.
            content (str): The full text/markdown content of the report.
            metadata (Dict): Additional metadata (e.g., agent version).

        Returns:
            str: Success message with file ID or error message.
        """
        # Save a local backup first
        try:
            local_path = os.path.join(self.sync_dir, filename)
            with open(local_path, "w") as f:
                if metadata:
                    f.write(f"--- METADATA ---\n{json.dumps(metadata, indent=2)}\n----------------\n\n")
                f.write(content)
            logger.info(f"Local backup saved to {local_path}")
        except Exception as e:
            logger.warning(f"Failed to save local backup: {e}")

        # Try to upload to Google Drive
        try:
            service = self._get_drive_service()

            # Prepare file content
            full_content = content
            if metadata:
                full_content = f"--- METADATA ---\n{json.dumps(metadata, indent=2)}\n----------------\n\n{content}"

            # Create file metadata
            file_metadata = {
                'name': filename,
                'mimeType': 'text/markdown'
            }

            # If folder_id is specified, upload to that folder
            if self.folder_id:
                file_metadata['parents'] = [self.folder_id]

            # Create media upload
            media = MediaIoBaseUpload(
                io.BytesIO(full_content.encode('utf-8')),
                mimetype='text/markdown',
                resumable=True
            )

            # Upload the file
            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink'
            ).execute()

            file_id = file.get('id')
            web_link = file.get('webViewLink', 'N/A')

            logger.info(f"Successfully uploaded to Google Drive: {filename} (ID: {file_id})")

            return (
                f"SUCCESS: Report uploaded to Google Drive\n"
                f"  - File ID: {file_id}\n"
                f"  - File Name: {filename}\n"
                f"  - Web Link: {web_link}\n"
                f"  - Local Backup: {local_path}"
            )

        except HttpError as error:
            error_msg = f"Google Drive API error: {error}"
            logger.error(error_msg)
            return (
                f"EXCEPTION: Could not upload to Google Drive ({error})\n"
                f"  - Local backup available at: {local_path}"
            )
        except Exception as e:
            error_msg = f"Unexpected error during upload: {str(e)}"
            logger.error(error_msg)
            return (
                f"EXCEPTION: Could not upload report ({str(e)})\n"
                f"  - Local backup available at: {local_path}"
            )