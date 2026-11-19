/**
 * ChainGuard On-Device Credential Detector and Shannon Entropy Analyzer.
 * Rule 9 & 10: Runs on-device; never transmits raw secret strings.
 */

export function calculateShannonEntropy(str) {
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

export function redactSecret(secret) {
  if (!secret) return "";
  const trimmed = secret.trim();
  if (trimmed.length <= 8) {
    return "****";
  }
  const prefix = trimmed.slice(0, 4);
  const suffix = trimmed.slice(-4);
  return `${prefix}****${suffix}`;
}

const SECRET_RULES = [
  {
    kind: "aws_access_key",
    regex: /\b(AKIA[0-9A-Z]{16})\b/g,
  },
  {
    kind: "github_token",
    regex: /\b(ghp_[0-9a-zA-Z]{36}|github_pat_[0-9a-zA-Z_]{82})\b/g,
  },
  {
    kind: "stripe_live_key",
    regex: /\b(sk_live_[0-9a-zA-Z]{24,})\b/g,
  },
  {
    kind: "google_api_key",
    regex: /\b(AIza[0-9A-Za-z\-_]{35})\b/g,
  },
  {
    kind: "jwt",
    regex: /\b(eyJ[a-zA-Z0-9_-]{10,}\.eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,})\b/g,
  },
  {
    kind: "pem_private_key",
    regex: /(-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----[^-]*-----END [A-Z0-9 ]*PRIVATE KEY-----)/gs,
  },
];

const GENERIC_ENTROPY_REGEX =
  /(?:api[_-]?key|secret|token|password|auth[_-]?token|bearer)\s*[:=]\s*['"]?([a-zA-Z0-9_\-+/=~!@#$%^&*]{20,})['"]?/gi;

// False positive patterns (e.g. UUID, standard commit hashes without secret prefixes)
const UUID_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export function scanTextForSecrets(text) {
  if (!text || typeof text !== "string") return null;

  // 1. Check strict known provider regexes
  for (const rule of SECRET_RULES) {
    rule.regex.lastIndex = 0;
    const match = rule.regex.exec(text);
    if (match && match[1]) {
      const rawSecret = match[1].trim();
      return {
        kind: rule.kind,
        rawSecret: rawSecret,
        redacted: redactSecret(rawSecret),
      };
    }
  }

  // 2. Check generic high-entropy key-value assignments
  GENERIC_ENTROPY_REGEX.lastIndex = 0;
  let genericMatch;
  while ((genericMatch = GENERIC_ENTROPY_REGEX.exec(text)) !== null) {
    const candidate = genericMatch[1].trim();
    // Exclude UUIDs
    if (UUID_REGEX.test(candidate)) continue;

    // Check Shannon entropy threshold (> 3.5 bits/char indicates high randomness)
    const entropy = calculateShannonEntropy(candidate);
    if (entropy >= 3.5) {
      return {
        kind: "generic_high_entropy_secret",
        rawSecret: candidate,
        redacted: redactSecret(candidate),
      };
    }
  }

  return null;
}
