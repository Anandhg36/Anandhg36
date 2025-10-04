# Secure Image Storage API (FastAPI)

This FastAPI project allows uploading images, generating secure time-limited access links, and retrieving images using encrypted tokens.

## Endpoints
### 1️⃣ POST /upload-image/
- Uploads one image to the local uploads/ folder.
- Validates:
  - Only one image per request
  - Allowed extensions: .jpg, .jpeg, .png
  - File size ≤ 5 MB
  - No duplicate filenames (prevents overwriting)
  - Sanitizes filenames to avoid path traversal

### 2️⃣ GET /image-link/{filename}
- Generates an encrypted token (Fernet-based) that includes the filename and a 5-minute expiry timestamp.
- Returns the token to the user for secure access.

### 3️⃣ GET /access_image/{token}
- Decrypts the token and validates:
  - The timestamp has not expired
  - The file exists in uploads/
- If valid, serves the image.
- Returns 404 or 400 if invalid or expired.

## 🔐 Encryption Method
- Uses *Fernet encryption* from the cryptography library.
- Each token stores the filename and expiration time, encrypted with a symmetric key from .env.
- Note:
The application uses a Fernet encryption key to securely encrypt and decrypt image filenames and access tokens.
For development and testing, this key is stored in the .env file under the variable name FERNET_KEY.
This allows the FastAPI app to load the key easily during local testing. However,this should not be exposed in a production environment
## 🧰 Environment Variable
Create a .env file: