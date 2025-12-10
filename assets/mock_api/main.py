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

from fastapi import FastAPI

app = FastAPI(title="Global GPU Spot Market API", version="1.0.0")

@app.get("/")
def health_check():
    return {"status": "online", "service": "Mock Vendor API"}

@app.get("/v1/market/spot")
def get_spot_price(chip: str):
    """
    Returns current spot market pricing.
    Design Doc Requirement: Price 10x normal, Limited Availability.
    """
    chip_key = chip.upper()

    if "H100" in chip_key:
        return {
            "chip": "H100",
            "price": 32000,  # $32k/unit (High price to discourage full buy)
            "currency": "USD",
            "availability": 250,  # Only 250 available (Forces use of Internal Stock)
            "vendor": "FastChips_Reseller_LLC",
        }
    elif "A100" in chip_key:
        return {
            "chip": "A100",
            "price": 15000,
            "availability": 50,
            "vendor": "Legacy_Systems_Inc",
        }
    else:
        # Simulate market scarcity for unknown chips
        return {
            "chip": chip,
            "price": 0,
            "availability": 0,
            "note": "No stock found in global spot market.",
        }

@app.get("/v1/shipping/estimate")
def get_shipping_estimate(origin: str, dest: str):
    """
    Returns shipping timeframes.
    """
    # Simulate different shipping routes
    if origin.upper() == "TW" and dest.upper() == "US":
        return {
            "route": "TW-US",
            "days": 14,
            "method": "AIR_FREIGHT_RUSH",
            "cost_per_unit": 150,
        }
    else:
        return {
            "route": f"{origin}-{dest}",
            "days": 45,
            "method": "STANDARD_SEA",
            "cost_per_unit": 50,
        }
