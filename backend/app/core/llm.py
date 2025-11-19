import os
from dotenv import load_dotenv
from groq import AsyncGroq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY missing in environment variables")

# create client once (global, reused across all requests)
client = AsyncGroq(api_key=GROQ_API_KEY)


async def generate_answer(question: str, context: str) -> str:
    """
    Generate a strictly RAG-based answer using Groq llama-3.3-70b-versatile.
    """

    prompt = f"""
You are a reliable RAG-based HR assistant.

RULES:
1. Use ONLY the information in CONTEXT.
2. NO outside knowledge.
3. NO guessing.
4. If answer is not directly present in context:
   reply: "Information not found in the provided documents."
5. If partially available → summarize ONLY from context sentences.

---------------------
CONTEXT:
{context}
---------------------

QUESTION:
{question}
"""

    response = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You answer strictly using provided context."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        max_tokens=500
    )

    # Correct Groq output structure
    return response.choices[0].message.content.strip()
