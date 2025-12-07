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

import requests
from typing import Dict, Any
from utils.config import config


class LogisticsTools:
    def __init__(self):
        self.base_url = config.API_BASE_URL

    def fetch_spot_prices(self, chip_type: str = "H100") -> Dict[str, Any]:
        """
        Checks the spot market price for a specific chip.
        Endpoint: GET /v1/market/spot?chip=H100 [cite: 97]
        """
        try:
            response = requests.get(
                f"{self.base_url}/v1/market/spot", params={"chip": chip_type}
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": f"Market API unreachable: {str(e)}"}

    def estimate_shipping(self, origin: str, destination: str = "US") -> Dict[str, Any]:
        """
        Gets shipping estimates.
        Endpoint: GET /v1/shipping/estimate?origin=TW&dest=US [cite: 99]
        """
        try:
            response = requests.get(
                f"{self.base_url}/v1/shipping/estimate",
                params={"origin": origin, "dest": destination},
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": f"Shipping API unreachable: {str(e)}"}
