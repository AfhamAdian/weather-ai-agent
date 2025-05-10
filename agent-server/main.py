# FILE: agent-server/main.py

import os
import io
from fastapi import FastAPI, HTTPException, Request, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
import uuid
from typing import Optional
from elevenlabs.client import ElevenLabs
from agent_utils import ans_to_user_query
from io import BytesIO




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

os.makedirs("audio_files", exist_ok=True)
app.mount("/audio", StaticFiles(directory="audio_files"), name="audio")

@app.post("/sendvoice")
async def send_voice(file: UploadFile = File(...), session_id: Optional[str] = Form(None)):
    """
    Process a voice message and return a response with a playable audio URL
    """
    try:
        # Read audio file once
        audio_bytes = await file.read()
        audio_stream = BytesIO(audio_bytes)
        
        # Save the file
        file_id = str(uuid.uuid4())
        file_path = f"audio_files/{file_id}.wav"
        with open(file_path, "wb") as f:
            f.write(audio_bytes)
        
        audio_url = f"/audio/{file_id}"
        
        # Use the BytesIO stream for transcription
        # Make sure position is at the beginning
        audio_stream.seek(0)
        
        # Get transcription
        print("here firster")   
        transcription = client.speech_to_text.convert(
            file=audio_stream,
            model_id="scribe_v1",
            tag_audio_events=True,
            language_code="eng",
            diarize=True
        )
        print("here second")

        print(f"Transcription: {transcription.text}")

        # Return response
        return {
            "success": True,
            "response": transcription.text,
            "audio_url": audio_url,
            "session_id": session_id
        }
    except Exception as e:
        print(f"Error processing voice message: {e}")
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




@app.post("/text_to_speech")
async def text_to_speech(request: Request):
    # 1. Parse incoming JSON
    data = await request.json()
    text = (data.get("text") or "").strip()
    if not text:
        raise HTTPException(400, detail="`text` is required")

    # 2. Generate TTS via ElevenLabs (mirroring tts_demo.py)
    try:
        # You must pick a valid voice_id from your account
        voice_id = "JBFqnCBsd6RMkjVDRZzb"

        # This returns a generator of raw MP3 byte-chunks
        audio_generator = client.text_to_speech.convert(
            voice_id=voice_id,
            text=text,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )

        # 3. Concatenate chunks into one `bytes` object
        if hasattr(audio_generator, "__iter__") and not isinstance(audio_generator, (bytes, bytearray)):
            audio_bytes = b"".join(audio_generator)
        else:
            audio_bytes = audio_generator  # already bytes

        # (Optional) Save for debugging or caching
        with open("audio_files/latest.mp3", "wb") as f:
            f.write(audio_bytes)

        # 4. Stream it back as an MP3 blob
        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/mpeg",
            headers={"Content-Disposition": 'inline; filename="tts.mp3"'}
        )

    except Exception as e:
        # Log and return a 500
        print("TTS generation failed:", repr(e))
        raise HTTPException(500, detail="TTS generation failed")
