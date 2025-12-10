# Fix Google Drive Authentication Scope Issue

## Problem

You're seeing this error:
```
Request had insufficient authentication scopes
```

This happens because Application Default Credentials (ADC) don't include Google Drive scopes by default.

## Solution

You have **two options** to fix this:

### Option 1: Re-authenticate with Drive Scope (Quickest)

Run this command to re-authenticate with the correct scopes:

```bash
gcloud auth application-default login --scopes=https://www.googleapis.com/auth/drive.file,https://www.googleapis.com/auth/userinfo.email,https://www.googleapis.com/auth/cloud-platform
```

This will:
1. Open your browser
2. Ask you to grant Google Drive permissions
3. Save the credentials with the Drive scope

### Option 2: Use a Service Account (Production Recommended)

1. **Create a Service Account:**
   ```bash
   # Set your project ID
   export PROJECT_ID="your-project-id"
   
   # Create service account
   gcloud iam service-accounts create gpu-procurement-agent \
       --display-name="GPU Procurement Agent" \
       --project=$PROJECT_ID
   
   # Create and download key
   gcloud iam service-accounts keys create ~/gpu-procurement-key.json \
       --iam-account=gpu-procurement-agent@${PROJECT_ID}.iam.gserviceaccount.com
   ```

2. **Set the environment variable:**
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS=~/gpu-procurement-key.json
   ```

3. **Share your Google Drive folder with the service account:**
   - Get the service account email: `gpu-procurement-agent@YOUR_PROJECT_ID.iam.gserviceaccount.com`
   - Open Google Drive in your browser
   - Right-click on the folder where you want reports uploaded
   - Click "Share"
   - Add the service account email
   - Give it "Editor" permissions

## Quick Test

After fixing authentication, test it:

```bash
python -c "
from utils.gdrive_integration import ReportGenerator
reporter = ReportGenerator()
result = gdrive.upload_file('test.md', '# Test\nThis is a test.')
print(result)
"
```

You should see:
```
SUCCESS: Report uploaded to Google Drive
  - File ID: ...
  - Web Link: ...
```

## Why This Happened

The `gcloud auth application-default login` command only grants these default scopes:
- `https://www.googleapis.com/auth/cloud-platform`
- `https://www.googleapis.com/auth/userinfo.email`

It does NOT include:
- `https://www.googleapis.com/auth/drive.file` (needed to upload files to Drive)

## Recommendation

For **local development**: Use Option 1 (quickest)
For **production/deployment**: Use Option 2 (service accounts are more secure)

## Troubleshooting

If you still see permission errors after Option 1:

1. Check which credentials are active:
   ```bash
   gcloud auth application-default print-access-token
   ```

2. Try revoking and re-authenticating:
   ```bash
   gcloud auth application-default revoke
   gcloud auth application-default login --scopes=https://www.googleapis.com/auth/drive.file,https://www.googleapis.com/auth/userinfo.email,https://www.googleapis.com/auth/cloud-platform
   ```

3. Verify the Drive API is enabled:
   ```bash
   gcloud services enable drive.googleapis.com --project=YOUR_PROJECT_ID
   ```
