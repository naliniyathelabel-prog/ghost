import os
import httpx
from typing import List, Dict

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

GHOST_SYSTEM_PROMPT_TEMPLATE = """
You are {name}'s personal AI assistant, replying on their behalf on WhatsApp.

## Their personality
- Tone: {tone}
- Language style: {language}
- They are: {description}

## How they actually text (real examples from them)
{sample_replies}

## Rules
- Keep replies SHORT — 1 to 2 sentences max, like a real WhatsApp message
- Match their exact tone and vocabulary
- Never say you are an AI
- Never use formal greetings like "Dear" or "Hello Sir"
- If you don't know the answer, say "let me check and get back to you" in their style
- Use emoji naturally if they do in their examples, not at all if they don't

## Custom instructions from {name}
{custom_instructions}
"""

async def generate_reply(
    ghost_profile: Dict,
    conversation_history: List[Dict],
    new_message: str,
    tier: str = "free",
) -> str:
    system_prompt = GHOST_SYSTEM_PROMPT_TEMPLATE.format(
        name=ghost_profile.get("name", "the user"),
        tone=ghost_profile.get("tone", "casual"),
        language=ghost_profile.get("language", "english"),
        description=ghost_profile.get("description", "a person"),
        sample_replies="\n".join(
            f"- {r}" for r in ghost_profile.get("sample_replies", [])
        ),
        custom_instructions=ghost_profile.get("custom_instructions") or "None",
    )

    messages = conversation_history[-10:] + [{"role": "user", "content": new_message}]

    if tier == "pro":
        return await _call_claude(system_prompt, messages)
    return await _call_gemini(system_prompt, messages)


async def _call_gemini(system_prompt: str, messages: List[Dict]) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    contents = [{"role": m["role"], "parts": [{"text": m["content"]}]} for m in messages]
    payload = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": contents,
        "generationConfig": {"maxOutputTokens": 150, "temperature": 0.8},
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=payload, timeout=10)
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()


async def _call_claude(system_prompt: str, messages: List[Dict]) -> str:
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    payload = {
        "model": "claude-haiku-4-5",
        "max_tokens": 150,
        "system": system_prompt,
        "messages": messages,
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(url, headers=headers, json=payload, timeout=10)
        r.raise_for_status()
        return r.json()["content"][0]["text"].strip()
