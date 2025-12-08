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

from google import genai
from google.genai.types import Part, GenerateContentResponse
from assets.config import config
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class ContractAnalyzer:
    def __init__(self):
        self.client = genai.Client(vertexai=True, project=config.PROJECT_ID, location=config.REGION)

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
            log.info(f"[🔧 analyze_contract_clause] Reviewing Contract Clauses for GCS URI: {gcs_uri}")
            document = Part.from_uri(file_uri=gcs_uri, mime_type="application/pdf")
            response: GenerateContentResponse = self.client.models.generate_content(
                model=config.MODEL_NAME,
                contents=[document, prompt],
            )
            if not response.text:
                log.error("[❌ analyze_contract_clause] Empty contract analysis.  Something went wrong.")
                return "Empty contract analysis.  Something went wrong."
            
            log_text = response.text.replace('\n', ' ')
            log.info(f"[✅ analyze_contract_clause] Success: {log_text}")
            return response.text
        except Exception as e:
            log.error(f"[❌ analyze_contract_clause] Error analyzing contract: {str(e)}")
            return f"Error analyzing contract: {str(e)}"
