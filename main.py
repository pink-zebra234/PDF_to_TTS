# Import Libraries
import PyPDF2
import requests
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import uvicorn

# Configurations
ELEVENLABS_API_KEY = "sk_7a5968b2053fe6bcceeafd6b0c01bbaf4f0d64cea84e1d66"  # Replace with your ElevenLabs API key
VOICE_ID = "Ir1QNHvhaJXbAGhT50w3"  # Replace with your voice ID from ElevenLabs

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

# Run FastAPI Server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
