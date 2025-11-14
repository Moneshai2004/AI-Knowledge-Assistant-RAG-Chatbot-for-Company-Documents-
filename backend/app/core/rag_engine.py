import os
import faiss
import pickle
from typing import List, Tuple
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
from PyPDF2 import PdfReader
load_dotenv()



EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
VECTOR_STORE_PATH = "data/faiss_index"
EMBEDDINGS_PATH = "data/embeddings.pkl"

def load_pdf_text(file_path: str) -> str:

    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def split_text_into_chunks(text: str) -> List[str]:
  
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
    )
    return splitter.split_text(text)

def create_embeddings(chunks: List[str]) -> List[List[float]]:

    model = SentenceTransformer(EMBEDDING_MODEL)
    embeddings = model.encode(chunks, show_progress_bar=True)
    return embeddings

def build_faiss_index(embeddings: List[List[float]]) -> faiss.IndexFlatL2:
  
    dimension = len(embeddings[0])
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index

def save_index(index, chunks):
    os.makedirs("data", exist_ok=True)
    faiss.write_index(index, VECTOR_STORE_PATH)
    with open(EMBEDDINGS_PATH, "wb") as f:
        pickle.dump(chunks, f)

def load_index():
    index = faiss.read_index(VECTOR_STORE_PATH)
    with open(EMBEDDINGS_PATH, "rb") as f:
        chunks = pickle.load(f)
    return index, chunks

def retrieve_similar_chunks(query: str, top_k: int = 3):
    model = SentenceTransformer(EMBEDDING_MODEL)
    query_emb = model.encode([query])
    index, chunks = load_index()
    D, I = index.search(query_emb, top_k)
    results = [chunks[i] for i in I[0]]
    return results

def answer_query(query: str, context_chunks: List[str]) -> str:

    context = "\n\n".join(context_chunks)
    prompt = f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer clearly:"

    llm = ChatGroq(model="llama-3.3-70b-versatile",temperature=0.1)

    messages = [
        SystemMessage(content="Answer only using the context. Be concise."),
        HumanMessage(content=prompt)
    ]
    response = llm.invoke(messages)
    return response.content

def rag_pipeline(pdf_path: str):

    text = load_pdf_text(pdf_path)
    chunks = split_text_into_chunks(text)
    embeddings = create_embeddings(chunks)
    index = build_faiss_index(embeddings)
    save_index(index, chunks)
    print("RAG index created successfully.")

def ask_question(query: str):

    context = retrieve_similar_chunks(query)
    answer = answer_query(query, context)
    return answer