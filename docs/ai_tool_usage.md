# AI Tool Usage Log for Multi-Agent Finance Assistant

This document details the usage of AI tools, specifically Google Gemini (via the `google.generativeai` library), throughout the development of the multi-agent finance assistant project. It logs prompts, generated code/solutions, model parameters, and human interventions.

---

## Log Entries

### 1. Initial Project Understanding and Architecture Design

* **Date:** May 29, 2025
* **Task:** define agent roles, and outline the overall architecture.
* **AI Tool Used:** Google Gemini (Generative Language API)
* **Prompts Used:**
    * "This is my assignment [paste entire assignment description]. Give me a breakdown of how to approach it."
    * "Explain the concept of Retrieval-Augmented Generation (RAG) in the context of an LLM."
    * "How can FastAPI be used to build microservices for different agents?"
* **Generated Code/Solutions (Examples):**
    * High-level architectural overview.
    * Initial thoughts on agent responsibilities and data flow.
* **Model Parameters:** `temperature=0.7`, `top_p=0.95`
* **Human Intervention/Refinements:**
    * Adapted the general architectural advice to specific framework choices (FastAPI, Langchain for RAG components).
    * Clarified the distinct roles of each agent based on assignment's specific labels (API Agent, Scraping Agent, etc.).

---

### 2. Developing the Core LLM Engine (`llm_agent.py`)

* **Date:** May 29, 2025
* **Task:** Create a robust LLM interaction module, including API key handling and model selection.
* **AI Tool Used:** Google Gemini (Generative Language API)
* **Prompts Used:**
    * "I'm getting `google.api_core.exceptions.NotFound: 404 models/gemini-pro is not found`. Here's my `llm_agent.py` and `test_llm_agent.py`. What changes can I make to remove this error?"
    * "My API key credentials seem correct in Google Cloud Console, but I'm still getting 'model not found'. Can you give me code to list all available Gemini models through `google.generativeai`?"
    * "I'm now getting 'Gemini 1.0 Pro Vision has been deprecated'. The error suggests `gemini-1.5-flash`. How can I update my `LLMEngine` to prioritize this model, and gracefully fall back if it's not available?"
* **Generated Code/Solutions (Examples):**
    * Initial `LLMAgent` class structure with `generate_response`.
    * Code snippets for `genai.list_models()`.
    * Refined `LLMEngine` constructor with model prioritization and error handling.
* **Model Parameters:** `temperature=0.5`, `top_p=0.8`
* **Human Intervention/Refinements:**
    * Verified API key and permissions manually in Google Cloud Console.
    * Adjusted `model_priorities` list based on Gemini's direct error messages and `list_models()` output.
    * Ensured consistent print statements for debugging throughout the class.

---

### 3. Implementing the Language Agent (`language_agent.py`)

* **Date:** May 29, 2025
* **Task:** Define the Language Agent's role in synthesizing the market brief using RAG, composing the `LLMEngine`.
* **AI Tool Used:** Google Gemini (Generative Language API)
* **Prompts Used:**
    * "I want my `language_agent.py` to use the `LLMEngine` from `llm_agent.py`. It needs a `synthesize_market_brief` method that takes a query and context documents for RAG. The output format should match this example: 'Today, your Asia tech allocation is...'. Please provide the code with relevant print statements."
    * "My `language_agent.py` currently has `summarize`, `translate`, `rephrase` methods. These aren't strictly for the assignment's market brief. Should I keep them, and how should I adjust the `translate_text` if it's not for a specific foreign language?"
    * "Please provide the complete `language_agent.py` code based on our discussion, focusing on the assignment's requirements."
* **Generated Code/Solutions (Examples):**
    * The `LanguageAgent` class structure, including the `synthesize_market_brief` method.
    * The specific prompt engineering for the RAG task.
    * Advice on whether to keep/remove `summarize`/`translate`/`rephrase`.
* **Model Parameters:** `temperature=0.6`, `top_p=0.85`
* **Human Intervention/Refinements:**
    * Decided to remove `translate_text` and `rephrase_text` to keep the agent focused on core assignment deliverables.
    * Refined the RAG prompt to ensure all aspects of the desired output (AUM, earnings, sentiment) are explicitly covered by the LLM.
    * Ensured proper import structure (`from agents.llm_agent import LLMEngine`).

---

### 4. Developing the API Agent (`api_agent.py`)

