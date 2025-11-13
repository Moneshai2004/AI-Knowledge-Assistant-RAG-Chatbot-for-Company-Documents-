from backend.app.core.rag_engine import rag_pipeline, retrieve_similar_chunks

rag_pipeline("data/HR-Policy.pdf")
print(retrieve_similar_chunks("What is refund policy?"))
