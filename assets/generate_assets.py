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


def create_vendor_contract():
    """Generates the Master Supply Agreement with the hidden loophole."""
    c = canvas.Canvas(
        os.path.join(ASSET_DIR, "Master_Supply_Agreement_NVIDIA.pdf"), pagesize=letter
    )

    c.drawString(100, 750, "MASTER SUPPLY AGREEMENT - CONFIDENTIAL")
    c.drawString(100, 730, "VENDOR: NVIDIA CORP | BUYER: YOUR_COMPANY")

    # Clause 2: Exclusivity (The Constraint)
    c.drawString(100, 680, "2. EXCLUSIVITY")
    c.drawString(
        100, 665, "Buyer agrees to purchase all GPU hardware exclusively from Vendor."
    )
    c.drawString(
        100,
        650,
        "Purchasing from third parties or spot markets is a breach of contract.",
    )

    # ... padding text ...
    c.drawString(100, 500, "[...Standard boilerplate omitted for brevity...]")

    # Clause 7.B: Force Majeure (The Loophole)
    c.drawString(100, 400, "7.B NON-PERFORMANCE & EXCEPTIONS")
    c.drawString(
        100,
        385,
        "In the event that Vendor fails to deliver agreed units for > 60 days,",
    )
    c.drawString(100, 370, "the Exclusivity clause (Section 2) is temporarily voided.")
    c.drawString(
        100,
        355,
        "Buyer may source units from alternate vendors until backlog is cleared.",
    )

    c.save()
    print("✅ Generated: Master_Supply_Agreement_NVIDIA.pdf")


def create_warehouse_manual():
    """Generates the 'Rosetta Stone' for the cryptic status codes."""
    c = canvas.Canvas(
        os.path.join(ASSET_DIR, "Warehouse_Policy_Manual_1998.pdf"), pagesize=letter
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


if __name__ == "__main__":
    create_vendor_contract()
    create_warehouse_manual()
