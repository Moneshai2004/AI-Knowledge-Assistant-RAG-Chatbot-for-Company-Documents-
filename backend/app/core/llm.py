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

If the answer is not fully explicit, summarize ONLY using the sentences found in the context.
If nothing relevant exists, then say:
"Information not found in the provided documents."


---------------------
CONTEXT:
{context}
---------------------

QUESTION:
{question}
"""

    response = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=500
    )

    # FIX
    return response.choices[0].message.content.strip()
