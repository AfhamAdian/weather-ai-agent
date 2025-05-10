from fastapi import FastAPI, Request, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uuid
from typing import Optional
from io import BytesIO
from elevenlabs.client import ElevenLabs

import os
import json

from agent_utils import ans_to_user_query

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],  
)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Weather Agent API"}


@app.get("/api_key")
def get_api_key():
    return {"google_api_key": os.environ.get("GOOGLE_API_KEY")}


@app.post("/sendmsg")
async def send_message(request: Request):
    try:
        data = await request.json()
        response =  ans_to_user_query(data["query"])
        response_data = response
        
        return {
            "success": True,
            "response": response_data.get("response", response),
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }





client = ElevenLabs(
  api_key=os.getenv("ELEVENLABS_API_KEY"),
)

# Create audio directory if it doesn't exist
os.makedirs("audio_files", exist_ok=True)

# Mount static files directory to serve audio files
app.mount("/audio", StaticFiles(directory="audio_files"), name="audio")

@app.post("/sendvoice")
async def send_voice(file: UploadFile = File(...), session_id: Optional[str] = Form(None)):
    """
    Process a voice message and return a response with a playable audio URL
    """
    try:
        audio_bytes = await file.read()
        audio_stream = BytesIO(audio_bytes)

        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_path = f"audio_files/{file_id}.wav"
        
        # Save the uploaded audio file
        with open(file_path, "wb") as f:
            f.write(audio_bytes)  
        
        # Generate URL for this audio file
        audio_url = f"/audio/{file_id}"
        
        # Here you would use a speech-to-text service
        # For now, we'll return the audio URL so it can be played
        transcription = client.speech_to_text.convert(
            file=audio_stream,
            model_id="scribe_v1",       # Model to use
            tag_audio_events=True,      # Tag audio events like laughter, applause, etc.
            language_code="eng",        # Language of the audio file
            diarize=True                # Annotate who is speaking
        )


        return {
            "success": True,
            "response": transcription.text,
            "audio_url": audio_url,
            "session_id": session_id
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "session_id": session_id
        }

@app.get("/audio/{file_id}")
async def get_audio(file_id: str):
    """
    Retrieve an audio file by ID
    """
    file_path = f"audio_files/{file_id}.wav"
    if not os.path.exists(file_path):
        return {"error": "Audio file not found"}
    return FileResponse(file_path)