#!/bin/bash
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


# Configuration
API_PORT=8080
API_HOST="127.0.0.1"
# Check if phase number is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <phase>"
    exit 1
fi

PHASE=$1
PHASE_DIR="labs/$PHASE"
VENV_DIR="$PHASE_DIR/venv"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Load load environment
. scripts/base_env.sh

source $VENV_DIR/bin/activate

echo -e "${BLUE}🚀 Running Vertex AI L400 Lab 2 Test for $PHASE...${NC}"

# --- Step 1: The External World (Mock API) ---
echo -e "\n${BLUE}[1/2] Launching Mock Spot Market API...${NC}"

# Kill any existing process on port 8080 to avoid conflicts
fuser -k $API_PORT/tcp > /dev/null 2>&1

mkdir -p ./workspace/$PHASE_DIR/logs/
mkdir -p ./workspace/$PHASE_DIR/tests/

# Start API in background
cd assets/mock_api
uvicorn main:app --host $API_HOST --port $API_PORT > ../../workspace/$PHASE_DIR/logs/latest-test-mock-api.log 2>&1 &
API_PID=$!
cd ../..

echo "✅ API running in background (PID: $API_PID). Logs at ./workspace/$PHASE_DIR/logs/latest-test-mock-api.log"
echo "   Waiting 5 seconds for API to warm up..."
sleep 5

# --- Step 2: Unit Test (Agents) ---
echo -e "\n${BLUE}[2/2] 🛡️ Launching Unit Test...${NC}"
echo "---------------------------------------------------------------"

# Run the main agent loop
python -m pytest -v -s --log-cli-level=INFO -W "ignore::DeprecationWarning" $PHASE_DIR/tests --junitxml=./workspace/$PHASE_DIR/tests/latest-test-results.xml 2>&1 | tee ./workspace/$PHASE_DIR/tests/latest-test-results.log

# --- Cleanup ---
echo -e "\n${BLUE}🧹 Cleaning up...${NC}"
fuser -k $API_PORT/tcp > /dev/null 2>&1
echo "✅ Mock API stopped."
echo -e "${GREEN}🏁 Demo Complete.${NC}"
