import logging
import time
from appwrite.exception import AppwriteException
from appwrite.services.databases import Databases


def log_and_create_attribute(create_func, *args, **kwargs):
    try:
        logging.info(f"Creating attribute/index: {kwargs.get('key', args[2] if len(args) > 2 else 'unknown')} ({create_func.__name__})")
        result = create_func(*args, **kwargs)
        logging.info(f"Successfully created: {kwargs.get('key', args[2] if len(args) > 2 else 'unknown')}")
        return result
    except AppwriteException as ae:
        logging.warning(f"AppwriteException during creation: {ae}")
        return None
    except Exception as e:
        logging.error(f"Exception during creation: {e}")
        return None


def list_collection_attributes(db, database_id, collection_id):
    try:
        attrs = db.list_attributes(database_id=database_id, collection_id=collection_id)
        logging.info(f"Attributes for collection {collection_id}: {[a['key'] for a in attrs['attributes']]}")
        return attrs
    except Exception as e:
        logging.error(f"Error listing attributes: {e}")
        return None

def init_sales_schema(db, database_id, sales_collection_id):
    try:
        log_and_create_attribute(db.create_string_attribute, database_id, sales_collection_id, key="sales_process_id", size=36, required=True)
        log_and_create_attribute(db.create_string_attribute, database_id, sales_collection_id, key="status", size=20, required=True)
        log_and_create_attribute(db.create_string_attribute, database_id, sales_collection_id, key="agent_id", size=36, required=True)
        log_and_create_attribute(db.create_string_attribute, database_id, sales_collection_id, key="lead_name", size=100, required=True)
        log_and_create_attribute(db.create_string_attribute, database_id, sales_collection_id, key="lead_phone", size=20, required=True)
        log_and_create_attribute(db.create_datetime_attribute, database_id, sales_collection_id, key="created_at", required=True)
        log_and_create_attribute(db.create_datetime_attribute, database_id, sales_collection_id, key="updated_at", required=False)
       
        logging.info("Successfully initialized sales attributes with unique constraints.")
    except Exception as e:
        logging.error(f"Error in init_sales_schema: {e}")

def init_recordings_schema(db, database_id, recordings_collection_id):
    try:
        log_and_create_attribute(
            db.create_string_attribute,
            database_id,
            recordings_collection_id,
            key="recording_id",
            size=36,
            required=True
        )
        log_and_create_attribute(
            db.create_string_attribute,
            database_id,
            recordings_collection_id,
            key="sales_process_id",
            size=36,
            required=True
        )
        log_and_create_attribute(
            db.create_string_attribute,
            database_id,
            recordings_collection_id,
            key="status",
            size=20,
            required=True
        )
        log_and_create_attribute(
            db.create_string_attribute,
            database_id,
            recordings_collection_id,
            key="file_name",
            
            size=200,
            required=True
        )
        log_and_create_attribute(
            db.create_datetime_attribute,
            database_id,
            recordings_collection_id,
            key="recorded_at",
            required=True
        )
        logging.info("Successfully initialized recordings attributes")
    except Exception as e:
        logging.error(f"Error in init_recordings_schema: {e}")

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

async def main():
    from dotenv import load_dotenv
    from config.settings import settings
    from app.core.appwrite_client import get_database

    load_dotenv()

    logging.basicConfig(level=logging.INFO)

    db: Databases = get_database()

    database_id = settings.APPWRITE_DATABASE_ID
    sales_collection_id = settings.APPWRITE_SALES_COLLECTION_ID
    recordings_collection_id = settings.APPWRITE_RECORDINGS_COLLECTION_ID

    if not database_id or not sales_collection_id or not recordings_collection_id:
        logging.error("Missing required database or collection IDs")
        logging.error(f"Database ID: {database_id}")
        logging.error(f"Sales Collection ID: {sales_collection_id}")
        logging.error(f"Recordings Collection ID: {recordings_collection_id}")
        sys.exit(1)

    logging.info(f"Using database_id: {database_id}")
    logging.info(f"Using sales_collection_id: {sales_collection_id}")
    logging.info(f"Using recordings_collection_id: {recordings_collection_id}")

    init_recordings_schema(db, database_id, recordings_collection_id)
    init_sales_schema(db, database_id, sales_collection_id)
    logging.info("Waiting 10 seconds for Appwrite attribute propagation...")
    time.sleep(10)
    list_collection_attributes(db, database_id, recordings_collection_id)
    list_collection_attributes(db, database_id, sales_collection_id)
    logging.info("Schema initialization complete.")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())