from agents.language_agent import LanguageAgent

def test_rag():
    agent = LanguageAgent()
    docs = [
        "Raga AI is a conversational assistant designed for financial services.",
        "It uses retrieval-augmented generation to provide better answers.",
        "Streamlit is used to build the front-end interface."
    ]
    agent.add_documents(docs)

    query = "How does Raga AI help in financial services?"
    answer = agent.rag_answer(query)
    print("RAG Answer:", answer)

if __name__ == "__main__":
    test_rag()
