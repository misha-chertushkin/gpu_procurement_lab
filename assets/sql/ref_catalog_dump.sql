-- Copyright 2025 Google LLC
--
-- Licensed under the Apache License, Version 2.0 (the "License");
-- you may not use this file except in compliance with the License.
-- You may obtain a copy of the License at
--
--     http://www.apache.org/licenses/LICENSE-2.0
--
-- Unless required by applicable law or agreed to in writing, software
-- distributed under the License is distributed on an "AS IS" BASIS,
-- WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
-- See the License for the specific language governing permissions and
-- limitations under the License.

CREATE OR REPLACE TABLE `gpu_procurement_db.REF_CATALOG_DUMP`
(
    CATALOG_ID STRING,
    HUMAN_READABLE_NAME STRING,
    VENDOR_SKU STRING
);

-- SEED DATA TODO: remove GPU type from ID values (H100, A100, RTX4090) - the model might cheat
INSERT INTO `gpu_procurement_db.REF_CATALOG_DUMP` VALUES ('REF_H100_XIE', 'H100 Tensor Core GPU', 'NV-H100-80GB');
INSERT INTO `gpu_procurement_db.REF_CATALOG_DUMP` VALUES ('REF_A100_NV', 'A100 Tensor Core GPU', 'NV-A100-40GB');
INSERT INTO `gpu_procurement_db.REF_CATALOG_DUMP` VALUES ('REF_RTX4090', 'GeForce RTX 4090', 'NV-RTX-4090');