# agents/language_agent.py

from typing import List
# Assuming LLMEngine is the class defined in agents/llm_agent.py
from agents.llm_agent import LLMEngine # <--- THIS LINE IS CORRECT, ENSURE LLMEngine CLASS EXISTS IN llm_agent.py


class LanguageAgent:
    """
    The Language Agent specialized in synthesizing market brief narratives
    using Retrieval-Augmented Generation (RAG) for the Morning Market Brief use case.
    It utilizes the LLMEngine for underlying LLM interactions.
    """
    def __init__(self):
        print("LanguageAgent: Initializing LanguageAgent for market brief synthesis...")
        self.llm_engine = LLMEngine() # <--- INSTANTIATING LLMEngine
        print(f"LanguageAgent: LLMEngine initialized with model '{self.llm_engine.actual_model_name_used}'.")
        print("LanguageAgent: Ready to synthesize financial narratives based on context.")

    def synthesize_market_brief(self, query: str, context_documents: List[str]) -> str:
        # ... (rest of this method is unchanged and uses self.llm_engine.generate_response)
        print(f"\nLanguageAgent: Initiating market brief synthesis for query: '{query}'")
        print(f"LanguageAgent: Received {len(context_documents)} context documents for RAG processing.")

        context_str = "\n".join([f"Context Document {i+1}:\n{doc}" for i, doc in enumerate(context_documents)])

        full_prompt = (
            f"You are a sophisticated finance assistant providing a concise morning market brief. "
            f"Synthesize the response verbally and directly, as if spoken, adhering to the "
            f"portfolio manager's query. Your task is to provide a comprehensive summary "
            f"based on the provided context.\n\n"
            f"User Query: '{query}'\n\n"
            f"Ensure the brief specifically covers the following points from the context:\n"
            f"- Current risk exposure/allocation in Asia tech stocks, including percentage of AUM and changes from yesterday.\n"
            f"- Any key earnings surprises (both beats and misses) from relevant companies, with specific percentages.\n"
            f"- Overall regional sentiment or cautionary tilts, providing reasons for the sentiment.\n\n"
            f"Contextual Information to use:\n{context_str}\n\n"
            f"Strictly adhere to the following output format example, starting directly with the brief:\n"
            f"'Today, your Asia tech allocation is 22 % of AUM, up from 18 % yesterday. "
            f"TSMC beat estimates by 4 %, Samsung missed by 2 %. Regional sentiment is "
            f"neutral with a cautionary tilt due to rising yields.'\n\n"
            f"Market Brief:"
        )

        print(f"LanguageAgent: Passing RAG prompt to LLMEngine for generation using model '{self.llm_engine.actual_model_name_used}'...")
        try:
            response = self.llm_engine.generate_response(full_prompt)
            print("LanguageAgent: Market brief synthesis completed by LLMEngine.")
            return response
        except Exception as e:
            print(f"LanguageAgent: Error during market brief synthesis: {e}")
            return f"Error synthesizing brief: {e}"

    def summarize_text(self, text: str) -> str:
        # ... (rest of this method is unchanged)
        print("LanguageAgent: Summarizing text using LLMEngine...")
        prompt = f"Summarize the following financial text concisely:\n{text}"
        try:
            return self.llm_engine.generate_response(prompt)
        except Exception as e:
            print(f"LanguageAgent: Error during text summarization: {e}")
            return f"Error summarizing text: {e}"