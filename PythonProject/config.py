import os
from datetime import timedelta
from dotenv import load_dotenv
from cryptography.fernet import Fernet

# Load environment variables
load_dotenv()

# Encryption Key (for local/testing use only — not for production exposure)
FERNET_KEY = os.getenv("FERNET_KEY")
fernet = Fernet(FERNET_KEY.encode())

# Directory for file uploads
UPLOAD_FOLDER = "./uploads/"

# Allowed file extensions
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}

# Maximum file size (in bytes) -> 5 MB
MAX_FILE_SIZE = 5 * 1024 * 1024

# Token expiry time
TOKEN_EXPIRY_MINUTES = 5
