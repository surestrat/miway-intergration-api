import logging
from appwrite.client import Client
from appwrite.services.account import Account
from appwrite.services.databases import Databases
from appwrite.services.storage import Storage
from appwrite.services.teams import Teams
from appwrite.services.users import Users
from appwrite.services.functions import Functions
from appwrite.services.locale import Locale
from appwrite.services.health import Health
from appwrite.services.avatars import Avatars
from appwrite.exception import AppwriteException
from config.settings import settings
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

def validate_url(url: str, name: str) -> None:
    """Validate that a URL is properly formatted"""
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            raise ValueError(f"Invalid {name} URL: {url}")
    except Exception as e:
        raise ValueError(f"Error parsing {name} URL: {str(e)}")

def get_appwrite_client() -> Client:
    """Get a configured and validated Appwrite client"""
    try:
        endpoint = settings.APPWRITE_ENDPOINT.strip('"# ')  # Remove quotes and comments
        project_id = settings.APPWRITE_PROJECT_ID.strip('"# ')
        api_key = settings.APPWRITE_API_KEY.strip('"# ')
        
        # Log configuration (without sensitive data)
        logger.debug(f"Initializing Appwrite client with endpoint: {endpoint}")
        logger.debug(f"Using project ID: {project_id}")
        
        # Create and configure the client
        client = Client()
        client.set_endpoint(endpoint)
        client.set_project(project_id)
        client.set_key(api_key)
        
        return client
        
    except AppwriteException as e:
        logger.error(f"Appwrite client error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error initializing Appwrite client: {str(e)}")
        raise

def get_account() -> Account:
    return Account(get_appwrite_client())

def get_database() -> Databases:
    """Get a configured Appwrite Databases client with error handling"""
    try:
        client = get_appwrite_client()
        databases = Databases(client)
        
        # Test the database connection
        databases.list()  # This will throw if connection fails
        return databases
    except AppwriteException as e:
        logger.error(f"Failed to connect to Appwrite database: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error connecting to database: {str(e)}")
        raise

def get_storage():
    return Storage(get_appwrite_client())

def get_teams():
    return Teams(get_appwrite_client())

def get_users():
    return Users(get_appwrite_client())

def get_functions():
    return Functions(get_appwrite_client())

def get_locale():
    return Locale(get_appwrite_client())

def get_health():
    return Health(get_appwrite_client())

def get_avatars():
    return Avatars(get_appwrite_client())

def get_buckets():
    return Storage(get_appwrite_client())