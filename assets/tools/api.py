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
from assets.config import config
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class LogisticsTools:
    def __init__(self):
        self.base_url = config.API_BASE_URL

    def fetch_spot_prices(self, chip_type: str = "H100") -> Dict[str, Any]:
        """
        Returns the latest market price for the given GPU chip type.
        
        Args:
            chip_type: GPU model type, for example "H100"

        Returns:
            Price information or an error message
        """
        url = f"{self.base_url}/v1/market/spot"
        log.info(f"[🔧 fetch_spot_prices] Checking spot prices for chip {chip_type}: {url}")
        try:
            response = requests.get(url, params={"chip": chip_type})
            response.raise_for_status()
            log.info("[✅ fetch_spot_prices] Success")
            return response.json()
        except requests.RequestException as e:
            log.error(f"[❌ fetch_spot_prices] Market API unreachable: {str(e)}")
            return {"error": f"Market API unreachable: {str(e)}"}

    def estimate_shipping(self, origin: str, destination: str = "US") -> Dict[str, Any]:
        """
        Returns the GPU shipping cost from the given Origin to Destination
        
        Args:
            origin: defines where the GPUs will be shipped from.
            destination: defines where the GPU should be delivered to.

        Returns:
            Shipping price information or an error message
        """
        url = f"{self.base_url}/v1/shipping/estimate"
        log.info(f"[🔧 estimate_shipping] Estimating shipping: {url}")
        try:
            response = requests.get(
                url,
                params={"origin": origin, "dest": destination},
            )
            response.raise_for_status()
            log.info("[✅ estimate_shipping] Success")
            return response.json()
        except requests.RequestException as e:
            log.error(f"[❌ estimate_shipping] Shipping API unreachable: {str(e)}")
            return {"error": f"Shipping API unreachable: {str(e)}"}
