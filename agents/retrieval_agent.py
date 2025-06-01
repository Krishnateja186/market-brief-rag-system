# agents/retrieval_agent.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import google.generativeai as genai
# For vector store and embeddings, LangChain is a convenient choice
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document # To represent text chunks
import sys

# Load environment variables (for API key)
# Note: For Render, environment variables are set directly in the dashboard,
# so dotenv might not be strictly necessary, but it's good for local testing.
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(
    title="Retriever Agent Microservice",
    description="Indexes data embeddings and retrieves relevant text chunks for RAG."
)

class RetrieverAgent:
    """
    Manages indexing of text data into a vector store and retrieving relevant chunks.
    This agent uses Google Generative AI Embeddings and FAISS for vector storage.
    """
    def __init__(self, vector_store_path: str = "faiss_index", embedding_model_name: str = "models/text-embedding-004"):
        """
        Initializes the RetrieverAgent.

        Args:
            vector_store_path (str): The local path where the FAISS index will be saved/loaded.
            embedding_model_name (str): The name of the Google Generative AI embedding model to use.
                                        Defaults to "models/text-embedding-004".
        """
        print(f"RetrieverAgent: Initializing RetrieverAgent with embedding model '{embedding_model_name}'...")
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            # Critical error: API key is absolutely necessary for embeddings
            print("CRITICAL ERROR: RetrieverAgent: GOOGLE_API_KEY not found for embedding model. Please set it in your Render environment variables or .env file.")
            raise ValueError("RetrieverAgent: GOOGLE_API_KEY not found. Service cannot start without it.")

        # Initialize the embedding model
        # google_api_key is passed directly for robustness
        self.embeddings = GoogleGenerativeAIEmbeddings(model=embedding_model_name, google_api_key=api_key)
        self.vector_store_path = vector_store_path
        self.vectorstore = None
        self._load_or_create_vector_store()
        print(f"RetrieverAgent: Vector store initialized/loaded at '{vector_store_path}'.")

    def _load_or_create_vector_store(self):
        """
        Loads an existing FAISS index from the specified path or creates a new one.
        Handles cases where the index file might be corrupted or non-existent.
        """
        if os.path.exists(self.vector_store_path):
            try:
                # allow_dangerous_deserialization=True is necessary for loading FAISS indexes
                self.vectorstore = FAISS.load_local(self.vector_store_path, self.embeddings, allow_dangerous_deserialization=True)
                print(f"RetrieverAgent: Loaded existing FAISS index from {self.vector_store_path}.")
            except Exception as e:
                print(f"RetrieverAgent: Error loading FAISS index from {self.vector_store_path}: {e}. This might indicate corruption or an incompatible version. Creating a new, empty index.")
                # If loading fails, create a new empty index with a dummy document
                # This ensures vectorstore is always initialized
                try:
                    self.vectorstore = FAISS.from_documents([Document(page_content="initial document for empty index")], self.embeddings)
                    self.vectorstore.save_local(self.vector_store_path)
                    print("RetrieverAgent: Successfully created a new, empty index.")
                except Exception as init_e:
                    print(f"CRITICAL ERROR: RetrieverAgent: Failed to create even an empty index: {init_e}")
                    # If we can't even create an empty index, the service is not functional
                    raise init_e # Re-raise to prevent service startup if this critical step fails
        else:
            print(f"RetrieverAgent: No FAISS index found at {self.vector_store_path}. Creating a new empty index.")
            # A dummy document is needed to initialize an empty FAISS index
            try:
                self.vectorstore = FAISS.from_documents([Document(page_content="initial document for empty index")], self.embeddings)
                self.vectorstore.save_local(self.vector_store_path)
                print("RetrieverAgent: Successfully created a new, empty index.")
            except Exception as init_e:
                print(f"CRITICAL ERROR: RetrieverAgent: Failed to create an empty index from scratch: {init_e}")
                raise init_e # Re-raise to prevent service startup if this critical step fails


    def index_documents(self, documents: List[str], metadata: Optional[List[Dict[str, Any]]] = None) -> int:
        """
        Indexes a list of text documents into the FAISS vector store.

        Args:
            documents: A list of text strings (document content) to be indexed.
            metadata: Optional. A list of dictionaries, where each dictionary
                      corresponds to a document's metadata. Length must match `documents`.

        Returns:
            The number of documents successfully indexed.
        """
        if not documents:
            print("RetrieverAgent: No documents provided for indexing. Returning 0 indexed documents.")
            return 0
        if metadata and len(documents) != len(metadata):
            raise ValueError("RetrieverAgent: Length of documents and metadata must match if metadata is provided.")

        docs_to_add = []
        for i, doc_content in enumerate(documents):
            doc_metadata = metadata[i] if metadata and i < len(metadata) else {}
            docs_to_add.append(Document(page_content=doc_content, metadata=doc_metadata))

        print(f"RetrieverAgent: Attempting to index {len(docs_to_add)} documents into vector store...")
        try:
            # --- START: Debugging prints for indexing ---
            print(f"RetrieverAgent: Debug - Docs to add count: {len(docs_to_add)}")
            if docs_to_add:
                print(f"RetrieverAgent: Debug - First doc content (first 100 chars): {docs_to_add[0].page_content[:100]}")
                print(f"RetrieverAgent: Debug - First doc metadata: {docs_to_add[0].metadata}")
            # --- END: Debugging prints ---

            if self.vectorstore:
                print("RetrieverAgent: Adding documents to existing vector store...")
                # This is the critical line where embeddings are generated and added
                self.vectorstore.add_documents(docs_to_add)
            else:
                # This case should ideally not happen if _load_or_create_vector_store works
                print("RetrieverAgent: Vector store was None during indexing, creating a new one from documents.")
                self.vectorstore = FAISS.from_documents(docs_to_add, self.embeddings)

            print("RetrieverAgent: Documents added successfully. Saving index locally...")
            self.vectorstore.save_local(self.vector_store_path)
            print(f"RetrieverAgent: Successfully indexed {len(docs_to_add)} documents and saved index locally.")
            return len(docs_to_add)
        except Exception as e:
            # Enhanced error logging to capture the exact exception during indexing
            print(f"RetrieverAgent: !!!!! CRITICAL ERROR during document indexing: {type(e).__name__} - {e}")
            raise HTTPException(status_code=500, detail=f"Failed to index documents into vector store: {e}")


    def retrieve_top_k_chunks(self, query: str, k: int = 5) -> List[str]:
        """
        Retrieves the top-k most relevant text chunks from the vector store
        for a given query.

        Args:
            query (str): The search query (e.g., from the Orchestrator or Language Agent).
            k (int): The number of top relevant chunks to retrieve. Defaults to 5.

        Returns:
            List[str]: A list of strings, where each string is the `page_content`
                       of a retrieved relevant document chunk.
        """
        if not self.vectorstore:
            raise HTTPException(status_code=500, detail="RetrieverAgent: Vector store not initialized. Cannot perform retrieval.")

        print(f"RetrieverAgent: Retrieving top {k} chunks for query: '{query}'...")
        try:
            # Use as_retriever and invoke for LangChain's recommended retrieval pattern
            # search_kwargs={"k": k} sets the number of results to retrieve
            retriever = self.vectorstore.as_retriever(search_kwargs={"k": k})
            retrieved_docs = retriever.invoke(query)

            # Extract just the page_content (the text) from the Document objects
            chunks = [doc.page_content for doc in retrieved_docs]
            print(f"RetrieverAgent: Successfully retrieved {len(chunks)} chunks for the query.")
            # Uncomment the line below for detailed debugging of retrieved chunks
            # print(f"RetrieverAgent: Retrieved chunks (first 100 chars each):\n" +
            #       "\n".join([chunk[:100] + "..." for chunk in chunks]))
            return chunks
        except Exception as e:
            print(f"RetrieverAgent: Error during document retrieval: {e}")
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred during retrieval: {e}")


