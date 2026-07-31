import time
from google import genai
from src.config import GEMINI_MODEL_NAME, API_KEY, RETRIEVAL_K
from src.retrieve import retrieve

LEVEL_INSTRUCTIONS = {
    "beginner": "Explain in plain language, avoid jargon, use analogies, define any technical terms you must use.",
    "intermediate": "Assume undergraduate-level physics background. Define only the more advanced or niche terms.",
    "expert": "Use precise technical language and equations where relevant. Do not simplify or over-explain basics.",
}


def build_prompt(query: str, results: dict, level: str) -> str:
    context_blocks = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        context_blocks.append(f"[Source: {meta['source']}, chunk {meta['chunk_index']}]\n{doc}")
    context = "\n\n".join(context_blocks)

    level_instruction = LEVEL_INSTRUCTIONS.get(level, LEVEL_INSTRUCTIONS["intermediate"])

    return f"""You are a physics assistant. Answer the question using ONLY the context below.
If the context doesn't contain enough information to answer, say so honestly — do not guess.
Cite which source(s) you used in your answer.

{level_instruction}

Context:
{context}

Question: {query}

Answer: """


def explain(query: str, level: str = "intermediate"):
    client = genai.Client(api_key=API_KEY)
    results = retrieve(query, k=RETRIEVAL_K)
    prompt = build_prompt(query, results, level)

    # results is in the form dict[list[list[dict, dict, dict, dict, dict]]];
    # e.g. results["metadatas"][0] is list of 5 dictionaries corresponding to first queries' top5 outcomes.
    # Below we are collecting unique sources across all retrieved chunks, preserving order
    sources = list(dict.fromkeys(m["source"] for m in results["metadatas"][0]))

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL_NAME,
                contents=prompt
            )
            answer = (response.text or "").strip()
            if not answer:
                raise ValueError("Empty response body from Gemini")
            return answer, sources
        except Exception as exc:
            wait = 30 * (attempt + 1)
            print(f"  Gemini batch  error (attempt {attempt + 1}/3): {exc} - retrying in {wait}s")
            if attempt < 2:
                time.sleep(wait)
    print(f"  [explain] Gave up after 3 attempts for query: {query!r}")
    return "Sorry, I couldn't generate an explanation right now — please try again."


if __name__ == "__main__":
    answer, sources = explain("What causes the sloshing spiral in galaxy clusters?", level="beginner")
    print(answer)
    print("Sources: ", sources)
