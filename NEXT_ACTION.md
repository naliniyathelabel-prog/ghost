# NEXT_ACTION.md

**Last updated:** 2026-05-13
**Branch:** main (scaffold complete — feature branches from here)
**Repo:** https://github.com/naliniyathelabel-prog/ghost

---

## What's Done ✅

| Slice | Files | Status |
|---|---|---|
| Repo scaffold | .gitignore, README.md | ✅ |
| Architecture doc | docs/ARCHITECTURE.md | ✅ |
| ADR-001 WhatsApp Bridge | docs/adr/ADR-001 | ✅ |
| ADR-002 AI Model | docs/adr/ADR-002 | ✅ |
| Backend app shell | apps/backend/main.py, requirements.txt | ✅ |
| Backend webhook route | apps/backend/routers/webhook.py | ✅ |
| Backend ghost route | apps/backend/routers/ghost.py | ✅ |
| AI service | apps/backend/services/ai.py | ✅ |
| Baileys bridge | bridge/index.ts, package.json | ✅ |
| Supabase schema | infra/migrations/001_init.sql | ✅ |

---

## Next Slice: `feat/backend-webhook-ai-wired`

Wire the full happy path end-to-end:
1. `/webhook/inbound` → fetch ghost_profile from Supabase → call ai.py → POST /send to bridge
2. Log inbound + outbound to message_logs
3. Add Supabase client singleton to backend
4. Test with a real WhatsApp message manually

**Acceptance criteria:**
- Send a WhatsApp message to the linked number
- Backend logs it in message_logs
- AI generates a reply
- Bridge sends it back
- Message visible in message_logs table

---

## After That: `feat/mobile-scaffold`

- Expo React Native app init
- Onboarding screens: QR scan + train Ghost (5 sample replies)
- Dashboard screen with ON/OFF toggle
- Auth with Supabase

---

## Known Risks (from ADR-001)
- Bridge MUST run on residential IP — not Oracle VM or GCP
- Warm-up: start at 20 msgs/day, ramp over 7 days
- wa-auth/ directory must be backed up — losing it forces re-scan

---

## Recovery
```bash
git clone https://github.com/naliniyathelabel-prog/ghost.git
cd ghost/apps/backend && cp .env.example .env  # fill keys
cd ../../bridge && cp .env.example .env         # fill keys
# restore wa-auth/ from backup
# resume from this file
```
