# Google Drive Integration Setup

This document explains how to set up and use the Google Drive integration for uploading procurement reports.

## Overview

The `ReportGenerator` class in `src/utils/gdrive_integration.py` now supports **real Google Drive uploads** instead of just simulating them. It uses Google Application Default Credentials (ADC) for authentication.

## Features

- ✅ Upload reports to Google Drive
- ✅ Automatic local backup of all reports
- ✅ List recent reports from Drive
- ✅ Delete reports from Drive
- ✅ Graceful fallback to local storage if Drive upload fails
- ✅ Support for organizing reports in specific folders

## Setup Instructions

### 1. Install Required Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `google-api-python-client` - Google Drive API client
- `google-auth-httplib2` - HTTP library for Google Auth
- `google-auth-oauthlib` - OAuth 2.0 support

### 2. Authentication Setup

You need to set up Google Cloud credentials. Choose one of the following methods:

#### Option A: Using Application Default Credentials (Recommended for GCP)

If you're running on Google Cloud Platform (Compute Engine, Cloud Run, etc.), ADC is automatically configured.

For local development:

```bash
gcloud auth application-default login --scopes=https://www.googleapis.com/auth/drive.file,https://www.googleapis.com/auth/userinfo.email,https://www.googleapis.com/auth/cloud-platform
```

**Important:** You MUST include the `--scopes` parameter to grant Google Drive access. Without it, you'll get "insufficient permissions" errors.

#### Option B: Using Service Account (Recommended for Production)

1. Create a service account in Google Cloud Console
2. Download the service account key JSON file
3. Set the environment variable:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

### 3. Enable Google Drive API

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Select your project
3. Navigate to "APIs & Services" > "Library"
4. Search for "Google Drive API"
5. Click "Enable"

### 4. Grant Drive Access (Service Account Only)

If using a service account, you need to grant it access to Google Drive:

1. Get the service account email (e.g., `my-service@project.iam.gserviceaccount.com`)
2. Share the target Google Drive folder with this email address
3. Give it "Editor" or "Writer" permissions

## Usage

### Basic Upload

```python
from utils.gdrive_integration import ReportGenerator

# Initialize (uploads to root of "My Drive")
reporter = ReportGenerator()

# Upload a report
result = gdrive.upload_file(
    filename="my_report.md",
    content="# Report Content\n\nThis is my report.",
    metadata={"version": "1.0", "author": "agent"}
)

print(result)
```

### Upload to Specific Folder

```python
# Initialize with a specific folder ID
reporter = ReportGenerator(folder_id="YOUR_FOLDER_ID_HERE")

# Upload to that folder
result = gdrive.upload_file(
    filename="report.md",
    content="Content here"
)
```

**How to get a folder ID:**
1. Open the folder in Google Drive web interface
2. The URL will look like: `https://drive.google.com/drive/folders/1a2b3c4d5e6f7g8h9i0j`
3. The folder ID is the last part: `1a2b3c4d5e6f7g8h9i0j`

### List Recent Reports

```python
# List the 10 most recent reports
reports = reporter.list_reports(max_results=10)

for report in reports:
    print(f"Name: {report['name']}")
    print(f"Created: {report['createdTime']}")
    print(f"Link: {report['webViewLink']}")
    print()
```

### Delete a Report

```python
success = reporter.delete_report(file_id="FILE_ID_HERE")
if success:
    print("Report deleted successfully")
```

## Configuration via Environment Variables

You can configure the Google Drive folder ID via environment variables:

```bash
export GDRIVE_FOLDER_ID="your_folder_id_here"
```

Then in your code:

```python
import os
from utils.gdrive_integration import ReportGenerator

folder_id = os.getenv("GDRIVE_FOLDER_ID")
reporter = ReportGenerator(folder_id=folder_id)
```

## Error Handling

The implementation includes robust error handling:

1. **Local Backup**: Always saves a local copy to `./gdrive_sync/` before attempting upload
2. **Graceful Degradation**: If Google Drive upload fails, the local backup is preserved
3. **Detailed Error Messages**: Returns clear error messages indicating what went wrong

Example error handling:

```python
result = gdrive.upload_file("report.md", "Content")

if "SUCCESS" in result:
    print("✓ Uploaded to Google Drive")
else:
    print("✗ Upload failed, but local backup available")
    
print(result)  # Detailed status message
```

## Troubleshooting

### Authentication Errors

**Error**: `Failed to authenticate with Google Drive: Could not automatically determine credentials`

**Solution**: Set up credentials using one of the methods in section 2 above.

### Permission Errors

**Error**: `403 Forbidden` or `Insufficient permissions`

**Solution**: 
- Ensure the Google Drive API is enabled
- If using a service account, make sure the folder is shared with the service account email
- Verify the credentials have the `https://www.googleapis.com/auth/drive.file` scope

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'googleapiclient'`

**Solution**: Install the required packages:
```bash
pip install -r requirements.txt
```

## Security Best Practices

1. **Never commit credentials**: Add service account keys to `.gitignore`
2. **Use minimal scopes**: The code uses `drive.file` scope (only files created by the app)
3. **Rotate keys regularly**: If using service accounts, rotate keys every 90 days
4. **Use Secret Manager**: Store sensitive credentials in Google Secret Manager

## Example: Integration with Commander Agent

The commander agent automatically uses this integration:

```python
from utils.gdrive_integration import ReportGenerator

# Already initialized in commander/agent.py
reporter = ReportGenerator()

# Agent will call this
result = gdrive.upload_file(
    filename="H100_Procurement_Report.md",
    content=final_report,
    metadata={"version": "1.0", "agent": "root_agent"}
)
```

## Testing

To test the integration:

```bash
python -c "
from utils.gdrive_integration import ReportGenerator
reporter = ReportGenerator()
result = gdrive.upload_file('test.md', '# Test\nThis is a test.')
print(result)
"
```

You should see output like:
```
SUCCESS: Report uploaded to Google Drive
  - File ID: 1a2b3c4d5e6f...
  - File Name: test.md
  - Web Link: https://drive.google.com/file/d/...
  - Local Backup: ./gdrive_sync/test.md
```
