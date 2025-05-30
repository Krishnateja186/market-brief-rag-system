# streamlit_app/app.py

import streamlit as st
import requests
import io
import base64 # For handling audio if returned as base64 string

# --- Configuration ---
# Configure the Orchestrator's URL using Streamlit Secrets.
# This URL MUST be the public URL of your Orchestrator microservice once it's deployed (e.g., on Render).
# You need to add ORCHESTRATOR_URL = "https://your-orchestrator-url.onrender.com"
# in your Streamlit Cloud app's Secrets.
ORCHESTRATOR_URL = st.secrets.get("ORCHESTRATOR_URL")

# Add a check to ensure the URL is configured in secrets
if not ORCHESTRATOR_URL:
    st.error("Error: Orchestrator URL not found in Streamlit Secrets. "
             "Please add 'ORCHESTRATOR_URL' to your app's secrets in Streamlit Community Cloud settings. "
             "Example: ORCHESTRATOR_URL = \"https://your-orchestrator-service.onrender.com\"")
    st.stop() # Stop the app from running if the critical URL is missing

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="Morning Market Brief Assistant",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Header Section ---
st.title("📈 Morning Market Brief Assistant")
st.markdown("""
    Your AI-powered assistant for quick daily market insights on Asia Tech stocks.
    Simply type your query or (soon) speak it, and get a synthesized market brief!
""")

st.divider()

# --- User Input Section ---
st.header("Request Your Market Brief")

# Text Input for the query
text_query = st.text_input(
    "Enter your query:",
    value="What’s our risk exposure in Asia tech stocks today, and highlight any earnings surprises?",
    placeholder="e.g., 'Give me an update on Asia tech performance today.'",
    help="Type the question you want the assistant to answer about the market."
)

# Voice Input Placeholder (to be fully implemented with STT Agent)
st.subheader("🗣️ Voice Input (Under Development)")
st.info("Voice input will be enabled once the **Voice Agent (STT)** is fully integrated and deployed.")
# You can add a placeholder button if you like, but it won't be functional yet
# if st.button("🎙️ Record Voice Query"):
#     st.warning("Voice recording and STT integration is not yet active. Please use text input.")


# --- Generate Brief Button ---
if st.button("Generate Market Brief", type="primary", use_container_width=True):
    if not text_query:
        st.warning("Please enter a text query to generate the market brief.")
    else:
        st.info("Generating your market brief. This might take a moment as the AI agents coordinate...")
        
        # Use a spinner to indicate ongoing processing
        with st.spinner("Talking to agents: API, Retriever, Analysis, Language..."):
            try:
                # Prepare the payload for the Orchestrator
                payload = {"text_query": text_query}

                # Make an HTTP POST request to the Orchestrator
                response = requests.post(f"{ORCHESTRATOR_URL}/generate_market_brief", json=payload)
                response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)

                brief_data = response.json() # Parse the JSON response from the Orchestrator

                st.subheader("📊 Your Market Brief:")

                # Display the synthesized text brief
                brief_text = brief_data.get("market_brief_text", "No brief text was generated. Please check Orchestrator logs.")
                st.markdown(brief_text)

                # --- Audio Playback Section (Future Integration with TTS Agent) ---
                # The Orchestrator should return audio bytes or a base64 encoded string
                # For now, the Orchestrator returns only text. When TTS is integrated,
                # uncomment and adapt this section.
                # if "market_brief_audio" in brief_data:
                #     audio_base64 = brief_data["market_brief_audio"]
                #     if audio_base64:
                #         audio_bytes = base64.b64decode(audio_base64)
                #         st.audio(audio_bytes, format='audio/mpeg') # Or 'audio/wav' depending on TTS output
                #         st.success("Brief generated and ready to play!")
                #     else:
                #         st.info("Audio brief is empty.")
                # else:
                #     st.info("Audio brief generation is not yet fully enabled by the Orchestrator.")

                st.success("Market brief generated successfully!")

            except requests.exceptions.ConnectionError:
                st.error(f"Failed to connect to the Orchestrator at {ORCHESTRATOR_URL}. "
                         "Please ensure the Orchestrator microservice is running and its URL is correct in Streamlit Secrets.")
            except requests.exceptions.HTTPError as e:
                # Catch specific HTTP errors from the Orchestrator
                error_detail = e.response.json().get("detail", "Unknown error from Orchestrator.")
                st.error(f"Error from Orchestrator: {e.response.status_code} - {error_detail}")
                st.exception(e) # Display full traceback for debugging
            except Exception as e:
                st.error(f"An unexpected error occurred during brief generation: {e}")
                st.exception(e) # Display full traceback for debugging

st.markdown("---")
st.caption("""
    **To run this application (locally with backend agents):**
    1.  Ensure all backend microservices (API Agent, Retriever Agent, Analysis Agent, Scraping Agent, STT Agent, TTS Agent) are running on their specified ports.
    2.  Start the Orchestrator microservice (`orchestrator/main.py`) on `http://localhost:8000`.
    3.  Set a local environment variable (e.g., in a .streamlit/secrets.toml file if using Streamlit's local secrets management) or directly in code for local testing: `ORCHESTRATOR_URL = "http://localhost:8000"`
    4.  In your terminal, navigate to your project's root directory and run: `streamlit run streamlit_app/app.py`

    **For Cloud Deployment (Streamlit Community Cloud):**
    1.  Deploy your Orchestrator microservice and other backend agents to a cloud platform (e.g., Render). Get their public/internal URLs.
    2.  In Streamlit Community Cloud settings for this app, go to "Secrets".
    3.  Add `ORCHESTRATOR_URL = "https://your-orchestrator-url.onrender.com"` (replace with your actual URL).
""")
st.markdown("---")
st.markdown("Developed as part of the Multi-Agent Finance Assistant Assignment.")