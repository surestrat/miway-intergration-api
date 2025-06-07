from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.api.v1 import sales

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")
app.include_router(sales.router, prefix="/api/v1/sales", tags=["Sales"])

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
