# -*- coding: utf-8 -*-
"""PDF to TTS_v1.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Yta81o5cT4UltqWN0NjMiEzORp8iAbgW
"""

!pip install PyPDF2

pip install fastapi uvicorn PyPDF2 requests python-multipart

# Install required libraries
!pip install fastapi uvicorn PyPDF2 requests python-multipart nest_asyncio

# Import Libraries
import PyPDF2
import requests
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import uvicorn
import nest_asyncio
import threading

# Configurations
ELEVENLABS_API_KEY = "sk_7a5968b2053fe6bcceeafd6b0c01bbaf4f0d64cea84e1d66"
VOICE_ID = "Ir1QNHvhaJXbAGhT50w3"

# Initialize FastAPI App
app = FastAPI()

# Function to extract text from PDF
def extract_text_from_pdf(file):
    try:
        reader = PyPDF2.PdfReader(file)
        text = " ".join([page.extract_text() for page in reader.pages])
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error extracting text: {str(e)}")

# Function to generate audio using ElevenLabs API
def generate_audio(text, output_file="output.mp3"):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    payload = {
        "text": text,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        with open(output_file, "wb") as audio_file:
            audio_file.write(response.content)
        return output_file
    else:
        raise HTTPException(status_code=500, detail="Error generating audio")

# API Endpoint for PDF Upload
@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    text = extract_text_from_pdf(file.file)
    if not text:
        raise HTTPException(status_code=400, detail="Failed to extract text from the PDF")

    output_file = generate_audio(text)
    return FileResponse(output_file, media_type="audio/mpeg", filename="output.mp3")

# Run FastAPI Server in a Thread
def run_api():
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Enable Nest AsyncIO to run Uvicorn in Colab
nest_asyncio.apply()
api_thread = threading.Thread(target=run_api)
api_thread.start()

print("Backend is ready. You can now upload your file.")

from google.colab import files
import requests

# Upload the PDF file
print("Upload your PDF file:")
uploaded_file = files.upload()

# Extract the uploaded file name
file_name = list(uploaded_file.keys())[0]
print(f"Uploaded file: {file_name}")

# Send file to backend API
url = "http://localhost:8000/upload/"
with open(file_name, 'rb') as file_data:
    response = requests.post(url, files={'file': file_data})

# Handle response
if response.status_code == 200:
    output_file = "output.mp3"
    with open(output_file, "wb") as audio_file:
        audio_file.write(response.content)
    print(f"Audio file generated and saved as {output_file}")
    files.download(output_file)
else:
    print("Error:", response.json())