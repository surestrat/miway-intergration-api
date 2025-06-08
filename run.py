import sys
import uvicorn
import logging
import traceback
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    try:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger = logging.getLogger("Miway")
        logger.info("Starting surestrat api")
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=4005,
            reload=True,
            log_level="debug",
            log_config=None,
        )
    except Exception as e:
        print(f"An error occurred while starting the server: {e}")
        traceback.print_exc()
        sys.exit(1)
