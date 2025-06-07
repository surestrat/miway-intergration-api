from fastapi import APIRouter, Request, Form, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from email_validator import validate_email, EmailNotValidError
from datetime import datetime
from typing import Optional

from app.core.appwrite_client import get_account
from app.schemas.sales import StartSalesRequest, BaseRequest, User
from app.services.dtech_service import (
    create_process, continue_process, get_status,
    stop_process as dtech_stop_process, get_recording_url
)
from app.utils.background import run_background_tasks

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/login-form", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login_form.html", {"request": request})

@router.post("/login", response_class=HTMLResponse)
def login(email: str = Form(...), password: str = Form(...), background_tasks: BackgroundTasks = None):
    try:
        validate_email(email)
        session = get_account().create_email_session(email=email, password=password)
        run_background_tasks(background_tasks, {"event": "login", "email": email})
        return f"<div><strong>Logged in! Token:</strong> {session['$id']}</div>"
    except EmailNotValidError as e:
        return f"<div style='color:red'>Invalid email: {e}</div>"
    except Exception as e:
        return f"<div style='color:red'>Login failed: {e}</div>"

@router.post("/start", response_class=HTMLResponse)
async def start_sales(request: StartSalesRequest, background_tasks: BackgroundTasks):
    try:
        result = await create_process(request.user, request.lead)
        run_background_tasks(background_tasks, {"event": "start_process", "result": result})
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/continue/{spid}")
async def continue_sales(spid: str, request: BaseRequest, user: User, background_tasks: BackgroundTasks):
    try:
        result = await continue_process(spid, user)
        run_background_tasks(background_tasks, {"event": "continue_process", "result": result})
        # Format response according to spec
        return {
            "url": result["url"],
            "url_expiry": result["url_expiry"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{spid}/{accountid}")
async def get_process_status(spid: str, accountid: str):
    try:
        result = await get_status(spid, accountid)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop/{spid}")
async def stop_process(spid: str, request: BaseRequest, reason: str):
    try:
        result = await dtech_stop_process(spid, request.account_id, reason)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/recording-url/{spid}")
async def get_recording_upload_url(
    spid: str,
    account_id: str,
    date_start: datetime,
    date_end: datetime,
    recording_hash: str,
    filename: str,
    content_type: str,
    external_ref: Optional[str] = None
):
    try:
        result = await get_recording_url(
            spid=spid,
            account_id=account_id,
            date_start=date_start.isoformat(),
            date_end=date_end.isoformat(),
            recording_hash=recording_hash,
            filename=filename,
            content_type=content_type,
            external_ref=external_ref
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
