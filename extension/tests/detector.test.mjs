import test from "node:test";
import assert from "node:assert/strict";
import {
  scanTextForSecrets,
  calculateShannonEntropy,
  redactSecret,
} from "../detector.js";

test("Redaction retains 4-char prefix and suffix with masked middle", () => {
  const secret = "AKIA" + "12345678" + "WXYZ";
  const redacted = redactSecret(secret);
  assert.equal(redacted, "AKIA****WXYZ");
});

test("Programmatic test vector: AWS Access Key ID detected", () => {
  const awsKey = "AK" + "IA" + "1234567890ABCDEF";
  const result = scanTextForSecrets(`Deploy error with credentials: ${awsKey}`);
  assert.ok(result);
  assert.equal(result.kind, "aws_access_key");
  assert.equal(result.rawSecret, awsKey);
  assert.equal(result.redacted, "AKIA****CDEF");
});

test("Programmatic test vector: GitHub Personal Access Token detected", () => {
  const ghpToken = "gh" + "p_" + "1234567890abcdef1234567890abcdef1234";
  const result = scanTextForSecrets(`git push origin main using token ${ghpToken}`);
  assert.ok(result);
  assert.equal(result.kind, "github_token");
  assert.equal(result.rawSecret, ghpToken);
});

test("Programmatic test vector: Stripe Live Secret Key detected", () => {
  const stripeKey = "sk" + "_live_" + "51Abcdefghijklmnopqrstuvwx123456789";
  const result = scanTextForSecrets(`const stripe = new Stripe("${stripeKey}");`);
  assert.ok(result);
  assert.equal(result.kind, "stripe_live_key");
  assert.equal(result.rawSecret, stripeKey);
});

test("Programmatic test vector: Google API Key detected", () => {
  const googleKey = "AI" + "za" + "SyD1234567890abcdefghijklmnopqrstuv";
  const result = scanTextForSecrets(`Maps API configuration: key=${googleKey}`);
  assert.ok(result);
  assert.equal(result.kind, "google_api_key");
  assert.equal(result.rawSecret, googleKey);
});

test("Programmatic test vector: JWT Token detected", () => {
  const jwtToken =
    "ey" +
    "JhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9." +
    "ey" +
    "JzdWIiOiIxMjM0NTY3ODkwIn0." +
    "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk";
  const result = scanTextForSecrets(`Authorization: Bearer ${jwtToken}`);
  assert.ok(result);
  assert.equal(result.kind, "jwt");
});

test("Programmatic test vector: PEM Private Key header detected", () => {
  const pem =
    "-----BEGIN " +
    "RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA0...\n-----END " +
    "RSA PRIVATE KEY-----";
  const result = scanTextForSecrets(pem);
  assert.ok(result);
  assert.equal(result.kind, "pem_private_key");
});

test("Programmatic test vector: Generic High-Entropy token detected", () => {
  // High entropy random string
  const highEntropy = "xK9" + "#mP$2vL!9qR@5tZ&8wY*1";
  const result = scanTextForSecrets(`api_key = "${highEntropy}"`);
  assert.ok(result);
  assert.equal(result.kind, "generic_high_entropy_secret");
});

test("False positive negative test: UUIDs are not detected as secrets", () => {
  const uuid = "550e8400-e29b-41d4-a716-446655440000";
  const result = scanTextForSecrets(`User session request id: ${uuid}`);
  assert.equal(result, null);
});

test("False positive negative test: Git commit hash is not detected", () => {
  const gitHash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4";
  const result = scanTextForSecrets(`Commit SHA: ${gitHash}`);
  assert.equal(result, null);
});

test("False positive negative test: Normal prose and code snippets are safe", () => {
  const normalText = `
    function calculateTotal(price, taxRate) {
      // Return total rounded to two decimals
      return price * (1 + taxRate);
    }
    console.log("Server running on port 8080");
  `;
  const result = scanTextForSecrets(normalText);
  assert.equal(result, null);
});
