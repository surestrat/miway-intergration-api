# DTech API Integration Guide

This guide explains how to use the DTech External Sales API integration.

## Obtaining Required Credentials

### 1. DTech API Credentials

1. Contact DTech Support to register for API access
   - Email their support team to request API access
   - They will provide:
     - A temporary token
     - Your account ID (`DIFFERENT_ACCOUNT_ID`)
     - Security group information

2. Activate your API client using the temporary credentials:
```bash
curl -X POST \
https://test-dsp.integrations.different.co.za/activate/{security_group} \
-H 'accept: application/json' \
-H 'content-type: application/json' \
-d '{
  "account_id": "{your_account_id}",
  "request_token": "{your_temporary_token}"
}'
```

3. After successful activation, you'll receive:
   - AWS Access Key (`AWS_ACCESS_KEY_ID`)
   - AWS Secret Key (`AWS_SECRET_ACCESS_KEY`)
   - Keep these secure and never commit them to version control

### 2. Appwrite Setup

1. Sign up at [Appwrite Cloud](https://cloud.appwrite.io)

2. Create a new project:
   - Go to "Projects" → "Create Project"
   - Note down the `Project ID` (`APPWRITE_PROJECT_ID`)
   
3. Get your API Key:
   - Go to "Project Settings" → "API Keys"
   - Create a new API key with required permissions
   - Note down:
     - Endpoint URL (`APPWRITE_ENDPOINT`)
     - API Key (`APPWRITE_API_KEY`)

4. Create Database and Collections:
   - Go to "Databases" → "Create Database"
   - Name it "MiWay Sales Database"
   - Note down the Database ID
   - Create two collections:
     1. "Sales Processes"
     2. "Call Recordings"
   - Note down both Collection IDs

5. Update your `.env` file with the IDs:
```env
APPWRITE_DATABASE_ID="your_database_id"
APPWRITE_SALES_COLLECTION_ID="your_sales_collection_id"
APPWRITE_RECORDINGS_COLLECTION_ID="your_recordings_collection_id"
```

6. Run the database setup script to create attributes and indexes:
```bash
python scripts/setup_appwrite.py
```

This will create the following structure:

Sales Process Collection:
- Attributes:
  - sales_process_id (string, 36 chars, required)
  - status (string, 20 chars, required)
  - agent_id (string, 36 chars, required)
  - lead_name (string, 100 chars, required)
  - lead_phone (string, 20 chars, required)
  - created_at (datetime, required)
  - updated_at (datetime, required)
- Indexes:
  - sales_process_id_idx (unique)
  - agent_id_idx (key)

Call Recordings Collection:
- Attributes:
  - recording_id (string, 36 chars, required)
  - sales_process_id (string, 36 chars, required)
  - status (string, 20 chars, required)
  - file_name (string, 200 chars, required)
  - recorded_at (datetime, required)
- Indexes:
  - recording_id_idx (unique)
  - sales_process_id_idx (key)

### 3. Environment Configuration

Create a `.env` file in your project root with the following structure:
```env
# Appwrite Configuration
APPWRITE_ENDPOINT="https://cloud.appwrite.io/v1"
APPWRITE_PROJECT_ID="your_project_id"
APPWRITE_API_KEY="your_api_key"

# Appwrite Database Settings
APPWRITE_DATABASE_ID="your_database_id"
APPWRITE_SALES_COLLECTION_ID="your_sales_collection_id"
APPWRITE_RECORDINGS_COLLECTION_ID="your_recordings_collection_id"

# DTech API Configuration
DIFFERENT_API_TEST="https://test-dsp.integrations.different.co.za"
DIFFERENT_API_PROD="https://dsp.integrations.different.co.za"
DIFFERENT_ACCOUNT_ID="your_dtech_account_id"

# AWS Credentials (from DTech activation)
AWS_ACCESS_KEY_ID="your_aws_access_key"
AWS_SECRET_ACCESS_KEY="your_aws_secret_key"
AWS_REGION="eu-west-1"
AWS_SERVICE="execute-api"

# Redis Configuration
REDIS_HOST="localhost"
REDIS_PORT=6379
REDIS_DB=0

# Security Configuration
SECRET_KEY="your-secret-key-here"
SESSION_COOKIE_NAME="session_id"
SESSION_EXPIRE_MINUTES=1440
```

⚠️ Security Notes:
- Never commit `.env` file to version control
- Rotate credentials regularly
- Use different credentials for test and production
- Store production credentials in a secure vault
- Monitor AWS CloudTrail for API usage

## Setup

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables as described above in `.env`:
```env
# DTech API Configuration
DIFFERENT_API_TEST=https://test-dsp.integrations.different.co.za
DIFFERENT_ACCOUNT_ID=your_account_id
AWS_ACCESS_KEY=your_aws_access_key
AWS_SECRET_KEY=your_aws_secret_key
AWS_REGION=eu-west-1
```

## API Endpoints

### 1. Start Sales Process

Initiates a new sales process.

```python
from app.schemas.sales import StartSalesRequest, User, Lead

request = StartSalesRequest(
    account_id="your_account_id",
    user=User(
        external_id="agent123",
        first_name="John",
        last_name="Doe",
        provider_id="provider_123"
    ),
    lead=Lead(
        first_name="Jane",
        last_name="Smith",
        phone_mobile="(083) 555-5555",
        campaign_code="CAMPAIGN_01",
        lead_origin="Website"
    )
)

response = await client.post("/api/v1/sales/start", json=request.dict())
```

### 2. Continue Sales Process

Get a new URL to continue an existing sales process.

```python
response = await client.post(
    f"/api/v1/sales/continue/{spid}",
    json={
        "account_id": "your_account_id",
        "user": {
            "external_id": "agent123",
            "first_name": "John",
            "last_name": "Doe",
            "provider_id": "provider_123"
        }
    }
)
```

### 3. Check Process Status

Monitor the status of a sales process.

```python
response = await client.get(f"/api/v1/sales/status/{spid}/{account_id}")
```

### 4. Stop Process

Stop an ongoing sales process.

```python
response = await client.post(
    f"/api/v1/sales/stop/{spid}",
    json={
        "account_id": "your_account_id",
        "reason": "Customer not interested"
    }
)
```

### 5. Upload Call Recording

Upload a call recording in two steps:

1. Get upload URL:
```python
from app.utils.file_utils import calculate_file_md5
from datetime import datetime

recording_hash = calculate_file_md5("recording.wav")

request = RecordingUploadRequest(
    account_id="your_account_id",
    date_start=datetime.now(),
    date_end=datetime.now(),
    recording_hash=recording_hash,
    filename="recording.wav",
    content_type="audio/wav"
)

response = await client.post(f"/api/v1/sales/recording-url/{spid}", json=request.dict())
```

2. Upload the file:
```python
from app.services.dtech_service import upload_recording_file

success = await upload_recording_file(
    upload_url=response.upload_url,
    file_path="recording.wav",
    content_type="audio/wav",
    recording_hash=recording_hash
)
```

## Error Handling

The API uses standard HTTP status codes:
- 200: Success
- 400: Bad Request (validation error)
- 401: Unauthorized (AWS authentication failed)
- 403: Forbidden (invalid AWS signature)
- 404: Not Found
- 500: Internal Server Error

Example error response:
```json
{
    "detail": "Error message here",
    "code": "ERROR_CODE"
}
```

## Validation

- All dates must be in ISO 8601 format (YYYY-MM-DDTHH:mm:ss)
- Phone numbers must be in format (083) 555-5555
- Recording content types must be audio/wav or audio/mpeg
- Account ID must be a valid UUID
- File names must not exceed 200 characters

## AWS Authentication

All requests are authenticated using AWS Signature Version 4. The SDK handles this automatically, but you must provide valid AWS credentials in your environment variables.

## Data Models

### Sales Process
The sales process data model includes:
```json
{
    "sales_process_id": "UUID string",
    "status": "in_progress|complete|stopped",
    "agent_id": "UUID string",
    "lead_name": "Full name string",
    "lead_phone": "(083) 555-5555",
    "created_at": "2025-06-08T10:00:00Z",
    "updated_at": "2025-06-08T10:30:00Z"
}
```

### Call Recording
The call recording data model includes:
```json
{
    "recording_id": "UUID string",
    "sales_process_id": "UUID string",
    "status": "pending|uploading|complete|failed",
    "file_name": "recording.wav",
    "recorded_at": "2025-06-08T10:15:00Z"
}
```
