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

# Fetch the Main Project for project number use
data "google_project" "main_project" {
  depends_on = [
    google_project_service.serviceusage_api,
  ]
  project_id = var.project_id
}

# Create Legal Contract GCS Bucket
resource "google_storage_bucket" "gcs_bucket" {
  depends_on = [
    google_project_service.storage_api,
  ]
  name                        = local.final_gcs_bucket_name
  location                    = var.region
  uniform_bucket_level_access = true
  force_destroy               = true
}

# Permit Gemini to Read from GCS Buckets
resource "google_storage_bucket_iam_member" "vertex_legal_bucket_viewer" {
  depends_on = [
    google_project_service.iam_manager_api,
    google_project_service.storage_api,
    google_project_service.aiplatform_api,
    google_storage_bucket.gcs_bucket,
  ]

  bucket = local.final_gcs_bucket_name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:service-${data.google_project.main_project.number}@gcp-sa-aiplatform.iam.gserviceaccount.com"
}

# Create A2A Card GCS Bucket
resource "google_storage_bucket" "a2a_card_bucket" {
  depends_on = [
    google_project_service.storage_api,
  ]
  name                        = local.final_a2a_card_bucket_name
  location                    = var.region
  uniform_bucket_level_access = true
  force_destroy               = true
}
