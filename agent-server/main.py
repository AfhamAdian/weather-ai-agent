from fastapi import FastAPI, Request, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# import asyncio
# from typing import Optional
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




# @app.post("/sendvoice")
# async def send_voice(file: UploadFile = File(...), session_id: Optional[str] = Form(None)):
#     """
#     Process a voice message and return a response
#     """
#     try:
#         # Save the uploaded audio file
#         file_path = f"temp_audio_{session_id}.wav"
#         with open(file_path, "wb") as f:
#             content = await file.read()
#             f.write(content)
        
#         # Here you would use a speech-to-text service to convert the audio to text
#         # For now, we'll just return that this feature is coming soon
#         return {
#             "success": True,
#             "response": "Voice message processing is coming soon!",
#             "session_id": session_id
#         }
#     except Exception as e:
#         return {
#             "success": False,
#             "error": str(e),
#             "session_id": session_id
#         }

# # Helper function to process queries asynchronously
# async def process_query_async(query: str):
#     # Create a separate thread to run the CPU-bound processing
#     loop = asyncio.get_event_loop()
#     result = await loop.run_in_executor(None, ans_to_user_query, query)
#     return result
