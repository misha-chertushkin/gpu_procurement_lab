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


export PROJECT_ID=${project_id}
export LOCATION=${location}
export GOOGLE_CLOUD_REGION=${location}
export GCS_BUCKET_NAME=${gcs_bucket_name}
export A2A_CARD_BUCKET_NAME=${a2a_card_bucket_name}

export GOOGLE_GENAI_USE_VERTEXAI="1"
export GOOGLE_CLOUD_PROJECT=${project_id}
export GOOGLE_CLOUD_LOCATION=${location}

export OTEL_SERVICE_NAME=l400-lab2
export OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true
export OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true
export ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS=true
