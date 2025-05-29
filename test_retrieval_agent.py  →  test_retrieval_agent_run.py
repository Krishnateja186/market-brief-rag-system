import sys
import os

# Add current directory to sys.path to find the agents package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.retrieval_agent import RetrievalAgent

def test_retrieval():
    agent = RetrievalAgent()
    documents = [
        "Raga AI is an assistant for financial services.",
        "OpenAI provides models like GPT-4o.",
        "Streamlit is a Python library for making web apps."
    ]
    agent.add_documents(documents)

    query = "What is Raga AI?"
    results = agent.retrieve(query)

    if not results:
        print("No results found.")
    else:
        for doc, score in results:
            print(f"[{score:.2f}] {doc}")

if __name__ == "__main__":
    test_retrieval()
