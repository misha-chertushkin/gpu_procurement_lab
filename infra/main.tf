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

# 1. The Dataset
resource "google_bigquery_dataset" "dataset" {
  dataset_id                 = var.dataset_id
  friendly_name              = "GPU Procurement Legacy DB"
  description                = "The opaque legacy database for the L400 Lab"
  location                   = "US"
  delete_contents_on_destroy = true
}

# 2. Table 1: The Messy Inventory (Schema from Phase 1 Design)
resource "google_bigquery_table" "inventory" {
  dataset_id          = google_bigquery_dataset.dataset.dataset_id
  table_id            = "LEGACY_INV_MAIN_V2"
  deletion_protection = false

  schema = <<EOF
[
  {
    "name": "ITEM_REF_ID",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "Internal Product Reference ID"
  },
  {
    "name": "LOC_BIN_HEX",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "Hex location code. 55=Quarantine, A1=Shipping"
  },
  {
    "name": "QOH_RAW_VAL",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Quantity on Hand (Raw Value)"
  },
  {
    "name": "LAST_TOUCH_DT_UNIX",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Unix Timestamp"
  },
  {
    "name": "STATUS_FLAG_9",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Status Flag: 0=OK, 9=Legal Hold"
  }
]
EOF
}

# 3. Table 2: The Rosetta Stone Catalog
resource "google_bigquery_table" "catalog" {
  dataset_id          = google_bigquery_dataset.dataset.dataset_id
  table_id            = "REF_CATALOG_DUMP"
  deletion_protection = false

  schema = <<EOF
[
  {
    "name": "REF_ID",
    "type": "STRING",
    "mode": "NULLABLE"
  },
  {
    "name": "HUMAN_READABLE_NAME",
    "type": "STRING",
    "mode": "NULLABLE"
  },
  {
    "name": "MANUFACTURER",
    "type": "STRING",
    "mode": "NULLABLE"
  }
]
EOF
}

# 4. Data Seeding (The "Hidden" 300 Units)
# We use a query job to perform the INSERTs.
resource "google_bigquery_job" "seed_inventory" {
  job_id   = "seed_inventory_${formatdate("YYYYMMDDhhmmss", timestamp())}"
  location = "US"

  lifecycle {
    ignore_changes = [
      job_id,
    ]
  }

  query {
    query = <<EOT
      INSERT INTO `${var.project_id}.${var.dataset_id}.${google_bigquery_table.inventory.table_id}` 
      (ITEM_REF_ID, LOC_BIN_HEX, QOH_RAW_VAL, LAST_TOUCH_DT_UNIX, STATUS_FLAG_9)
      VALUES
      -- The Golden Set Success Condition: 300 units in Quarantine (55) with Legal Hold (9)
      ('REF_9982_X', '55', 300, 1715625600, '9'), 
      -- Decoy data
      ('REF_9982_X', 'A1', 0, 1715620000, '0'),
      ('REF_1002_A', 'B2', 5000, 1715500000, '0')
    EOT

    create_disposition = ""
    write_disposition  = ""
  }

  depends_on = [google_bigquery_table.inventory]
}

resource "google_bigquery_job" "seed_catalog" {
  job_id   = "seed_catalog_${formatdate("YYYYMMDDhhmmss", timestamp())}"
  location = "US"

  lifecycle {
    ignore_changes = [
      job_id,
    ]
  }

  query {
    query              = <<EOT
      INSERT INTO `${var.project_id}.${var.dataset_id}.${google_bigquery_table.catalog.table_id}` 
      (REF_ID, HUMAN_READABLE_NAME, MANUFACTURER)
      VALUES
      ('REF_9982_X', 'H100 GPU Tensor Core', 'NVIDIA'),
      ('REF_1002_A', 'Standard Power Cable', 'Generic')
    EOT
    create_disposition = ""
    write_disposition  = ""
  }

  depends_on = [google_bigquery_table.catalog]
}