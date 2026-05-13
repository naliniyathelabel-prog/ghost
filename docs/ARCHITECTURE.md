# Ghost — System Architecture

## Overview

Ghost is a mobile-first personal WhatsApp AI assistant. The system has four main components
that work together to receive a WhatsApp message, process it through an AI agent trained on
the user's personal voice, and send a reply — all without the official WhatsApp Business API.

---

## System Diagram

```
User's Phone (WhatsApp)
        │
        ▼
┌───────────────────┐
│  Baileys Bridge   │  Node.js process — holds WA Web session
│  (bridge/)        │  Receives inbound, dispatches outbound
└────────┬──────────┘
         │ HTTP (internal)
         ▼
┌───────────────────┐
│  FastAPI Backend  │  AI agent, memory, session, auth
│  (apps/backend/)  │
└────────┬──────────┘
         │ Supabase (Postgres + Auth + Storage)
         ▼
┌───────────────────┐
│  Supabase         │  Users, ghost profiles, message logs
└───────────────────┘
         ▲
         │ REST / Realtime
┌───────────────────┐
│  React Native App │  Mobile UI — onboarding, dashboard, inbox
│  (apps/mobile/)   │
└───────────────────┘
```

---

## Component Responsibilities

### 1. Baileys Bridge (`bridge/`)
- Holds the WhatsApp Web session (QR-linked, persists auth)
- Listens for inbound messages → POSTs to backend `/webhook/inbound`
- Exposes `/send` endpoint for backend to trigger outbound messages
- Runs on user's **residential IP** (not cloud VM) to avoid bans
- Key risk: WhatsApp can detect automation — see ADR-001

### 2. FastAPI Backend (`apps/backend/`)
- `/webhook/inbound` — receives message from bridge, queues AI processing
- `/ai/reply` — builds prompt with Ghost profile + conversation history → calls LLM
- `/ghost` — CRUD for user's Ghost profile (tone, rules, examples)
- `/messages` — message log, review inbox feed
- `/auth` — Supabase Auth JWT validation
- Memory: last N messages per contact stored in Supabase for context window

### 3. Supabase
- `users` — auth, subscription tier
- `ghost_profiles` — system prompt, tone config, sample replies
- `contacts` — per-user contact rules (always reply / ask first / never)
- `message_logs` — inbound + outbound history, thumb ratings

### 4. React Native Mobile App (`apps/mobile/`)
- **Onboarding:** QR scan → train Ghost (5 sample replies) → go live
- **Dashboard:** Ghost ON/OFF toggle, today's stats
- **Inbox:** every AI reply with thumb up/down rating
- **Settings:** contact rules, time rules, language, tone sliders

---

## Data Flow (Happy Path)

```
1. Contact sends WA message to user's number
2. Baileys bridge receives it → POST /webhook/inbound {from, text, timestamp}
3. Backend fetches: ghost_profile + last 10 messages from this contact
4. Backend builds prompt: system_prompt (ghost profile) + conversation history + new message
5. LLM generates reply
6. Backend logs reply → POST bridge /send {to, text}
7. Bridge sends via Baileys
8. Message log updated — visible in mobile inbox
```

---

## Security Boundaries

- Bridge ↔ Backend: internal network only, shared secret header
- Backend ↔ Supabase: service role key, never exposed to mobile
- Mobile ↔ Backend: Supabase JWT, row-level security
- No WhatsApp credentials stored in backend — bridge owns the session file

---

## Known Risks

| Risk | Severity | Mitigation |
|---|---|---|
| WhatsApp bans number for automation | High | Residential IP, warm-up schedule, human-paced delays |
| LLM reply sounds robotic | Medium | Good system prompt, sample replies in training |
| Bridge session expires | Medium | Auto-reconnect logic, mobile alert on disconnect |
| Supabase row-level security misconfigured | High | RLS tests before launch |

---

## Deferred (Post-MVP)

- Multi-number support
- Group chat handling
- Voice message transcription + reply
- Proactive outbound campaigns (customer messaging)
- Self-hosted LLM option (Ollama)