# --- FastAPI Endpoints for Retriever Agent Microservice ---

# Initialize the RetrieverAgent instance. This happens once when the FastAPI application starts.
# Any errors during this initialization will prevent the service from starting.
try:
    # 'faiss_index' is the default path where the vector store will be saved.
    # It will create a directory with this name.
    retriever_agent_instance = RetrieverAgent(vector_store_path="faiss_index")
except Exception as e:
    print(f"CRITICAL ERROR: RetrieverAgent failed to initialize. Service will not be functional.")
    print(f"Initialization Details: {e}")
    # Set the instance to None to prevent calls to an uninitialized agent
    retriever_agent_instance = None
    # For a production system, you might want to uncomment this to prevent the service from running in a bad state
    # sys.exit(1) # Requires 'import sys'

# Pydantic models for request and response bodies of the API endpoints
class IndexRequest(BaseModel):
    """Request model for indexing documents."""
    documents: List[str]
    metadata: Optional[List[Dict[str, Any]]] = None # Optional metadata for each document

class RetrieveRequest(BaseModel):
    """Request model for retrieving document chunks."""
    query: str
    k: int = 5 # Default number of chunks to retrieve

class RetrieveResponse(BaseModel):
    """Response model for retrieved document chunks."""
    chunks: List[str]

@app.get("/")
def root():
    """Root endpoint for Retriever Agent Microservice."""
    return {"message": "Retriever Agent Microservice is running. Visit /docs for API documentation."}

@app.post("/index_data")
async def index_data_endpoint(request: IndexRequest):
    """
    API endpoint to index a list of documents (text strings) into the vector store.
    This would typically be called by the Orchestrator or a data pipeline
    after fetching and preprocessing raw data.
    """
    if retriever_agent_instance is None:
        raise HTTPException(status_code=500, detail="Retriever Agent is not initialized. Check server logs for initialization errors.")
    try:
        indexed_count = retriever_agent_instance.index_documents(request.documents, request.metadata)
        return {"status": "success", "indexed_count": indexed_count}
    except HTTPException as e:
        # Re-raise HTTPException raised by the agent method to pass proper status codes
        raise e
    except Exception as e:
        # Catch any other unexpected errors during indexing
        print(f"RetrieverAgent: !!! UNCAUGHT EXCEPTION in /index_data endpoint: {type(e).__name__} - {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during indexing: {e}")

@app.post("/retrieve_chunks", response_model=RetrieveResponse)
async def retrieve_chunks_endpoint(request: RetrieveRequest):
    """
    API endpoint to retrieve the top-k most relevant text chunks from the
    vector store based on a given query.
    This would typically be called by the Orchestrator before interacting
    with the Language Agent for RAG.
    """
    if retriever_agent_instance is None:
        raise HTTPException(status_code=500, detail="Retriever Agent is not initialized. Check server logs for initialization errors.")
    try:
        chunks = retriever_agent_instance.retrieve_top_k_chunks(request.query, request.k)
        return {"chunks": chunks}
    except HTTPException as e:
        # Re-raise HTTPException raised by the agent method
        raise e
    except Exception as e:
        # Catch any other unexpected errors during retrieval
        print(f"RetrieverAgent: !!! UNCAUGHT EXCEPTION in /retrieve_chunks endpoint: {type(e).__name__} - {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during retrieval: {e}")