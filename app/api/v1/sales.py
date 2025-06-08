from fastapi import APIRouter, Request, Form, BackgroundTasks, HTTPException, Depends, Cookie
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer
from email_validator import validate_email, EmailNotValidError
from datetime import datetime, timedelta
from typing import Optional
import uuid
import json

from app.core.appwrite_client import get_account
from app.schemas.sales import (
    StartSalesRequest, BaseRequest, User, RecordingUploadResponse,
    RecordingUploadRequest
)
from app.services.dtech_service import (
    create_process, continue_process, get_status,
    stop_process as dtech_stop_process, get_recording_url
)
from app.utils.background import run_background_tasks
from app.utils.session import session_manager
from app.utils.aws_exceptions import handle_dtech_error

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(session_id: str = Cookie(None)) -> Optional[dict]:
    """Get current user from session"""
    if not session_id:
        return None
    return await session_manager.get_session(session_id)

@router.get("/login-form", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login_form.html", {"request": request})

@router.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    background_tasks: BackgroundTasks | None = None
):
    try:
        # Validate email
        validate_email(email)
        
        # Authenticate with Appwrite
        session = get_account().create_email_password_session(email=email, password=password)
        
        if not session or not isinstance(session, dict) or "$id" not in session:
            return HTMLResponse(
                content=f"<div class='error-message'><i class='fas fa-exclamation-circle'></i> Invalid session data returned from Appwrite</div>",
                status_code=401
            )
        
        # Create session
        session_id = str(uuid.uuid4())
        session_data = {
            "user_id": session.get("$id"),
            "email": email,
            "created_at": datetime.now().isoformat()
        }
        
        await session_manager.set_session(session_id, session_data)
        
        # Add background task
        if background_tasks:
            run_background_tasks(background_tasks, {"event": "login", "email": email})
        
        response = HTMLResponse(
            content=f"<div class='success-message'><i class='fas fa-check-circle'></i> Login successful!</div>"
        )
        response.set_cookie(
            key="session_id",
            value=session_id,
            max_age=86400,  # 24 hours
            httponly=True,
            secure=True,
            samesite="strict"
        )
        return response
        
    except EmailNotValidError as e:
        return HTMLResponse(
            content=f"<div class='error-message'><i class='fas fa-exclamation-circle'></i> Invalid email format</div>",
            status_code=400
        )
    except Exception as e:
        return HTMLResponse(
            content=f"<div class='error-message'><i class='fas fa-exclamation-circle'></i> Login failed: {str(e)}</div>",
            status_code=401
        )

@router.post("/logout")
async def logout(session_id: str = Cookie(None)):
    """Logout user and clear session"""
    if session_id:
        await session_manager.delete_session(session_id)
    response = HTMLResponse("<div class='success-message'>Logged out successfully</div>")
    response.delete_cookie("session_id")
    return response

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

@router.post("/recording-url/{spid}", response_model=RecordingUploadResponse)
async def get_recording_upload_url(
    spid: str,
    request: RecordingUploadRequest,
    current_user: dict = Depends(get_current_user)
):
    """Get URL for uploading recording with progress tracking"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
        
    try:
        # Generate upload ID for tracking
        upload_id = str(uuid.uuid4())
        
        # Store upload metadata in session
        upload_metadata = {
            "upload_id": upload_id,
            "filename": request.filename,
            "started_at": datetime.now().isoformat(),
            "status": "pending"
        }
        
        await session_manager.set_session(
            f"upload:{upload_id}",
            upload_metadata,
            expiry=timedelta(hours=1)
        )
        
        result = await get_recording_url(
            spid=spid,
            account_id=request.account_id,
            date_start=request.date_start.isoformat(),
            date_end=request.date_end.isoformat(),
            recording_hash=request.recording_hash,
            filename=request.filename,
            content_type=request.content_type,
            external_ref=request.external_ref
        )
        
        # Update upload status
        upload_metadata["status"] = "url_generated"
        await session_manager.set_session(
            f"upload:{upload_id}",
            upload_metadata,
            expiry=timedelta(hours=1)
        )
        
        return RecordingUploadResponse(
            **result,
            upload_id=upload_id
        )
        
    except Exception as e:
        error = handle_dtech_error(e)
        return JSONResponse(
            status_code=error.status_code,
            content={"detail": error.detail}
        )

@router.get("/upload-status/{upload_id}")
async def get_upload_status(
    upload_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get the status of an ongoing upload"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
        
    try:
        upload_data = await session_manager.get_session(f"upload:{upload_id}")
        if not upload_data:
            raise HTTPException(status_code=404, detail="Upload not found")
            
        return JSONResponse(content=upload_data)
    except Exception as e:
        error = handle_dtech_error(e)
        return JSONResponse(
            status_code=error.status_code,
            content={"detail": error.detail}
        )
