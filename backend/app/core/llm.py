import os
from groq import AsyncGroq
from dotenv import load_dotenv
load_dotenv()


GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = AsyncGroq(api_key=GROQ_API_KEY)

async def generate_answer(question: str, context: str) -> str:
    prompt = f"""
You are a highly reliable HR & company-policy AI assistant.

Your ONLY knowledge source is the RAG context provided below.
Do NOT use outside knowledge. 
Do NOT guess. 
If the answer is not in the context, you must say:
"Information not found in the provided documents."

Follow these rules STRICTLY:

1. NEVER hallucinate missing information.
2. NEVER answer beyond what the context explicitly states.
3. If context lacks the answer → say the line above.
4. Always cite the source chunks using this format:
   (Source: DOC=<doc_id>, Page=<page>, Score=<score>)
5. If multiple chunks support the answer → cite all of them.
6. If the question asks for a summary → compress, don’t invent.
7. If the question asks for a yes/no → use only context evidence.
8. BE CONCISE. Avoid long paragraphs unless required.
9. Output must be factual, authoritative, and professional.

---------------------
CONTEXT (RAG OUTPUT):
{context}
---------------------

QUESTION:
{question}

Provide the final answer with citations.
"""

    response = await client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        max_tokens=500
    )

    return response.choices[0].message["content"].strip()
