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


""" def create_contract_pdf(filename: str):
    " ""
    Generates a PDF with the specific conflicting clauses required for the lab.
    " ""
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "MASTER SUPPLY AGREEMENT")
    c.setFont("Helvetica", 10)
    c.drawString(
        50, height - 70, "BETWEEN: NVIDIA CORP (Supplier) AND GLOBAL TECH INC (Buyer)"
    )
    c.drawString(50, height - 85, "DATE: 2024-01-01")

    # Clause 4: The Restriction (Exclusivity)
    # The Naive Agent is expected to struggle with this
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 150, "4. EXCLUSIVITY AND SOURCING")
    c.setFont("Helvetica", 11)
    text_4 = [
        "4.1 Buyer agrees to purchase 100% of its required H100 GPU units exclusively",
        "from Supplier.",
        "4.2 Purchase from unauthorized third-party resellers (scalpers, spot market)",
        "is strictly prohibited and constitutes a material breach of contract.",
    ]
    y = height - 170
    for line in text_4:
        c.drawString(50, y, line)
        y -= 15

    # Clause 7: The Loophole (Force Majeure) - his is what the Legal Agent must find.
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y - 30, "7. NON-PERFORMANCE AND EXCEPTIONS")
    y -= 50
    c.setFont("Helvetica", 11)
    text_7 = [
        "7.A Standard delays shall not void the exclusivity agreement.",
        # The Critical Clause 7.B mentioned in the Golden Set
        "7.B EXCEPTION: If Supplier fails to deliver confirmed orders within sixty (60)",
        "days of the scheduled delivery date, the Exclusivity requirement (Clause 4)",
        "shall be temporarily suspended.",
        "7.C In such events (7.B), Buyer is permitted to source deficit units from",
        "third-party vendors until Supplier inventory stabilizes.",
    ]

    for line in text_7:
        c.drawString(50, y, line)
        y -= 15

    c.save()
    print(f"📄 Generated local PDF: {filename}")


 """


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
