from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    
class BaseRequest(BaseModel):
    account_id: str

class User(BaseModel):
    external_id: str
    first_name: str
    last_name: str
    provider_id: str

class Lead(BaseModel):
    external_reference: str | None = None
    first_name: str
    last_name: str
    phone_mobile: str
    phone_work: str | None = None
    email: EmailStr | None = None
    id_number: str | None = None
    campaign_code: str
    lead_origin: str

class StartSalesRequest(BaseRequest):
    user: User
    lead: Lead
