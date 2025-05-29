# agents/llm_agent.py

import google.generativeai as genai
import os
from dotenv import load_dotenv
from typing import List, Optional

load_dotenv()

class LLMEngine: # <--- THIS CLASS NAME MUST BE 'LLMEngine'
    """
    Core LLM Engine for direct interaction with Google Generative AI models.
    Handles API configuration and model selection logic.
    """
    def __init__(self, api_key: str = None):
        print("LLMEngine: Initializing LLM Engine...")
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("LLMEngine: GOOGLE_API_KEY not found. Please set it in your .env file or pass it directly.")

        genai.configure(api_key=self.api_key)
        self.model = None
        self.actual_model_name_used = None

        model_priorities = [
            'gemini-1.5-flash', # Recommended by Google in deprecation message
            'gemini-pro',       # Common alias for text models
            'gemini-1.0-pro'    # Explicit model name for text
        ]

        try:
            print("LLMEngine: Attempting to find a suitable Gemini model from preferred list...")
            available_models_info = {}

            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    available_models_info[m.name.split('/')[-1]] = m.name # Store short name -> full name

            for preferred_name in model_priorities:
                if preferred_name in available_models_info:
                    try:
                        self.model = genai.GenerativeModel(preferred_name)
                        self.actual_model_name_used = preferred_name
                        print(f"LLMEngine: Successfully configured model '{preferred_name}'.")
                        break
                    except Exception as config_e:
                        print(f"LLMEngine: Failed to configure '{preferred_name}' (possibly transient issue): {config_e}")
                else:
                    print(f"LLMEngine: Model '{preferred_name}' not found in available models list.")

            if not self.model: # If after trying all priorities, no model was configured
                print("\nLLMEngine: ERROR: No suitable Gemini text model could be configured from the preferred list.")
                print("LLMEngine: Available models that support 'generateContent':")
                if available_models_info:
                    for short_name, full_name in available_models_info.items():
                        print(f"  - {full_name}")
                else:
                    print("  (No models found at all supporting 'generateContent'.)")
                print("LLMEngine: Please verify your API key, its permissions, and regional availability.")
                raise ValueError("No suitable Gemini model found or configured by LLMEngine.")

        except Exception as e:
            print(f"\nLLMEngine: CRITICAL ERROR: LLM Engine initialization failed. Check your GOOGLE_API_KEY and network connection.")
            print(f"LLMEngine: Details: {e}")
            raise # Re-raise to stop execution if LLM setup fails

    def generate_response(self, prompt: str) -> str:
        """
        Generates a direct response from the configured LLM for a given prompt.
        This is the core LLM interaction method.
        """
        if not self.model:
            print("LLMEngine: Model not initialized. Cannot generate response.")
            return "Error: LLM Engine not configured."
        # print(f"LLMEngine: Sending prompt to model '{self.actual_model_name_used}'...") # Uncomment for debug
        try:
            response = self.model.generate_content(prompt)
            # print("LLMEngine: Response received from LLM.") # Uncomment for debug
            return response.text
        except Exception as e:
            print(f"LLMEngine: Error during content generation: {e}")
            return f"Error from LLM: {e}"