from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional
from datetime import datetime

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    
class BaseRequest(BaseModel):
    account_id: str = Field(..., description="The DTech account ID")

class User(BaseModel):
    external_id: str = Field(..., example="AgentSystemID1")
    first_name: str = Field(..., example="AgentName1")
    last_name: str = Field(..., example="AgentSurname1")
    provider_id: str = Field(..., example="c69f2d28-906a-3468-013b-6396e468a103")

class Lead(BaseModel):
    external_reference: Optional[str] = None
    first_name: str = Field(..., example="John99")
    last_name: str = Field(..., example="Doe99")
    phone_mobile: str = Field(..., example="(083) 555-5599", pattern=r'^\(\d{3}\) \d{3}-\d{4}$')
    phone_work: Optional[str] = None
    email: Optional[EmailStr] = None
    id_number: Optional[str] = None
    campaign_code: str = Field(..., example="MWLItalkTestDefault")
    lead_origin: str = Field(..., example="Our test website")

class StartSalesRequest(BaseRequest):
    user: User
    lead: Lead

class SalesProcessResponse(BaseModel):
    sales_process_id: str
    url: str
    url_expiry: datetime

class RecordingUploadRequest(BaseModel):
    account_id: str = Field(..., min_length=36, max_length=36)
    date_start: datetime
    date_end: datetime
    recording_hash: str = Field(..., min_length=1)
    filename: str = Field(..., max_length=200)
    content_type: str = Field(..., pattern='^audio/(wav|mpeg)$')
    external_ref: Optional[str] = Field(None, max_length=36)

    @validator('date_end')
    def end_date_must_be_after_start(cls, v, values):
        if 'date_start' in values and v <= values['date_start']:
            raise ValueError('end_date must be after start_date')
        return v

    @validator('content_type')
    def validate_content_type(cls, v):
        allowed_types = ['audio/wav', 'audio/mpeg']
        if v not in allowed_types:
            raise ValueError(f'content_type must be one of {allowed_types}')
        return v

class RecordingUploadResponse(BaseModel):
    recording_id: str = Field(..., min_length=36, max_length=36)
    upload_url: str
    success: bool = True
    upload_id: Optional[str] = None
