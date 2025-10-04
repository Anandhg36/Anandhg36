import os
from datetime import datetime, timedelta
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import FileResponse
from pathvalidate import sanitize_filename
from config import (UPLOAD_FOLDER, ALLOWED_EXTENSIONS, MAX_FILE_SIZE, TOKEN_EXPIRY_MINUTES, fernet)

app = FastAPI()

@app.get("/image-link/{filename}")
def get_image_link(filename: str, request: Request):
    sanitized_filename = sanitizeFilename(filename)
    filepath = os.path.join(UPLOAD_FOLDER, sanitized_filename)
    if not os.path.isfile(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    encrypted_filename = encryptFilenameWithTimestamp(sanitized_filename)
    full_link = f"{request.url.scheme}://{request.url.hostname}:{request.url.port}/access_image/{encrypted_filename}"
    return {"link": full_link}


@app.get("/access_image/{token}")
def get_image(token: str):
    try:
        decrypted_file = fernet.decrypt(token.encode()).decode()
        filename, expiration_timestamp = decrypted_file.split("|")
        if datetime.now().timestamp() > float(expiration_timestamp):
            raise HTTPException(status_code=404, detail="Token expired")
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.isfile(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        return FileResponse(file_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid token: {str(e)}")


@app.post("/upload-image/")
async def upload_image(file: List[UploadFile] = File(...)):
    # To validate that only one image is sent
    if len(file) != 1:
        raise HTTPException(status_code=400, detail="Only one image can be uploaded at a time.")
    upload_file = file[0]
    original_extension = os.path.splitext(upload_file.filename)[1].lower()
    # Checking whether file is in image extension type
    if original_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file Type")
    file_content = await upload_file.read()
    # Validating the size of the image
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")
    sanitized_filename = sanitizeFilename(upload_file.filename)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    file_path = os.path.join(UPLOAD_FOLDER, sanitized_filename)
    # This prevents overwriting existing files and ensures unique uploads
    if os.path.isfile(file_path):
        raise HTTPException(status_code=400,
                            detail="Image with same name already exists. Please upload image with different name.")
    with open(file_path, "wb") as f:
        f.write(file_content)
    return {"message": f"File '{upload_file.filename}' uploaded successfully"}


# To encrypt the filename with timestamp
def encryptFilenameWithTimestamp(filename: str) -> str:
    timestamp = (datetime.now() + timedelta(minutes=TOKEN_EXPIRY_MINUTES)).timestamp()
    new_filename = f"{filename}|{timestamp}"
    encrypted_filename = fernet.encrypt(new_filename.encode())
    return encrypted_filename.decode()


# To sanitize filename to ensure it contains only safe characters
def sanitizeFilename(filename: str) -> str:
    new_filename = sanitize_filename(filename)
    return new_filename
