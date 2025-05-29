# Multi-Source, Multi-Agent Finance Assistant for Spoken Market Briefs

## Project Overview

This project implements an advanced, open-source finance assistant with multiple agents designed to deliver spoken daily market briefs to a portfolio manager. Using a microservices architecture, the system integrates several data sources plus advanced AI. [cite: 1, 2, 7]

## Use Case: Morning Market Brief

At 8 AM upon every trading day, a portfolio manager asks this:
"What is now our risk exposure in Asia tech stocks for today?" Highlight for me any earnings surprises [cite: 6].

The system verbally responds with a concise summary for example.
"Your Asia tech allocation currently stands at 22 % of AUM, an increase from 18 % yesterday. TSMC did beat estimates by 4 %, but Samsung missed estimates by 2 %. Due to the rising yields, the regional sentiment now is neutral, but with a cautionary tilt." [cite: 7]
## Architecture

The system is designed with a modular, microservices-based architecture to ensure scalability and maintainability. [cite: 9] Each specialized agent communicates via FastAPI endpoints, orchestrated to process voice input, perform RAG, analyze data, and synthesize a verbal response. [cite: 9]

### Agent Roles:

* **API Agent:** Polls real-time & historical market data via Yahoo Finance for Asia tech companies. [cite: 8]
* **Scraping Agent:** Crawls filings or fetches structured data from financial APIs (chosen for simplicity and "bingo points" over direct web scraping of raw filings). [cite: 9]
* **Retriever Agent:** Indexes embeddings (using Google Generative AI Embeddings) in FAISS and retrieves top-k chunks of relevant financial information. [cite: 9]
* **Analysis Agent:** Processes raw market data to extract key financial insights, such as portfolio allocation changes and earnings surprises.
* **Language Agent:** Synthesizes the final verbal market brief narrative using a large language model (LLM) (e.g., Gemini 1.5 Flash) leveraging the retrieved and analyzed context (RAG). [cite: 9]
* **Voice Agent (STT & TTS):** Handles Speech-to-Text (STT) via Whisper and Text-to-Speech (TTS) using an open-source toolkit (e.g., gTTS) to manage voice I/O pipelines. [cite: 3, 9]

### Orchestration & Communication:

* Microservices built with FastAPI for each agent. [cite: 9]
* Routing Logic: Voice input → STT → Orchestrator → RAG/Analysis → LLM → TTS or text. [cite: 9]
* Fallback Mechanism: If retrieval confidence falls below a set threshold, the system prompts the user for clarification via voice. [cite: 10]

## Project Structure