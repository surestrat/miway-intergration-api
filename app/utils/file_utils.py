import base64
import hashlib
from pathlib import Path

def calculate_file_md5(file_path: str | Path) -> str:
    """
    Calculate MD5 hash of a file and return it base64 encoded.
    This is specifically for the DTech API recording upload requirements.
    
    Args:
        file_path: Path to the file
        
    Returns:
        str: Base64 encoded MD5 hash of the file
    """
    file_path = Path(file_path)
    md5_hash = hashlib.md5()
    
    with open(file_path, 'rb') as f:
        # Read the file in chunks to handle large files
        for chunk in iter(lambda: f.read(4096), b''):
            md5_hash.update(chunk)
            
    # Get the binary hash and encode it to base64
    return base64.b64encode(md5_hash.digest()).decode('utf-8')
