# test_language_agent.py

import os
import google.generativeai as genai
from dotenv import load_dotenv

# Import the LanguageAgent (which now uses LLMEngine internally)
# Make sure your agents/language_agent.py file contains the 'LanguageAgent' class
# and that agents/llm_agent.py contains the 'LLMEngine' class.
from agents.language_agent import LanguageAgent

# Load environment variables from .env file at the very beginning
load_dotenv()

# --- Helper for checking API Key and available models (still useful for debugging) ---
def list_available_gemini_models_standalone():
    """
    A standalone function to verify if the Google API Key is set
    and which Gemini models are available for content generation.
    This helps in debugging API key and model access issues.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("ERROR: GOOGLE_API_KEY not set in environment variables for standalone model listing.")
        return

    # Print a masked version of the API key to confirm it's loaded, without exposing it fully
    print(f"DEBUG: GOOGLE_API_KEY loaded: {'*' * (len(api_key) - 5) + api_key[-5:] if api_key else 'None'}")

    try:
        genai.configure(api_key=api_key) # Configure with the loaded API key
        print("\n--- Verifying Google API Key and Listing Available Models ---")
        found_callable_models = False
        for m in genai.list_models():
            # Check if the model name contains "gemini" (case-insensitive) and supports generateContent
            if "gemini" in m.name.lower() and 'generateContent' in m.supported_generation_methods:
                print(f"  - Callable Gemini Model Name: {m.name}")
                found_callable_models = True
        if not found_callable_models:
            print("No Gemini models found that support 'generateContent' with your API key.")
        print("--- End of Model List ---")
    except Exception as e:
        print(f"\nERROR: Failed to list models. This often indicates an invalid API key or network issue.")
        print(f"Details: {e}")

# --- Test function for the Language Agent's core role (RAG) ---
def test_language_agent_market_brief_synthesis():
    """
    Tests the LanguageAgent's ability to synthesize a market brief
    using a simulated user query and relevant context documents.
    This simulates the full RAG workflow for the assignment's use case.
    """
    print("\n" + "="*80)
    print("Testing Language Agent: Market Brief Synthesis (RAG Simulation)")
    print("="*80)

    # The user's query as specified in the assignment [cite: 6]
    user_query = ("What’s our risk exposure in Asia tech stocks today, "
                  "and highlight any earnings surprises?")

    # Simulated context documents that would typically come from the Retriever Agent.
    # These documents contain the information required to form the market brief[cite: 7].
    simulated_context_documents = [
        "Portfolio allocation data: Asia tech currently represents 22% of AUM. This is an increase from yesterday's 18% allocation.",
        "Earnings report: Taiwan Semiconductor Manufacturing Company (TSMC) announced its Q1 earnings, reporting a 4% beat against analyst estimates. Strong demand for AI accelerators cited as key driver.",
        "Earnings report: Samsung Electronics released its Q1 earnings, which showed a 2% miss compared to market expectations, primarily due to softer memory chip prices and weaker consumer electronics demand.",
        "Market sentiment: General market sentiment in the Asia tech sector is currently neutral, but there's a cautionary tilt observed due to rising global bond yields, which are impacting valuations of growth stocks."
    ]

    print(f"\nSimulated User Query for Language Agent:\n'{user_query}'")
    print(f"\nSimulated Context Documents (would typically come from Retriever Agent):\n")
    for i, doc in enumerate(simulated_context_documents):
        print(f"  Doc {i+1}: {doc}")

    try:
        # Initialize the LanguageAgent. Its constructor will, in turn, initialize the LLMEngine.
        print("\nAttempting to initialize LanguageAgent...")
        language_agent = LanguageAgent()
        print("LanguageAgent initialized successfully.")

        # Call the core synthesis method of the LanguageAgent
        print("\nCalling LanguageAgent.synthesize_market_brief...")
        generated_brief = language_agent.synthesize_market_brief(user_query, simulated_context_documents)

        print("\n" + "-"*80)
        print("Generated Market Brief (Output from Language Agent):")
        print(generated_brief)
        print("-" * 80)

        # Basic assertions to check if a response was generated and doesn't contain error messages
        assert "Error" not in generated_brief, "The generated brief contains an error message."
        assert len(generated_brief) > 50, "The generated brief is too short, indicating possible issues."
        print("\nTest passed successfully (basic content and error check).")

    except Exception as e:
        print(f"\nTEST FAILED: An unexpected error occurred during the test execution: {e}")


if __name__ == "__main__":
    # First, always verify API key and model availability before running the main test
    list_available_gemini_models_standalone()

    # Proceed with the main test only if the GOOGLE_API_KEY environment variable is set
    api_key_check = os.getenv("GOOGLE_API_KEY")
    if not api_key_check:
        print("\nSkipping main test because GOOGLE_API_KEY is not set in environment variables.")
        print("Please ensure your .env file is correctly configured and loaded.")
    else:
        test_language_agent_market_brief_synthesis()