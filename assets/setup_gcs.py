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
from config import config

from assets.generate_assets import create_vendor_contract, create_warehouse_manual


def setup_gcs():
    client = storage.Client(project=config.PROJECT_ID)
    bucket_name = config.BUCKET_NAME

    # 1. Check if Bucket exists
    try:
        bucket = client.bucket(bucket_name)
        if not bucket.exists():
            print(f"❌ Bucket {bucket_name} does not exist.  Please initialize the environment.")
            return
        else:
            print(f"✅ Bucket {bucket_name} already exists.")
    except Exception as e:
        print(f"❌ Error setting up bucket: {e}")
        return

    # 2. Generate PDFs
    pdf_filename = "Master_Supply_Agreement_NVIDIA.pdf"
    create_vendor_contract(pdf_filename)

    pdf_warehouse_filename = "Warehouse_Policy_Manual_1998.pdf"
    create_warehouse_manual(pdf_warehouse_filename)

    # 3. Upload PDFs
    try:
        blob = bucket.blob(pdf_filename)
        blob.upload_from_filename(f"./assets/docs/{pdf_filename}")
        print(f"🚀 Uploaded {pdf_filename} to gs://{bucket_name}/")

        blob2 = bucket.blob(pdf_warehouse_filename)
        blob2.upload_from_filename(f"./assets/docs/{pdf_warehouse_filename}")
        print(f"🚀 Uploaded {pdf_warehouse_filename} to gs://{bucket_name}/")

    except Exception as e:
        print(f"❌ Failed to upload PDFs: {e}")


if __name__ == "__main__":
    setup_gcs()
