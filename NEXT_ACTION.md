# NEXT_ACTION.md

**Last updated:** 2026-05-13
**Active branch:** `feat/backend-webhook-ai-wired`
**Repo:** https://github.com/naliniyathelabel-prog/ghost

---

## What's Done ✅

| Slice | Files | Branch | Status |
|---|---|---|---|
| Repo scaffold | .gitignore, README.md | main | ✅ |
| Architecture + ADRs | docs/ | main | ✅ |
| Backend shell | main.py, requirements.txt | main | ✅ |
| Baileys bridge scaffold | bridge/index.ts | main | ✅ |
| Supabase schema + RLS | infra/migrations/001_init.sql | main | ✅ |
| Supabase client singleton | db/supabase_client.py | feat/backend-webhook-ai-wired | ✅ |
| Ghost service | services/ghost.py | feat/backend-webhook-ai-wired | ✅ |
| Bridge sender service | services/bridge.py | feat/backend-webhook-ai-wired | ✅ |
| /webhook/inbound wired | routers/webhook.py | feat/backend-webhook-ai-wired | ✅ |
| /messages inbox + rating | routers/messages.py | feat/backend-webhook-ai-wired | ✅ |
| /messages/stats | routers/messages.py | feat/backend-webhook-ai-wired | ✅ |
| Docker Compose + Dockerfiles | docker-compose.yml | feat/backend-webhook-ai-wired | ✅ |

---

## Full API Surface (Backend)

| Method | Route | Purpose |
|---|---|---|
| GET | /health | Health check |
| POST | /webhook/inbound | Bridge → backend (inbound WA message) |
| GET | /ghost/profile | Fetch ghost profile |
| PUT | /ghost/profile | Update ghost profile (tone, samples) |
| POST | /ghost/toggle | Toggle Ghost ON/OFF |
| GET | /messages/ | Inbox — list all AI replies |
| PATCH | /messages/{id}/rating | Thumbs up/down on a reply |
| GET | /messages/stats | Dashboard stats |

---

## Next Slice: `feat/mobile-scaffold`

Expo React Native app with:
1. **Onboarding flow:**
   - Screen 1: Welcome + "What is Ghost"
   - Screen 2: Connect WhatsApp (show QR from bridge)
   - Screen 3: Train Ghost — 5 sample reply inputs + tone/language sliders
   - Screen 4: Go live — Ghost ON toggle
2. **Dashboard screen:** ON/OFF toggle + today's stats card
3. **Inbox screen:** FlatList of AI replies + thumb up/down rating
4. **Supabase Auth:** email/OTP login

**Acceptance criteria:**
- User can complete onboarding in < 2 minutes
- Ghost ON/OFF toggle calls `/ghost/toggle`
- Inbox loads from `/messages/`
- Rating tap calls `/messages/{id}/rating`

---

## To Manually Test the Happy Path Right Now

```bash
# 1. Run migration in Supabase SQL editor
#    infra/migrations/001_init.sql

# 2. Create a user in Supabase Auth, copy UUID → GHOST_USER_ID in .env

# 3. Insert a test ghost profile in Supabase:
#    INSERT INTO ghost_profiles (user_id, name, tone, active)
#    VALUES ('your-uuid', 'Test', 'casual', true);

# 4. Start bridge (on your LOCAL machine, not cloud):
cd bridge && npm install && node index.ts   # scan QR

# 5. Start backend:
cd apps/backend && pip install -r requirements.txt
uvicorn main:app --reload

# 6. Send a WhatsApp message to your linked number
# 7. Check Supabase message_logs table — should see inbound + AI outbound
# 8. Check GET /messages/ — should list both
```

---

## Known Risks
- Bridge MUST run on residential IP (your laptop / phone Termux / Raspberry Pi)
- wa-auth/ folder = your WA session — back it up, losing it forces re-scan
- GHOST_USER_ID is hardcoded for MVP single-user mode — multi-user needs auth middleware

---

## Recovery
```bash
git clone https://github.com/naliniyathelabel-prog/ghost.git
cd ghost
git checkout feat/backend-webhook-ai-wired
# restore .env files, wa-auth/ from backup
# resume from this file
```
