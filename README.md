## 🛠️ Environment Setup

### Option 1: Terraform (Recommended for Production simulation)
1. Install Terraform.
2. Initialize and Apply:
   ```bash
   cd infra
   terraform init
   terraform apply -var="project_id=YOUR_PROJECT_ID"
   ```

### Option 2: Local Setup (For local development and testing)
1. Set up GCP authentication:
   ```bash
   gcloud auth login
   gcloud auth application default login
   ```
2. Create and activate a Python virtual environment (Python 3.12 recommended):
   ```bash
   python3.12 -m venv venv
   source venv/bin/activate
   ```
3. Install project dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the demo:
   ```bash
   bash run_demo.sh
   ```