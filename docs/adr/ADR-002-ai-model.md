# ADR-002: AI Model Selection

**Date:** 2026-05-13
**Status:** Accepted
**Deciders:** Founder

---

## Context

Ghost needs to generate replies that sound like the user — fast, cheap, and conversational.
The model must handle short text, maintain tone consistency, and work within a tight latency
budget (< 2s end-to-end for a natural reply speed).

---

## Options Considered

| Model | Speed | Cost | Quality | Notes |
|---|---|---|---|---|
| Claude Haiku 3.5 | Very fast | ~$0.0008/1k tokens | High | Best tone mimicry |
| Gemini 2.0 Flash | Very fast | ~$0.0003/1k tokens | High | Cheapest at scale |
| GPT-4o Mini | Fast | ~$0.0006/1k tokens | Good | Fallback option |
| Llama 3 (Ollama) | Depends on HW | Free | Medium | Self-hosted option |

---

## Decision

**Primary: Gemini 2.0 Flash** (cheapest, fast, good quality)
**Fallback: Claude Haiku 3.5** (better tone mimicry for edge cases)

Route by user tier:
- Free tier → Gemini Flash
- Pro tier → Claude Haiku (better tone match)

---

## Consequences

- Backend needs a model-router that selects based on user tier
- System prompt must carry ghost profile in every request (no fine-tuning for MVP)
- Token budget: ~500 tokens context + ~100 tokens reply = ~600 tokens/message → ~$0.0002/reply
- At 50 replies/day per user → ~$0.01/user/day → sustainable even on free tier
