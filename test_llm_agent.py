# This file remains UNCHANGED from the previous successful version.
# Its purpose is to run the test and provide debugging output.

from agents.llm_agent import LLMAgent
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def list_available_gemini_models_standalone():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("ERROR: GOOGLE_API_KEY not set in environment variables for standalone model listing.")
        return

    print(f"DEBUG: GOOGLE_API_KEY loaded: {'*' * (len(api_key) - 5) + api_key[-5:] if api_key else 'None'}")

    try:
        genai.configure(api_key=api_key)
        print("\n--- Verifying Google API Key and Listing Available Models ---")
        found_callable_models = False
        for m in genai.list_models():
            if "gemini" in m.name.lower() and 'generateContent' in m.supported_generation_methods:
                print(f"  - Callable Gemini Model Name: {m.name}")
                found_callable_models = True
        if not found_callable_models:
            print("No Gemini models found that support 'generateContent' with your API key.")
        print("--- End of Model List ---")
    except Exception as e:
        print(f"\nERROR: Failed to list models. This often indicates an invalid API key or network issue.")
        print(f"Details: {e}")

def test_language_agent_market_brief_synthesis():
    print("\n" + "="*80)
    print("Testing Language Agent: Market Brief Synthesis (RAG Simulation)")
    print("="*80)

    user_query = ("What’s our risk exposure in Asia tech stocks today, "
                  "and highlight any earnings surprises?")

    simulated_context_documents = [
        "Portfolio allocation data: Asia tech currently represents 22% of AUM. This is an increase from yesterday's 18% allocation.",
        "Earnings report: Taiwan Semiconductor Manufacturing Company (TSMC) announced its Q1 earnings, reporting a 4% beat against analyst estimates. Strong demand for AI accelerators cited as key driver.",
        "Earnings report: Samsung Electronics released its Q1 earnings, which showed a 2% miss compared to market expectations, primarily due to softer memory chip prices and weaker consumer electronics demand.",
        "Market sentiment: General market sentiment in the Asia tech sector is currently neutral, but there's a cautionary tilt observed due to rising global bond yields, which are impacting valuations of growth stocks."
    ]

    print(f"\nSimulated User Query:\n'{user_query}'")
    print(f"\nSimulated Context Documents (from Retriever Agent):\n")
    for i, doc in enumerate(simulated_context_documents):
        print(f"  Doc {i+1}: {doc}")

    try:
        # Initialize the LLMAgent (Language Agent)
        # It will now attempt to use 'gemini-1.5-flash' first.
        llm_agent = LLMAgent() # No need to pass model_name here, as it has internal priority logic

        generated_brief = llm_agent.synthesize_market_brief(user_query, simulated_context_documents)

        print("\n" + "-"*80)
        print("Generated Market Brief (from Language Agent):")
        print(generated_brief)
        print("-" * 80)

        assert "Error" not in generated_brief, "The generated brief contains an error message."
        assert len(generated_brief) > 50, "The generated brief is too short."
        print("\nTest passed successfully (basic content check).")

    except Exception as e:
        print(f"\nTEST FAILED: An error occurred during the test execution: {e}")


if __name__ == "__main__":
    list_available_gemini_models_standalone()

    api_key_check = os.getenv("GOOGLE_API_KEY")
    if not api_key_check:
        print("\nSkipping main test because GOOGLE_API_KEY is not set.")
    else:
        test_language_agent_market_brief_synthesis()