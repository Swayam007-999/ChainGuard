/**
 * On-device HMAC-SHA256 fingerprinting using browser WebCrypto API.
 * Conforms strictly to docs/CONTRACTS.md.
 */

export async function generateFingerprint(secret, key) {
  const enc = new TextEncoder();
  const cryptoKey = await crypto.subtle.importKey(
    "raw",
    enc.encode(key),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );
  const signature = await crypto.subtle.sign(
    "HMAC",
    cryptoKey,
    enc.encode(secret.trim())
  );
  return Array.from(new Uint8Array(signature))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("")
    .toLowerCase();
}
