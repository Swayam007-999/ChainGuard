# ChainGuard API & Data Contracts

This document establishes the exact data models, API endpoints, serialization schemas, and hashing algorithms for ChainGuard. All 5 modules (`extension/`, `agent/`, `backend/`, `dashboard/`, `lab/`) must conform strictly to these contracts.

---

## 1. Cryptographic Fingerprinting Specification

To uphold privacy guarantees, raw tokens, API keys, and sensitive pasted strings **never leave their local runtime unhashed**.

- **Algorithm**: `HMAC-SHA256`
- **Secret Key**: `FINGERPRINT_KEY` (Loaded from environment variable in backend and agent; configured via extension settings)
- **Input Encoding**: Raw secret string encoded as UTF-8 bytes (trimmed of leading/trailing whitespace)
- **Output Format**: Lowercase hexadecimal string (exactly 64 characters)

### Cross-Language Reference Implementations

#### Python (Backend & Agent)
```python
import hmac
import hashlib

def generate_fingerprint(secret: str, key: str) -> str:
    key_bytes = key.encode("utf-8")
    msg_bytes = secret.strip().encode("utf-8")
    return hmac.new(key_bytes, msg_bytes, hashlib.sha256).hexdigest().lower()
```

#### TypeScript / WebCrypto (Chrome Extension)
```typescript
async function generateFingerprint(secret: string, key: string): Promise<string> {
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
```

---

## 2. Database Schema (SQLite 3)

### 2.1 Table: `fingerprints`
Records HMAC hashes of sensitive tokens detected client-side by the extension.
```sql
CREATE TABLE fingerprints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fp_hex TEXT NOT NULL,                     -- 64-char lowercase hex
    kind TEXT NOT NULL,                       -- e.g. "aws_key", "jwt", "generic_token"
    source TEXT NOT NULL,                     -- e.g. "chatgpt.com", "claude.ai"
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_fingerprints_hex ON fingerprints(fp_hex);
```

### 2.2 Table: `dependencies`
Maintains the runtime package inventory scanned from manifests/lockfiles.
```sql
CREATE TABLE dependencies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    app TEXT NOT NULL,                        -- Service or application name
    ecosystem TEXT NOT NULL,                  -- "npm" | "pypi"
    name TEXT NOT NULL,                       -- e.g. "jsonwebtoken"
    version TEXT NOT NULL                     -- e.g. "8.5.1"
);
CREATE UNIQUE INDEX idx_deps_app_pkg ON dependencies(app, ecosystem, name, version);
```

### 2.3 Table: `vulns`
Stores known security advisories associated with scanned dependencies.
```sql
CREATE TABLE vulns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dependency_id INTEGER NOT NULL REFERENCES dependencies(id) ON DELETE CASCADE,
    osv_id TEXT NOT NULL,                     -- e.g. "GHSA-798r-2798-7688"
    summary TEXT NOT NULL,
    severity TEXT NOT NULL,                   -- "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
    fixed_in TEXT,                            -- Version fixing the issue or NULL
    exploit_keywords JSON NOT NULL            -- JSON list of strings, e.g. ["traversal", "rce"]
);
CREATE INDEX idx_vulns_dep_id ON vulns(dependency_id);
```

### 2.4 Table: `events`
High-throughput buffer of incoming web/API request summaries parsed by the Log Agent.
```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TIMESTAMP NOT NULL,                    -- ISO-8601 request timestamp
    ip TEXT NOT NULL,                         -- Client IP address (validated IPv4/IPv6)
    method TEXT NOT NULL,                     -- HTTP Method (e.g. "GET", "POST")
    path TEXT NOT NULL,                       -- Request URI / route
    status INTEGER NOT NULL,                  -- HTTP status code (e.g. 200, 403, 500)
    ua TEXT NOT NULL,                         -- User-Agent (max 200 chars, escaped)
    flags JSON NOT NULL,                      -- JSON list: ["sqli", "traversal", "jndi", "bruteforce"]
    token_fps JSON NOT NULL                   -- JSON list of 64-char hex strings
);
CREATE INDEX idx_events_ts ON events(ts);
CREATE INDEX idx_events_ip ON events(ip);
```

