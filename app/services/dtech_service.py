import httpx
import json
from app.schemas.sales import User, Lead, SalesProcessResponse
from config.settings import settings
from app.utils.aws_auth import AWSRequestSigner
from typing import Dict, Any
from datetime import datetime

# Initialize AWS request signer
signer = AWSRequestSigner(
    access_key=settings.AWS_ACCESS_KEY_ID,
    secret_key=settings.AWS_SECRET_ACCESS_KEY,
    region=settings.AWS_REGION
)

async def create_process(user: User, lead: Lead) -> Dict[str, Any]:
    """
    Create a new sales process.
    Example Response:
    {
        "sales_process_id": "41e9410d-0d16-cf75-a022-63cf9290ee5e",
        "url": "https://test.go.miwaylife.co.za/dl/ext/start/41e9410d-0d16-cf75-a022-63cf9290ee5e/0027da88-f485-4c02-82ef-c5e3d77673f7",
        "url_expiry": "2023-01-24T11:12:26.783817"
    }
    """
    url = f"{settings.DIFFERENT_API_TEST}/ext/start"
    payload = {
        "account_id": settings.DIFFERENT_ACCOUNT_ID,
        "user": user.model_dump(),
        "lead": lead.model_dump(exclude_none=True)
    }
    
    # Convert payload to JSON string for signing
    data = json.dumps(payload)
    
    # Get signed headers
    headers = signer.sign_request(
        method="POST",
        url=url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    )
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return SalesProcessResponse(**response.json()).model_dump()

async def continue_process(spid: str, user: User) -> Dict[str, Any]:
    """Continue an existing sales process"""
    url = f"{settings.DIFFERENT_API_TEST}/ext/continue/{spid}"
    payload = {
        "account_id": settings.DIFFERENT_ACCOUNT_ID,
        "user": user.model_dump()
    }
    
    data = json.dumps(payload)
    headers = signer.sign_request(
        method="POST",
        url=url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    )
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()

async def get_status(spid: str, account_id: str) -> Dict[str, Any]:
    """Get the status of a sales process"""
    url = f"{settings.DIFFERENT_API_TEST}/ext/status/{spid}/{account_id}"
    
    headers = signer.sign_request(
        method="GET",
        url=url,
        headers={"Accept": "application/json"}
    )
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

async def stop_process(spid: str, account_id: str, reason: str) -> Dict[str, Any]:
    """Stop an ongoing sales process"""
    url = f"{settings.DIFFERENT_API_TEST}/ext/stop/{spid}"
    payload = {
        "account_id": account_id,
        "reason": reason
    }
    
    data = json.dumps(payload)
    headers = signer.sign_request(
        method="POST",
        url=url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    )
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()

async def get_recording_url(
    spid: str,
    account_id: str,
    date_start: str,
    date_end: str,
    recording_hash: str,
    filename: str,
    content_type: str,
    external_ref: str = None
) -> Dict[str, Any]:
    """Get URL for uploading recording"""
    url = f"{settings.DIFFERENT_API_TEST}/recording-url/{spid}"
    payload = {
        "account_id": account_id,
        "date_start": date_start,
        "date_end": date_end,
        "recording_hash": recording_hash,
        "filename": filename,
        "content_type": content_type
    }
    if external_ref:
        payload["external_ref"] = external_ref
    
    data = json.dumps(payload)
    headers = signer.sign_request(
        method="POST",
        url=url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Content-MD5": recording_hash
        }
    )
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()

async def upload_recording_file(
    upload_url: str,
    file_path: str,
    content_type: str,
    recording_hash: str
) -> bool:
    """
    Upload a recording file to the provided presigned URL.
    
    Args:
        upload_url: The presigned URL from get_recording_url
        file_path: Path to the audio file
        content_type: MIME type of the file (audio/wav or audio/mpeg)
        recording_hash: Base64 encoded MD5 hash of the file
        
    Returns:
        bool: True if upload successful
    """
    try:
        headers = {
            "Content-Type": content_type,
            "Content-MD5": recording_hash
        }
        
        with open(file_path, 'rb') as f:
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    upload_url,
                    content=f.read(),
                    headers=headers
                )
                response.raise_for_status()
                return True
    except Exception as e:
        raise Exception(f"Failed to upload recording: {str(e)}")

async def activate_api_client(security_group: str, account_id: str, request_token: str) -> Dict[str, Any]:
    """
    Activate the API client to get AWS credentials.
    This should only be called once during initial setup.
    """
    url = f"{settings.DIFFERENT_API_TEST}/activate/{security_group}"
    payload = {
        "account_id": account_id,
        "request_token": request_token
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            json=payload,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
        )
        response.raise_for_status()
        return response.json()
