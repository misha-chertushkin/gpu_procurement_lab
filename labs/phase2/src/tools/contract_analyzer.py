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

from google.cloud import storage
import vertexai
from vertexai.generative_models import GenerativeModel, Part
from utils.config import config


class ContractAnalyzer:
    def __init__(self):
        vertexai.init(project=config.PROJECT_ID, location=config.REGION)
        self.model = GenerativeModel("gemini-3-pro-preview")
        self.storage_client = storage.Client()

    def analyze_contract_clause(self, doc_name: str, clause_type: str) -> str:
        """
        Analyzes the given legal document and extracts the specified clause.

        Args:
            doc_name (str): The filename in GCS (e.g., 'Master_Supply_Agreement.pdf').
            clause_type (str): The specific clause to look for (e.g., 'Exclusivity', 'Force Majeure').

        Returns:
            str: The extraction and interpretation of the clause.
        """

        gcs_uri = f"gs://{config.BUCKET_NAME}/{doc_name}"

        prompt = f"""
        You are a specialized legal assistant.
        Analyze the provided document specifically for the '{clause_type}' clause.
        
        If the clause exists:
        1. Quote it directly.
        2. Interpret its conditions (e.g., timeframes, exceptions).
        
        If it does not exist, state "No such clause found."
        """

        try:
            # Loading the file as a Part for multimodal processing
            document = Part.from_uri(uri=gcs_uri, mime_type="application/pdf")
            response = self.model.generate_content([document, prompt])
            return response.text
        except Exception as e:
            return f"Error analyzing contract: {str(e)}"
