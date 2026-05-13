# NEXT_ACTION.md

**Last updated:** 2026-05-13
**Branch:** main
**Repo:** https://github.com/naliniyathelabel-prog/ghost

---

## What's Done

| Slice | Files | Status |
|---|---|---|
| Repo scaffold | .gitignore, README.md | done |
| Architecture + ADRs | docs/ | done |
| Backend app shell | main.py, requirements.txt, .env.example | done |
| Supabase client | apps/backend/db.py | done |
| Webhook route — WIRED | routers/webhook.py — full happy path | done |
| Ghost route — WIRED | routers/ghost.py — profile, toggle, messages, rate | done |
| AI service | services/ai.py — Gemini Flash + Claude Haiku tier-routed | done |
| Baileys bridge | bridge/index.ts — inbound forward + typing sim + /send | done |
| Supabase schema + RLS | infra/migrations/001_init.sql | done |
| Mobile: API client | apps/mobile/lib/api.ts | done |
| Mobile: Tab layout | app/(tabs)/_layout.tsx | done |
| Mobile: Dashboard | app/(tabs)/index.tsx — Ghost toggle + live stats | done |
| Mobile: Inbox | app/(tabs)/inbox.tsx — message log + thumb rating | done |
| Mobile: Train screen | app/(tabs)/settings.tsx — tone, lang, 5 samples | done |

---

## Next Slice: `feat/e2e-smoke-test`

Full happy path manual test:
1. Run Supabase migration (001_init.sql in SQL editor)
2. Create a user in Supabase Auth, set GHOST_USER_ID in .env
3. POST /ghost/profile with sample profile
4. Start bridge (node bridge/index.ts) → scan QR
5. Start backend (uvicorn main:app --reload)
6. Send a WhatsApp message to the linked number
7. Verify: message logged in message_logs, AI reply sent back
8. Open mobile app → toggle ON → check inbox shows the reply

**Acceptance criteria:**
- One real WhatsApp message triggers one AI reply end-to-end
- message_logs has both inbound + outbound rows
- Mobile inbox shows the reply with rating buttons

---

## After That: `feat/onboarding-flow`

- Mobile onboarding screen: QR scan display (fetch from bridge /qr endpoint)
- Bridge: expose GET /qr as base64 PNG
- First-run flow: Train Ghost → QR Scan → Toggle ON → done

---

## Known Risks
- Bridge MUST run on residential IP (not Oracle VM / GCP)
- Warm-up: 20 msgs/day week 1, ramp to 50/day by week 2
- wa-auth/ directory must be backed up separately

---

## Recovery
```bash
git clone https://github.com/naliniyathelabel-prog/ghost.git
cd ghost/apps/backend && cp .env.example .env   # fill keys
cd ../../bridge && cp .env.example .env          # fill keys
# restore wa-auth/ from secure backup
# run Supabase migration 001_init.sql
# resume from this file
```
