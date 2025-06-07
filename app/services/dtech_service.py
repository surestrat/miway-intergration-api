import httpx
from app.schemas.sales import User, Lead
from config.settings import settings

async def create_process(user: User, lead: Lead) -> dict:
    url = f"{settings.DIFFERENT_API_TEST}/ext/start"
    payload = {
        "account_id": settings.DIFFERENT_ACCOUNT_ID,
        "user": user.dict(),
        "lead": lead.dict()
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        return response.json()

async def continue_process(spid: str, user: User) -> dict:
    url = f"{settings.DIFFERENT_API_TEST}/ext/continue/{spid}"
    payload = {
        "account_id": settings.DIFFERENT_ACCOUNT_ID,
        "user": user.dict()
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        return response.json()

async def get_status(spid: str, account_id: str) -> dict:
    url = f"{settings.DIFFERENT_API_TEST}/ext/status/{spid}/{account_id}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()

async def stop_process(spid: str, account_id: str, reason: str) -> dict:
    url = f"{settings.DIFFERENT_API_TEST}/ext/stop/{spid}"
    payload = {
        "account_id": account_id,
        "reason": reason
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
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
) -> dict:
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
        
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        return response.json()
