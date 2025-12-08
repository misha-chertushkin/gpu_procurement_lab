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

CREATE OR REPLACE TABLE `gpu_procurement_db.LEGACY_INV_MAIN_V2`
(
    ITEM_REF_ID STRING OPTIONS(description="Internal Product Reference ID (Non-Standard)"),
    LOC_BIN_HEX STRING OPTIONS(description="Warehouse Bin Location (Hex encoded). A1=Shipping, 55=Quarantine, B2=Lost"),
    QOH_RAW_VAL INT64 OPTIONS(description="Quantity on Hand (Raw Value)"),
    LAST_TOUCH_DT_UNIX INT64 OPTIONS(description="Last movement timestamp in Unix Epoch"),
    STATUS_FLAG_9 INT64 OPTIONS(description="Inventory Status: 0=OK, 1=Reserved, 9=Legal Hold")
);

-- SEED DATA TODO: remove GPU type from ID values (H100, A100, RTX4090) - the model might cheat

-- 1. Distractor H100 records (Standard Shipping Bin A1)
-- Shows 0 stock in attempt to confuse the agent.
INSERT INTO `gpu_procurement_db.LEGACY_INV_MAIN_V2` VALUES ('REF_H100_XIE', 'A1', 0, 1700000000, 0);

-- 2. The "Golden" Record (The Hidden Stock)
-- 300 units in Bin 55 (Quarantine) with Status 9 (Legal Hold).
-- The Inventory Agent must find this record in order to solve the task.
INSERT INTO `gpu_procurement_db.LEGACY_INV_MAIN_V2` VALUES ('REF_H100_XIE', '55', 300, 1710000000, 9);

-- 3. Distractors: additional products to make the DB look more realistic.
INSERT INTO `gpu_procurement_db.LEGACY_INV_MAIN_V2` VALUES ('REF_A100_NV', 'A1', 50, 1705000000, 0);
INSERT INTO `gpu_procurement_db.LEGACY_INV_MAIN_V2` VALUES ('REF_RTX4090', 'B2', 1200, 1706000000, 0);