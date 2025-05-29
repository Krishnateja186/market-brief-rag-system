# voice_io/tts_service.py

from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel
from gtts import gTTS # Google Text-to-Speech library
import io

app = FastAPI(
    title="TTS Agent Microservice",
    description="Handles Text-to-Speech conversion using gTTS."
)

class TTSRequest(BaseModel):
    """Request model for text-to-speech conversion."""
    text: str
    lang: str = "en" # Default language for gTTS (e.g., 'en', 'hi', 'fr')
    slow: bool = False # Whether to speak slowly

@app.get("/")
def root():
    """Root endpoint for the TTS Agent."""
    return {"message": "TTS Agent Microservice is running. Visit /docs for API documentation."}

@app.post("/text_to_speech", response_class=Response, responses={
    200: {"content": {"audio/mpeg": {}}, "description": "Audio of the spoken text"},
    400: {"description": "Invalid input"},
    500: {"description": "Internal server error"}
})
async def text_to_speech_endpoint(request: TTSRequest):
    """
    Converts text to speech using gTTS and returns the audio as bytes.

    Args:
        request (TTSRequest): The request body containing text, language, and speed.

    Returns:
        Response: An HTTP response containing the audio bytes with 'audio/mpeg' content type.

    Raises:
        HTTPException:
            - 400 if the input text is empty.
            - 500 if an error occurs during text-to-speech conversion.
    """
    if not request.text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text for speech conversion cannot be empty."
        )

    print(f"TTS Agent: Converting text to speech (Language: '{request.lang}', Slow: {request.slow})...")
    try:
        # Create a gTTS object
        tts = gTTS(text=request.text, lang=request.lang, slow=request.slow)

        # Save audio to an in-memory bytes buffer
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0) # Rewind the buffer to the beginning

        print("TTS Agent: Text-to-speech conversion successful. Returning audio bytes.")
        # Return the audio bytes with the correct content type (audio/mpeg for MP3)
        return Response(content=audio_buffer.read(), media_type="audio/mpeg")
    except Exception as e:
        print(f"TTS Agent: Error during text-to-speech conversion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during text-to-speech conversion: {e}"
        )

# To run this TTS Agent microservice:
# 1. Install necessary packages: pip install fastapi uvicorn gtts
# 2. From your project's root directory, run: uvicorn voice_io.tts_service:app --reload --port 8006
# (Note: Using port 8006 here, adjust if another agent uses it)