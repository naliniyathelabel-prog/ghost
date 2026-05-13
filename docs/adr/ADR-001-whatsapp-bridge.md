# ADR-001: WhatsApp Bridge Strategy

**Date:** 2026-05-13
**Status:** Accepted
**Deciders:** Founder

---

## Context

Ghost needs to send and receive WhatsApp messages on behalf of the user's personal number.
There are two approaches: Meta's official WhatsApp Cloud API, or the unofficial WhatsApp Web
protocol via a library like Baileys.

---

## Options Considered

### Option A: Meta WhatsApp Cloud API (Official)
- Requires Meta Business verification
- Requires pre-approved message templates for outbound
- Costs ₹0.88/conversation after 1,000 free/month
- Messages come from a business number — not the user's personal number
- No risk of ban

### Option B: Baileys (WhatsApp Web Protocol — Unofficial)
- QR-linked to user's own personal/shop number
- No template approval, no Meta verification
- Free — no per-message cost
- Replies appear from the user's real number (personal feel)
- Risk: WhatsApp ToS violation — number can be banned if misused
- Used by OpenClaw, many open-source projects

---

## Decision

**Option B (Baileys)** for MVP.

Reasons:
1. Core product promise is "sounds like you from your real number" — Option A breaks this
2. Target users are small shop owners and individuals, not enterprises
3. Cost-free path lets us validate PMF before monetizing
4. Mitigations (residential IP, warm-up, human-paced delays) reduce ban risk sufficiently for MVP

---

## Consequences

- Bridge must run on a residential IP — user's local machine, Termux on Android, or Raspberry Pi
- Message rate must stay ≤ 50/day with randomized delays (10–30s between messages)
- Users must be warned in onboarding that this uses unofficial protocol
- If WhatsApp hardens detection: migrate to Option A as paid tier
