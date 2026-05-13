# Ghost 👻

> *Your AI twin on WhatsApp. Replies as you, while you live your life.*

Mobile-first personal WhatsApp AI assistant — trained on your voice, slang, and context.
Not a chatbot. A clone.

---

## What It Does

- Connects to your WhatsApp via QR scan (no Meta API needed)
- You train it with 5 real replies → it learns your tone in 2 minutes
- Toggle ON → Ghost handles all incoming messages as you
- Review inbox shows every reply before/after — thumb up/down to improve it

---

## Monorepo Structure

```
ghost/
├── apps/
│   ├── mobile/          # React Native (Expo) — iOS + Android
│   └── backend/         # FastAPI — AI agent, session, memory
├── packages/
│   └── shared/          # Types, constants shared across apps
├── bridge/              # Baileys WhatsApp bridge (Node.js)
├── docs/                # Architecture, ADRs, runbooks
└── infra/               # Docker, deployment configs
```

---

## Stack

| Layer | Tech |
|---|---|
| Mobile | React Native (Expo) |
| Backend | FastAPI + Supabase |
| WhatsApp Bridge | Baileys (WhatsApp Web protocol) |
| AI | Claude Haiku / Gemini Flash |
| Auth | Supabase Auth |
| Hosting | Railway (backend) + Expo EAS (mobile) |

---

## Quick Start (Local Dev)

```bash
# 1. Clone
git clone https://github.com/naliniyathelabel-prog/ghost.git
cd ghost

# 2. Backend
cd apps/backend
cp .env.example .env   # fill in keys
pip install -r requirements.txt
uvicorn main:app --reload

# 3. Bridge
cd ../../bridge
npm install
node index.js          # scan QR on first run

# 4. Mobile
cd ../apps/mobile
npm install
npx expo start
```

---

## Docs

- [Architecture](docs/ARCHITECTURE.md)
- [ADR-001: WhatsApp Bridge Strategy](docs/adr/ADR-001-whatsapp-bridge.md)
- [ADR-002: AI Model Selection](docs/adr/ADR-002-ai-model.md)

---

## Status

🟡 **In active development — not production ready**

See [NEXT_ACTION.md](NEXT_ACTION.md) for current progress.