### 2.5 Table: `incidents`
Correlated findings combining human leaks, vulnerable dependencies, and active live traffic.
```sql
CREATE TABLE incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    severity TEXT NOT NULL,                   -- "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
    status TEXT NOT NULL,                     -- "open" | "contained" | "resolved" | "dismissed"
    title TEXT NOT NULL,
    evidence JSON NOT NULL,                   -- Correlated IDs {fingerprint_ids, event_ids, vuln_ids}
    explanation JSON NOT NULL,                -- Plain-English summary {what_happened, why_it_matters, recommended_action}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2.6 Table: `actions`
Defensive mitigations generated by the Two-Speed Containment Engine.
```sql
CREATE TABLE actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id INTEGER NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
    type TEXT NOT NULL,                       -- "rate_limit_ip" | "revoke_token" | "isolate_service"
    reversible BOOLEAN NOT NULL,              -- true for rate limits, false for revocations
    status TEXT NOT NULL,                     -- "pending" | "applied" | "undone" | "expired"
    target TEXT NOT NULL,                     -- e.g. "198.51.100.24" or "API_KEY_ID"
    expires_at TIMESTAMP                      -- Nullable; auto-expiry time for temporary blocks
);
CREATE INDEX idx_actions_status ON actions(status);
```

### 2.7 Table: `allowlist`
Network CIDR blocks exempt from automatic containment actions.
```sql
CREATE TABLE allowlist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cidr TEXT NOT NULL UNIQUE,                -- e.g. "203.0.113.0/24"
    note TEXT NOT NULL                        -- e.g. "Office VPN", "Payment Webhook"
);
```

---

## 3. REST API Specification (Version 1)

All endpoints are prefixed with `/v1`. Responses are formatted in JSON with consistent structure.

### 3.1 Authentication & Credentials
- **Service Authentication (Extension & Log Agent)**:
  - Header: `X-ChainGuard-Key: <token>`
  - Evaluated using constant-time string comparison (`hmac.compare_digest`).
- **User / Operator Authentication (Dashboard)**:
  - Endpoint: `POST /v1/auth/login`
  - Cookie: `access_token=<jwt>; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=28800`

---

### 3.2 Endpoints Summary

| Method | Path | Required Auth | Source / Consumer | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/v1/auth/login` | None | Dashboard | Authenticate admin operator; issue JWT cookie |
| `POST` | `/v1/fingerprints` | `X-ChainGuard-Key` | Extension | Register on-device leaked secret fingerprint |
| `POST` | `/v1/dependencies/scan` | Dashboard Cookie | Dashboard | Upload manifest/lockfile for dependency parsing |
| `GET` | `/v1/dependencies` | Dashboard Cookie | Dashboard | List tracked dependencies and known CVEs |
| `POST` | `/v1/events/batch` | `X-ChainGuard-Key` | Log Agent | Ingest batch of parsed log events (max 500) |
| `GET` | `/v1/incidents` | Dashboard Cookie | Dashboard | Retrieve prioritized list of security incidents |
| `GET` | `/v1/incidents/{id}` | Dashboard Cookie | Dashboard | Retrieve deep evidence and timeline for an incident |
| `POST` | `/v1/actions/{id}/approve` | Dashboard Cookie | Dashboard | Execute human-approved disruptive action |
| `POST` | `/v1/actions/{id}/undo` | Dashboard Cookie | Dashboard | Revert an applied containment action |
| `GET` | `/v1/allowlist` | Dashboard Cookie / Key | Dashboard / Internal | List network CIDR allowlists |
| `POST` | `/v1/allowlist` | Dashboard Cookie | Dashboard | Add new CIDR allowlist entry |

---

### 3.3 Detailed Request & Response Payloads

#### `POST /v1/auth/login`
- **Request Body**:
  ```json
  {
    "password": "string"
  }
  ```
- **Response `200 OK`**:
  ```json
  {
    "status": "authenticated",
    "expires_in": 28800
  }
  ```
- **Error `401 Unauthorized`**:
  ```json
  {
    "detail": "Invalid credentials"
  }
  ```

#### `POST /v1/fingerprints`
- **Header**: `X-ChainGuard-Key: <CHAINGUARD_API_KEY>`
- **Request Body**:
  ```json
  {
    "fp_hex": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "kind": "stripe_secret_key",
    "source": "chatgpt.com"
  }
  ```
- **Validation**:
  - `fp_hex`: Must match regex `^[a-f0-9]{64}$`
  - `kind`: Max 64 characters
  - `source`: Max 128 characters
- **Response `201 Created`**:
  ```json
  {
    "id": 1,
    "fp_hex": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "kind": "stripe_secret_key",
    "source": "chatgpt.com",
    "detected_at": "2026-11-10T02:00:00Z"
  }
  ```

#### `POST /v1/events/batch`
- **Header**: `X-ChainGuard-Key: <CHAINGUARD_API_KEY>`
- **Request Body**:
  ```json
  {
    "events": [
      {
        "ts": "2026-11-10T02:00:00Z",
        "ip": "198.51.100.42",
        "method": "POST",
        "path": "/rest/user/login",
        "status": 401,
        "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "flags": ["sqli", "bruteforce"],
        "token_fps": [
          "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        ]
      }
    ]
  }
  ```
- **Validation**:
  - `events`: Array length between `1` and `500` items.
  - `ip`: Valid IPv4 or IPv6 address string.
  - `ua`: Maximum length truncated to 200 characters.
  - `flags`: List of allowed strings: `"sqli"`, `"traversal"`, `"jndi"`, `"bruteforce"`.
  - `token_fps`: List of strings matching `^[a-f0-9]{64}$`.
- **Response `200 OK`**:
  ```json
  {
    "status": "success",
    "stored": 1
  }
  ```

#### `GET /v1/allowlist`
- **Response `200 OK`**:
  ```json
  [
    {
      "id": 1,
      "cidr": "192.168.1.0/24",
      "note": "Office Local Network"
    }
  ]
  ```

#### `POST /v1/allowlist`
- **Request Body**:
  ```json
  {
    "cidr": "203.0.113.0/24",
    "note": "Production Payment Gateway Webhook"
  }
  ```
- **Validation**: `cidr` must be parsed successfully by Python `ipaddress.ip_network(strict=False)`.
- **Response `201 Created`**:
  ```json
  {
    "id": 2,
    "cidr": "203.0.113.0/24",
    "note": "Production Payment Gateway Webhook"
  }
  ```
