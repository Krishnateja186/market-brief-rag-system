# voice_io/stt_service.py

from fastapi import FastAPI, UploadFile, File, HTTPException, status
from pydantic import BaseModel
import io
import os
import base64 # New import for base64 encoding
import requests # New import for making HTTP requests
from dotenv import load_dotenv

# Load environment variables (for GOOGLE_API_KEY)
load_dotenv()

app = FastAPI(
    title="STT Agent Microservice (Google Speech-to-Text)",
    description="Handles Speech-to-Text conversion using Google Cloud Speech-to-Text API."
)

class STTResponse(BaseModel):
    """Response model for the transcribed text."""
    text: str

@app.get("/")
def root():
    """Root endpoint for the STT Agent."""
    return {"message": "STT Agent Microservice is running. Visit /docs for API documentation."}

@app.post("/speech_to_text", response_model=STTResponse)
async def speech_to_text_endpoint(audio_file: UploadFile = File(...)):
    """
    Converts speech from an uploaded audio file to text using Google Cloud Speech-to-Text API.

    Args:
        audio_file (UploadFile): The audio file to be transcribed.
                                 Supports common audio formats like mp3, wav, flac, ogg.

    Returns:
        STTResponse: A Pydantic model containing the transcribed text.

    Raises:
        HTTPException:
            - 400 if the uploaded file is not an audio file or is empty.
            - 500 if an error occurs during transcription with the Google Speech-to-Text API.
    """
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GOOGLE_API_KEY not found. Please set it in your .env file."
        )

    if not audio_file.content_type or not audio_file.content_type.startswith("audio/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Please upload an audio file (e.g., .mp3, .wav, .flac, .ogg)."
        )

    if audio_file.size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty audio file uploaded."
        )

    print(f"STT Agent: Received audio file '{audio_file.filename}' (Type: {audio_file.content_type}, Size: {audio_file.size} bytes) for transcription.")

    try:
        # Read audio content and encode it to base64
        audio_bytes = await audio_file.read()
        audio_content_base64 = base64.b64encode(audio_bytes).decode('utf-8')

        # Google Cloud Speech-to-Text API endpoint
        google_speech_api_url = f"https://speech.googleapis.com/v1/speech:recognize?key={google_api_key}"

        # Prepare the request payload
        # For general audio, let Google infer encoding and sample rate.
        # You can specify them if known for better accuracy (e.g., "encoding": "LINEAR16", "sampleRateHertz": 16000)
        # If using an OPUS file, you might try "encoding": "OGG_OPUS"
        request_body = {
            "audio": {
                "content": audio_content_base64
            },
            "config": {
                "languageCode": "en-US", # You can change this to your desired language
                # "encoding": "ENCODING_UNSPECIFIED", # Let Google auto-detect for common formats
                # "sampleRateHertz": 0 # Let Google auto-detect
            }
        }

        print(f"STT Agent: Sending request to Google Cloud Speech-to-Text API...")
        response = requests.post(google_speech_api_url, json=request_body)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)

        result = response.json()

        if result and "results" in result and result["results"]:
            transcribed_text = result["results"][0]["alternatives"][0]["transcript"]
            print(f"STT Agent: Transcription successful. Text: '{transcribed_text[:100]}...'")
            return STTResponse(text=transcribed_text)
        else:
            print(f"STT Agent: No transcription results found. Full response: {result}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No transcription results found from Google Speech-to-Text API. Check audio quality or API response."
            )

    except requests.exceptions.HTTPError as e:
        print(f"STT Agent: Google Speech-to-Text API HTTP error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code if e.response.status_code < 500 else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google Speech-to-Text API error: {e.response.text}"
        )
    except requests.exceptions.ConnectionError as e:
        print(f"STT Agent: Network connection error to Google API: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Could not connect to Google Speech-to-Text API: {e}"
        )
    except Exception as e:
        print(f"STT Agent: An unexpected error occurred during transcription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during transcription: {e}"
        )

# To run this STT Agent microservice:
# 1. Install necessary packages: pip install fastapi uvicorn python-dotenv requests
# 2. Ensure your GOOGLE_API_KEY is set in your .env file and has access to Google Cloud Speech-to-Text API.
# 3. From your project's root directory, run: uvicorn voice_io.stt_service:app --reload --port 8004