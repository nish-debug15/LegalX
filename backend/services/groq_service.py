"""
Groq LLM service — handles all AI generation:
1. Summary generation (plain text, 250 words max)
2. Key info extraction (structured JSON)
3. RAG Q&A (context-grounded answers)
4. Card description (one-liner for homepage)

Model: llama3-70b-8192 (Groq free tier)
"""

import os
import json
import logging
from groq import AsyncGroq

logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
MODEL = "llama3-70b-8192"
MAX_TOKENS = 1024
TEMPERATURE = 0.3


SUMMARY_PROMPT = (
    "You are a legal expert simplifying Indian law for common citizens. "
    "Based on the following legal text, write a clear summary in maximum 250 words. "
    "Use simple language. No legal jargon. Write for someone with no legal background.\n\n"
    "Legal Text:\n{context}\n\n"
    "Respond with plain text only."
)

KEY_INFO_PROMPT = (
    "Extract key information from this Indian legal text. "
    "Return ONLY a valid JSON object with exactly these keys. "
    "No markdown, no explanation, just JSON.\n\n"
    '{{"key_rights": ["..."], "important_provisions": ["..."], '
    '"penalties": ["..."], "who_can_benefit": ["..."]}}\n\n'
    "Legal Text:\n{context}"
)

RAG_QA_PROMPT = (
    "You are a legal assistant for Indian law. Answer the user's question using "
    "ONLY the context provided below. If the answer is not in the context, respond: "
    "'This information is outside the scope of this topic.'\n\n"
    "Context:\n{retrieved_chunks}\n\n"
    "Question: {user_question}\n\n"
    "Answer:"
)

CARD_DESCRIPTION_PROMPT = (
    "Write a single sentence (max 15 words) describing what the {topic_name} covers. "
    "Plain language, no jargon."
)


def _get_client() -> AsyncGroq:
    """Create an AsyncGroq client."""
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY environment variable is not set")
    return AsyncGroq(api_key=GROQ_API_KEY)


async def _call_groq(prompt: str) -> str:
    """Make a single Groq API call and return the response text."""
    client = _get_client()
    response = await client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
    )
    return response.choices[0].message.content.strip()


async def generate_summary(context: str) -> str:
    """
    Generate a plain-text summary of legal text.

    Args:
        context: Raw legal text (or concatenated chunks)

    Returns:
        Plain text summary (max ~250 words)
    """
    prompt = SUMMARY_PROMPT.format(context=context)
    summary = await _call_groq(prompt)
    logger.info(f"Generated summary ({len(summary.split())} words)")
    return summary


async def extract_key_info(context: str) -> dict:
    """
    Extract structured key information from legal text.

    Args:
        context: Raw legal text (or concatenated chunks)

    Returns:
        Dict with keys: key_rights, important_provisions, penalties, who_can_benefit
    """
    prompt = KEY_INFO_PROMPT.format(context=context)
    response = await _call_groq(prompt)

    cleaned = response.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    try:
        key_info = json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse key info JSON: {e}\nRaw response: {response}")
        key_info = {
            "key_rights": ["Information could not be extracted. Please try again."],
            "important_provisions": ["Information could not be extracted."],
            "penalties": ["Information could not be extracted."],
            "who_can_benefit": ["Information could not be extracted."],
        }

    logger.info(f"Extracted key info with {sum(len(v) for v in key_info.values())} items")
    return key_info


async def ask_question(retrieved_chunks: str, user_question: str) -> str:
    """
    Answer a user question using RAG (retrieved context only).

    Args:
        retrieved_chunks: Concatenated text of relevant chunks
        user_question: The user's question

    Returns:
        Answer text grounded in the provided context
    """
    prompt = RAG_QA_PROMPT.format(
        retrieved_chunks=retrieved_chunks,
        user_question=user_question,
    )
    answer = await _call_groq(prompt)
    logger.info(f"Generated RAG answer ({len(answer.split())} words)")
    return answer


async def generate_card_description(topic_name: str) -> str:
    """
    Generate a short one-liner description for a topic card.

    Args:
        topic_name: Human-readable topic name (e.g. "POCSO Act")

    Returns:
        Single sentence, max 15 words
    """
    prompt = CARD_DESCRIPTION_PROMPT.format(topic_name=topic_name)
    description = await _call_groq(prompt)
    logger.info(f"Generated card description for '{topic_name}': {description}")
    return description
