/**
 * ChainGuard Content Script - Listens for clipboard paste events on generative AI domains.
 * Redacts secrets on-device and transmits only HMAC fingerprints to the backend.
 */

// Detector functions bundled directly for zero-dependency Chrome extension runtime
function calculateShannonEntropy(str) {
  if (!str || str.length === 0) return 0;
  const len = str.length;
  const frequencies = {};
  for (let i = 0; i < len; i++) {
    const char = str[i];
    frequencies[char] = (frequencies[char] || 0) + 1;
  }
  let entropy = 0;
  for (const char in frequencies) {
    const p = frequencies[char] / len;
    entropy -= p * Math.log2(p);
  }
  return entropy;
}

function redactSecret(secret) {
  if (!secret) return "";
  const trimmed = secret.trim();
  if (trimmed.length <= 8) return "****";
  return `${trimmed.slice(0, 4)}****${trimmed.slice(-4)}`;
}

const SECRET_RULES = [
  { kind: "aws_access_key", regex: /\b(AKIA[0-9A-Z]{16})\b/g },
  { kind: "github_token", regex: /\b(ghp_[0-9a-zA-Z]{36}|github_pat_[0-9a-zA-Z_]{82})\b/g },
  { kind: "stripe_live_key", regex: /\b(sk_live_[0-9a-zA-Z]{24,})\b/g },
  { kind: "google_api_key", regex: /\b(AIza[0-9A-Za-z\-_]{35})\b/g },
  { kind: "jwt", regex: /\b(eyJ[a-zA-Z0-9_-]{10,}\.eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,})\b/g },
  { kind: "pem_private_key", regex: /(-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----[^-]*-----END [A-Z0-9 ]*PRIVATE KEY-----)/gs }
];

const GENERIC_ENTROPY_REGEX = /(?:api[_-]?key|secret|token|password|auth[_-]?token|bearer)\s*[:=]\s*['"]?([a-zA-Z0-9_\-+/=~!@#$%^&*]{20,})['"]?/gi;
const UUID_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

function scanText(text) {
  if (!text || typeof text !== "string") return null;

  for (const rule of SECRET_RULES) {
    rule.regex.lastIndex = 0;
    const match = rule.regex.exec(text);
    if (match && match[1]) {
      const raw = match[1].trim();
      return { kind: rule.kind, rawSecret: raw, redacted: redactSecret(raw) };
    }
  }

  GENERIC_ENTROPY_REGEX.lastIndex = 0;
  let genericMatch;
  while ((genericMatch = GENERIC_ENTROPY_REGEX.exec(text)) !== null) {
    const candidate = genericMatch[1].trim();
    if (UUID_REGEX.test(candidate)) continue;
    if (calculateShannonEntropy(candidate) >= 3.5) {
      return { kind: "generic_high_entropy_secret", rawSecret: candidate, redacted: redactSecret(candidate) };
    }
  }
  return null;
}

async function computeWebCryptoHMAC(secret, key) {
  const enc = new TextEncoder();
  const cryptoKey = await crypto.subtle.importKey(
    "raw",
    enc.encode(key),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );
  const sig = await crypto.subtle.sign("HMAC", cryptoKey, enc.encode(secret.trim()));
  return Array.from(new Uint8Array(sig))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("")
    .toLowerCase();
}

function showWarningModal(detected, fullPastedText, targetElement) {
  const existing = document.getElementById("chainguard-paste-guard-modal");
  if (existing) existing.remove();

  const container = document.createElement("div");
  container.id = "chainguard-paste-guard-modal";
  container.style.cssText = `
    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    background: rgba(0, 0, 0, 0.7); z-index: 9999999;
    display: flex; align-items: center; justify-content: center;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  `;

  const box = document.createElement("div");
  box.style.cssText = `
    background: #1e1e2e; color: #cdd6f4; width: 440px; border-radius: 12px;
    padding: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); border: 1px solid #f38ba8;
  `;

  box.innerHTML = `
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
      <div style="background: #f38ba8; color: #11111b; font-weight: bold; padding: 6px 10px; border-radius: 6px; font-size: 13px;">WARNING</div>
      <h3 style="margin: 0; font-size: 18px; color: #f38ba8;">ChainGuard Paste Guard</h3>
    </div>
    <p style="margin: 0 0 12px 0; font-size: 14px; line-height: 1.5; color: #bac2de;">
      A sensitive credential (<strong>${detected.kind}</strong>) was detected in your clipboard.
    </p>
    <div style="background: #181825; padding: 10px 14px; border-radius: 6px; margin-bottom: 18px; font-family: monospace; font-size: 13px; color: #fab387; border: 1px solid #313244;">
      ${detected.redacted}
    </div>
    <div style="display: flex; justify-content: flex-end; gap: 10px;">
      <button id="cg-cancel-btn" style="background: #313244; color: #cdd6f4; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 500;">
        Cancel
      </button>
      <button id="cg-paste-redacted-btn" style="background: #89b4fa; color: #11111b; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: bold;">
        Paste Redacted
      </button>
    </div>
  `;

  container.appendChild(box);
  document.body.appendChild(container);

  document.getElementById("cg-cancel-btn").onclick = () => container.remove();

  document.getElementById("cg-paste-redacted-btn").onclick = () => {
    container.remove();
    // Replace raw secret with redacted version in the full text
    const sanitizedText = fullPastedText.replace(detected.rawSecret, detected.redacted);
    insertTextAtCursor(targetElement, sanitizedText);
  };
}

function insertTextAtCursor(element, text) {
  if (!element) return;
  if (element.tagName === "TEXTAREA" || element.tagName === "INPUT") {
    const start = element.selectionStart || 0;
    const end = element.selectionEnd || 0;
    const val = element.value;
    element.value = val.slice(0, start) + text + val.slice(end);
    element.selectionStart = element.selectionEnd = start + text.length;
    element.dispatchEvent(new Event("input", { bubbles: true }));
  } else if (element.isContentEditable) {
    document.execCommand("insertText", false, text);
  }
}

// Global paste listener
document.addEventListener("paste", async (e) => {
  const clipboardData = e.clipboardData || window.clipboardData;
  if (!clipboardData) return;

  const pastedText = clipboardData.getData("text");
  if (!pastedText) return;

  const detected = scanText(pastedText);
  if (!detected) return;

  // Secret found! Prevent default paste immediately
  e.preventDefault();
  e.stopPropagation();

  // Retrieve configuration from Chrome storage
  chrome.storage.local.get(
    {
      backendUrl: "http://127.0.0.1:8000/v1",
      extensionKey: "cg_live_sample_fake_key_00000000000000000000000000000000",
      fingerprintKey: "fake_fingerprint_hmac_secret_key_1234567890abcdef",
    },
    async (cfg) => {
      try {
        // Calculate HMAC fingerprint on-device
        const fpHex = await computeWebCryptoHMAC(detected.rawSecret, cfg.fingerprintKey);

        // Transmit ONLY the fingerprint to the backend (Never the raw secret)
        fetch(`${cfg.backendUrl.replace(/\/+$/, "")}/fingerprints`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-ChainGuard-Key": cfg.extensionKey,
          },
          body: JSON.stringify({
            fp_hex: fpHex,
            kind: detected.kind,
            source: window.location.hostname,
          }),
        }).catch((err) => console.warn("[ChainGuard] Fingerprint register warning:", err));
      } catch (err) {
        console.error("[ChainGuard] Failed on-device fingerprinting:", err);
      }

      // Display warning modal
      showWarningModal(detected, pastedText, e.target);
    }
  );
}, true);