* **Date:** May 29, 2025
* **Task:** Create a FastAPI microservice to fetch daily market data and earnings surprises for Asia tech companies.
* **AI Tool Used:** Google Gemini (Generative Language API)
* **Prompts Used:**
    * "I need a FastAPI `api_agent.py` that uses `yfinance` to get daily stock prices for Asia tech companies and also looks for recent earnings surprises. It should return structured data. How can I set this up?"
    * "The assignment specifies 'Asia tech companies'. Can I include all international companies, or should I stick to the specific region?"
    * "Provide the full `api_agent.py` code focusing on Asia tech stocks."
* **Generated Code/Solutions (Examples):**
    * FastAPI app setup, Pydantic models for request/response.
    * `yf.Ticker().history()` and `yf.Ticker().earnings_history` usage.
    * Initial logic for identifying earnings surprises (actual vs. estimated).
* **Model Parameters:** `temperature=0.7`, `top_p=0.9`
* **Human Intervention/Refinements:**
    * Decided to explicitly limit to Asia tech as per assignment scope guidance.
    * Acknowledged the limitations of `yfinance` for precise "today's" earnings surprises and noted the need for a dedicated financial API for robustness.
    * Ensured correct use of `Optional` and type hints.

---

### 5. Creating the Retriever Agent (`retrieval_agent.py`)

* **Date:** May 29, 2025
* **Task:** Build the Retriever Agent microservice for indexing documents using embeddings and retrieving relevant chunks.
* **AI Tool Used:** Google Gemini (Generative Language API)
* **Prompts Used:**
    * "I need a FastAPI microservice for a Retriever Agent. It should use `langchain-google-genai` embeddings and `FAISS` for the vector store. Provide methods for `index_documents` and `retrieve_top_k_chunks`."
    * "My `pip install` for `faiss-cpu` is failing with `WinError 32` and 'process cannot access the file'. What does this mean and how can I fix it?"
    * "Can you provide the complete `retrieval_agent.py` code, including the FastAPI endpoints and the `RetrieverAgent` class, for a production-ready setup?"
* **Generated Code/Solutions (Examples):**
    * `RetrieverAgent` class with `__init__`, `_load_or_create_vector_store`, `index_documents`, `retrieve_top_k_chunks`.
    * FastAPI endpoints (`/index_data`, `/retrieve_chunks`).
    * Debugging advice for `WinError 32`.
* **Model Parameters:** `temperature=0.5`, `top_p=0.8`
* **Human Intervention/Refinements:**
    * Manually ensured `allow_dangerous_deserialization=True` for FAISS loading.
    * Added robust error handling and print statements for initialization and operations.
    * Confirmed correct handling of `Document` objects and metadata for LangChain.

---

### 6. Developing the Analysis Agent (`analysis_agent.py`)

* **Date:** May 29, 2025
* **Task:** Implement the Analysis Agent microservice to process raw market data into structured insights.
* **AI Tool Used:** Google Gemini (Generative Language API)
* **Prompts Used:**
    * "I need a FastAPI `analysis_agent.py` that takes raw stock and earnings data from my API Agent and calculates portfolio allocation (using fixed example data for now), summarizes earnings beats/misses, and includes fixed market sentiment. Provide the code with Pydantic models for input/output and relevant print statements."
    * "How should I structure the output of the Analysis Agent so it's easy for the Language Agent to consume?"
    * "Provide the final code for `analysis_agent.py`."
* **Generated Code/Solutions (Examples):**
    * `StockDataInput`, `EarningsDataInput`, `RawMarketData` (input models).
    * `PortfolioAllocationInsight`, `EarningsSummary`, `MarketSentimentInsight`, `AnalyticalInsights` (output models).
    * Logic for processing and structuring the data.
* **Model Parameters:** `temperature=0.6`, `top_p=0.9`
* **Human Intervention/Refinements:**
    * Ensured the output models are tailored for the Language Agent's RAG context.
    * Explicitly commented on where hardcoded values for AUM/sentiment would come from in a real-world dynamic system.
    * Added robust error handling for API Agent communication.

---

### (Continue adding entries as you build the Orchestrator, Voice Agent, and Streamlit App)

Remember to make an entry every time you use an AI tool for a significant task, debugging, or code generation. Be specific about the prompt, the AI's response, and how you refined it. This file will be key for your evaluation.