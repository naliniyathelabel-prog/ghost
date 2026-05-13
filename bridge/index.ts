import makeWASocket, {
  useMultiFileAuthState,
  DisconnectReason,
  fetchLatestBaileysVersion,
} from "@whiskeysockets/baileys";
import express from "express";
import { Boom } from "@hapi/boom";
import axios from "axios";
import dotenv from "dotenv";
import pino from "pino";

dotenv.config();

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";
const BRIDGE_SECRET = process.env.BRIDGE_SECRET || "change-me";
const PORT = parseInt(process.env.PORT || "3001");
const logger = pino({ level: "info" });
const app = express();
app.use(express.json());

let sock: ReturnType<typeof makeWASocket> | null = null;

async function startBridge() {
  const { state, saveCreds } = await useMultiFileAuthState("./wa-auth");
  const { version } = await fetchLatestBaileysVersion();

  sock = makeWASocket({
    version,
    auth: state,
    logger: pino({ level: "silent" }),
    printQRInTerminal: true,
  });

  sock.ev.on("creds.update", saveCreds);

  sock.ev.on("connection.update", ({ connection, lastDisconnect, qr }) => {
    if (qr) logger.info("Scan QR code to link WhatsApp");
    if (connection === "close") {
      const shouldReconnect =
        (lastDisconnect?.error as Boom)?.output?.statusCode !==
        DisconnectReason.loggedOut;
      if (shouldReconnect) {
        logger.info("Reconnecting...");
        startBridge();
      } else {
        logger.warn("Logged out — rescan QR to reconnect");
      }
    }
    if (connection === "open") logger.info("WhatsApp connected ✓");
  });

  // Inbound messages → backend
  sock.ev.on("messages.upsert", async ({ messages, type }) => {
    if (type !== "notify") return;
    for (const msg of messages) {
      if (msg.key.fromMe) continue;
      const text =
        msg.message?.conversation ||
        msg.message?.extendedTextMessage?.text ||
        "";
      if (!text) continue;
      try {
        await axios.post(
          `${BACKEND_URL}/webhook/inbound`,
          { from: msg.key.remoteJid, text, timestamp: msg.messageTimestamp },
          { headers: { "x-bridge-secret": BRIDGE_SECRET } }
        );
      } catch (e) {
        logger.error("Failed to forward to backend", e);
      }
    }
  });
}

// Outbound: backend calls this to send a message
app.post("/send", async (req, res) => {
  if (req.headers["x-bridge-secret"] !== BRIDGE_SECRET) {
    return res.status(401).json({ error: "Unauthorized" });
  }
  const { to, text } = req.body as { to: string; text: string };
  if (!sock) return res.status(503).json({ error: "Bridge not connected" });
  try {
    // Human-paced: simulate typing delay
    await sock.sendPresenceUpdate("composing", to);
    await new Promise((r) =>
      setTimeout(r, 1000 + Math.random() * text.length * 30)
    );
    await sock.sendPresenceUpdate("paused", to);
    await sock.sendMessage(to, { text });
    res.json({ ok: true });
  } catch (e) {
    res.status(500).json({ error: String(e) });
  }
});

app.get("/health", (_req, res) => res.json({ ok: true }));

app.listen(PORT, () => logger.info(`Bridge listening on :${PORT}`));
startBridge();
