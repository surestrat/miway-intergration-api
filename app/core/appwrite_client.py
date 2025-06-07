from appwrite.client import Client
from appwrite.services.account import Account
from config.settings import settings

def get_appwrite_client() -> Client:
    return (
        Client()
        .set_endpoint(settings.APPWRITE_ENDPOINT)
        .set_project(settings.APPWRITE_PROJECT_ID)
        .set_key(settings.APPWRITE_API_KEY)
    )

def get_account():
    return Account(get_appwrite_client())
