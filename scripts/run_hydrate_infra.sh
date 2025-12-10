#!/bin/bash
# Copyright 2025 Google LLC
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     https://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Configuration
API_PORT=8080
API_HOST="127.0.0.1"
ROOT_DIR="./"
VENV_DIR="$ROOT_DIR/venv"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Load load environment
. scripts/base_env.sh

echo -e "${BLUE}🚀 Starting Vertex AI L400 Lab 2 Demo Hydration of cloud resources...${NC}"

# Create and source the virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "🐍 Python virtual environment in $VENV_DIR not found, please intiialize the repository..."
    exit 1
fi
source $VENV_DIR/bin/activate


# --- Step 1: World Building (Data) ---
echo -e "\n${BLUE}[1/2] Building the 'Opaque' Database...${NC}"
python assets/setup_db.py
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Database setup failed. Check credentials/permissions.${NC}"
    exit 1
fi

echo -e "\n${BLUE}[2/2] creating 'Conflicting' Legal Documents...${NC}"
python assets/setup_gcs.py
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ GCS setup failed. Check bucket permissions.${NC}"
    exit 1
fi

exit 0
