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

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

ASSET_DIR = "./assets/docs"
os.makedirs(ASSET_DIR, exist_ok=True)


def create_vendor_contract(filename: str):
    """Generates the Master Supply Agreement with the hidden loophole."""
    c = canvas.Canvas(
        os.path.join(ASSET_DIR, filename), pagesize=letter
    )
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


def create_warehouse_manual(filename: str):
    """Generates the 'Rosetta Stone' for the cryptic status codes."""
    c = canvas.Canvas(
        os.path.join(ASSET_DIR, filename), pagesize=letter
    )

    c.drawString(100, 750, "WAREHOUSE OPERATIONS MANUAL (REV 1998)")

    c.drawString(100, 700, "SECTION 4: STATUS CODES")
    c.drawString(100, 685, "CODE 0: Available for Pick")
    c.drawString(100, 670, "CODE 1: Reserved for VIP")
    c.drawString(100, 655, "CODE 9: LEGAL HOLD / QUARANTINE")
    c.drawString(
        100, 640, "   * Items with Code 9 are physically present but legally frozen."
    )
    c.drawString(100, 625, "   * release requires valid Override Authorization.")

    c.save()
    print("✅ Generated: Warehouse_Policy_Manual_1998.pdf")
