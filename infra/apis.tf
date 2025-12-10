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

# Enable the Cloud Resource Manager API
resource "google_project_service" "cloudresourcemanager_api" {
  service            = "cloudresourcemanager.googleapis.com"
  disable_on_destroy = false
}

# Enable the BigQuery API
resource "google_project_service" "bigquery_api" {
  service            = "bigquery.googleapis.com"
  disable_on_destroy = false
}

# Enable the Vertex AI Platform API
resource "google_project_service" "aiplatform_api" {
  service            = "aiplatform.googleapis.com"
  disable_on_destroy = false
}

# Enable the Google Drive API
resource "google_project_service" "drive_api" {
  service            = "drive.googleapis.com"
  disable_on_destroy = false
}

# Enable the Identity and Access Management API
resource "google_project_service" "iam_manager_api" {
  service            = "iam.googleapis.com"
  disable_on_destroy = false
}

# Enable the Storage API
resource "google_project_service" "storage_api" {
  service            = "storage.googleapis.com"
  disable_on_destroy = false
}

# Enable the Service Usage API
resource "google_project_service" "serviceusage_api" {
  service            = "serviceusage.googleapis.com"
  disable_on_destroy = false
}

# Enable the Telemetry API
resource "google_project_service" "telemetry_api" {
  service            = "telemetry.googleapis.com"
  disable_on_destroy = false
}

# Enable the Cloud Logging API
resource "google_project_service" "logging_api" {
  service            = "logging.googleapis.com"
  disable_on_destroy = false
}

# Enable the Cloud Trace API
resource "google_project_service" "cloudtrace_api" {
  service            = "cloudtrace.googleapis.com"
  disable_on_destroy = false
}

# Enable the Cloud Monitoring API
resource "google_project_service" "monitoring_api" {
  service            = "monitoring.googleapis.com"
  disable_on_destroy = false
}
