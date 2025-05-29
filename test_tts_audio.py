import requests
import json
import os

TTS_AGENT_URL = "http://127.0.0.1:8006/text_to_speech"
OUTPUT_FILENAME = "test_speech.mp3"

payload = {
    "text": "Hello, this is a test from a Python script. I hope you can hear me!",
    "lang": "en",
    "slow": False
}

print(f"Sending request to TTS Agent at {TTS_AGENT_URL}...")

try:
    response = requests.post(TTS_AGENT_URL, json=payload, stream=True)
    response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)

    # Check if the content type is audio/mpeg
    if "audio/mpeg" in response.headers.get("Content-Type", ""):
        with open(OUTPUT_FILENAME, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Successfully saved audio to {OUTPUT_FILENAME}")
        print("Please try playing this file with a media player (like VLC or Windows Media Player).")
    else:
        print(f"Received unexpected content type: {response.headers.get('Content-Type')}")
        print(f"Response content: {response.text}")

except requests.exceptions.RequestException as e:
    print(f"Error connecting to TTS Agent or during request: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")