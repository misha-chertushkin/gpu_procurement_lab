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
from typing import List
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class FileSystemTools:
    def __init__(self, root_dir: str = "./workspace"):
        """
        Initialize with a root directory to sandbox the agent's file access.
        """
        self.root_dir = os.path.abspath(root_dir)
        os.makedirs(self.root_dir, exist_ok=True)

    def _get_safe_path(self, filename: str) -> str:
        """
        Sanitizes the path to ensure it stays within the root_dir.
        """
        # Prevent directory traversal attacks
        if ".." in filename or filename.startswith("/"):
            raise ValueError(f"Security Error: Access to {filename} is forbidden.")

        return os.path.join(self.root_dir, filename)

    def list_files(self) -> List[str]:
        """
        Lists all files in the current workspace.
        """
        log.info(f"[🔧 list_files] Listing files in {self.root_dir}")
        try:
            result = os.listdir(self.root_dir)
            log.info("[✅ list_files] Success")
            return result
        except Exception as e:
            log.error(f"[❌ list_files] Error listing files: {str(e)}")
            return [f"Error listing files: {str(e)}"]

    def read_file(self, filename: str) -> str:
        """
        Reads the content of a specific file.
        """
        log.info(f"[🔧 read_file] Reading {filename}")
        safe_path = self._get_safe_path(filename)
        if not os.path.exists(safe_path):
            log.error(f"[❌ read_file] File {filename} does not exist.")
            return f"Error: File {filename} does not exist."

        try:
            with open(safe_path, "r") as f:
                result = f.read()
                log.info("[✅ read_file] Success")
                return result
        except Exception as e:
            log.error(f"[❌ read_file] Error reading file: {str(e)}")
            return f"Error reading file: {str(e)}"

    def append_to_log(self, filename: str, content: str) -> str:
        """
        Appends text to a file. Useful for maintaining a running log or tracker.
        """
        log.info(f"[🔧 append_to_log] Addending to {filename}")
        safe_path = self._get_safe_path(filename)
        try:
            with open(safe_path, "a") as f:
                f.write(content + "\n")
            log.info(f"[✅ append_to_log] Success: Appended to {filename}.")
            return f"Success: Appended to {filename}."
        except Exception as e:
            log.error(f"[❌ append_to_log] Error appending to file: {str(e)}")
            return f"Error appending to file: {str(e)}"

    def write_file(self, filename: str, content: str) -> str:
        """
        Overwrites a file with new content. 
        """
        log.info(f"[🔧 write_file] Writing to {filename}")
        safe_path = self._get_safe_path(filename)
        try:
            with open(safe_path, "w") as f:
                f.write(content)
            log.info(f"[✅ write_file] Success: File {filename} created/overwritten.")
            return f"Success: File {filename} created/overwritten."
        except Exception as e:
            log.error(f"[❌ write_file] Error writing file: {str(e)}")
            return f"Error writing file: {str(e)}"
