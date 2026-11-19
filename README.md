# ChainGuard

 >By : Swayam Prakash Sahu   

ChainGuard is a defensive security co-pilot built for 1-50 person engineering teams who run live web applications or APIs without a dedicated security hire or 24/7 SOC.

Most security incidents in small teams do not start with zero-day malware. They happen in chains:
1. A developer pastes an API key or database config into an AI chatbot to debug an error.
2. A vulnerable third-party package is pulled in during a late-night fix.
3. Automated scanners probe the application and replay leaked credentials or hit known exploit paths.
4. The attack goes unnoticed for days because existing tools operate in isolation, dump unreadable logs, or trigger noisy false positives.

ChainGuard joins these links together: stopping secrets before they leave the developer's browser, tracking runtime dependencies, analyzing live reverse-proxy traffic, and correlating them so every alert is evaluated by whether it is actually exploitable in your specific application.

---

## Architecture Overview

```
+--------------------+        +---------------------+
|  Chrome Extension  |        |  Python Log Agent   |
| (On-device paste   |        | (Tails Nginx logs;  |
|  guard & HMAC hash)|        |  local token HMAC)  |
+---------+----------+        +----------+----------+
          |                              |
          | POST /v1/fingerprints        | POST /v1/events/batch
          v                              v
+---------------------------------------------------+
|               FastAPI Backend Engine              |
|                                                   |
| - Authentication & Rate Limiting                  |
| - Correlator (Links leak HMACs to live requests)  |
| - Two-Speed Containment Engine                    |
|   * Speed 1: Reversible auto rate-limit + TTL     |
|   * Speed 2: Human-approval for disruptive actions|
| - SQLite 3 Database (SQLAlchemy ORM)              |
+-------------------------+-------------------------+
                          ^
                          | Session Cookie (HttpOnly JWT)
                          v
+---------------------------------------------------+
|           React + Vite Dashboard (Tailwind)       |
|                                                   |
| - Plain-English incident explanations             |
| - One-click approval / rollback controls          |
| - Dependency vulnerability register               |
+---------------------------------------------------+
```

### The Four Modules & The Correlator

1. **Browser Paste Guard (`extension/`)**  
   Chrome Manifest V3 extension running locally on developer workstations. Intercepts paste events on designated AI chat services (ChatGPT, Claude, Gemini). Detects credentials using high-entropy patterns, computes `HMAC-SHA256(key=FINGERPRINT_KEY, secret)` on-device via WebCrypto, and registers only the 64-character hex hash with the backend. **Raw secret strings and conversation text never leave the browser.**

2. **Dependency Register (`backend/`)**  
   Parses `package.json`, `package-lock.json`, and `requirements.txt`. Cross-references dependencies against OSV vulnerability feeds, records CVEs, fixes, and attack signatures (e.g. path traversal, SQLi, JNDI).

3. **Log Agent (`agent/`)**  
   Lightweight Python service monitoring web server access logs (e.g., Nginx). Treats all log lines as hostile. Normalizes fields, extracts exploit flags (`sqli`, `traversal`, `jndi`, `bruteforce`), calculates HMAC fingerprints of tokens in `Authorization` headers and query strings locally, and batches events to the backend.

4. **Correlation Engine (`backend/`)**  
   The core link between detection and live exploitation:
   - If an incoming request uses a token whose HMAC fingerprint matches a secret leaked from the browser extension, the incident is flagged as an active credential compromise.
   - If a request targets an exploit path corresponding to an installed vulnerable dependency, severity escalates to `CRITICAL`.
   - If the probed package is not in the dependency register, the alert is downgraded to prevent alert fatigue.

5. **Two-Speed Containment Engine (`backend/`)**  
   - **Speed 1 (Automatic & Reversible)**: Applies temporary IP rate-limiting or throttling for aggressive scanners. Every rule has an automatic TTL expiry and instant one-click rollback. Localhost (`127.0.0.1`, `::1`), private RFC 1918 subnets, and allowlisted CIDRs can never be auto-blocked.
   - **Speed 2 (Disruptive / Human-Approved)**: Actions such as credential revocation or service isolation require explicit operator confirmation in the dashboard.

---

## Repository Structure

```
.
├── backend/          # FastAPI REST API, SQLAlchemy models, correlator, tests
│   ├── app/          # Application source code (auth, models, routes, security)
│   ├── tests/        # Pytest test suite (auth, negative tests, injection safety)
│   └── requirements.txt
├── dashboard/        # React + TypeScript + Vite + Tailwind dashboard
├── extension/        # Chrome Manifest V3 extension (TypeScript, WebCrypto API)
├── agent/            # Python log agent for tailing access logs
├── lab/              # Docker Compose test environment (OWASP Juice Shop + Nginx)
│   ├── docker-compose.yml
│   ├── nginx.conf
│   └── logs/         # Shared volume for Nginx access logs
├── docs/             # Technical specifications
│   ├── ARCHITECTURE.md # In-depth component design and threat model
│   └── CONTRACTS.md    # API endpoints, data models, and schemas
├── AGENTS.md         # Team conventions and security rules
└── .env.example      # Template environment configuration (fake values only)
```

---

## Quickstart

### Prerequisites
- Python 3.12+
- Node.js 18+ and npm
- Docker and Docker Compose (for the local attack simulation lab)

### 1. Environment Setup

Copy `.env.example` to create your local `.env`:
```bash
cp .env.example .env
```
Ensure `FINGERPRINT_KEY` matches across the backend, agent, and extension configurations.

### 2. Backend Setup & Tests

Create and activate a virtual environment, install dependencies, and run the test suite:
```bash
cd backend
python -m venv .venv

# On Linux/macOS:
source .venv/bin/activate
# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
pytest -v
```

Start the backend server on `http://127.0.0.1:8000`:
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 3. Browser Extension Installation & Demo (`extension/`)

1. Open Google Chrome and navigate to `chrome://extensions`.
2. Enable **Developer mode** toggle in the top-right corner.
3. Click **Load unpacked** and select the `D:\Chain-Guard\extension` folder.
4. Click the ChainGuard extension icon in your toolbar to configure settings:
   - Backend URL: `http://127.0.0.1:8000/v1`
   - Extension API Key: matches `CHAINGUARD_API_KEY` in `.env`
   - Fingerprint Key: matches `FINGERPRINT_KEY` in `.env`
5. **How to Demo**:
   - Open [ChatGPT](https://chatgpt.com) or [Claude](https://claude.ai).
   - Attempt to paste a test AWS key (e.g., `AKIAIOSFODNN7EXAMPLE`) or test Stripe key (e.g., `sk_test_51Abcdefghijklmnopqrstuvwx12345`).
   - ChainGuard intercepts the paste, prevents the raw secret from leaking, computes the `HMAC-SHA256` hash on-device, posts the fingerprint to the backend, and displays the in-page warning modal offering a safe "Paste Redacted" option.

### 4. Lab Environment (Juice Shop + Nginx)

Run the vulnerable target application behind Nginx on port 8080:
```bash
cd lab
docker compose up -d
```
Access the Juice Shop at `http://localhost:8080`. Nginx writes structured access logs containing method, path, status, User-Agent, and authorization headers to `./lab/logs/access.log`.

---

## Security Guarantees & Operating Constraints

- **Zero Raw Secrets Stored**: Raw credentials and prompt text are never persisted or sent over the wire. All token matching relies on keyed `HMAC-SHA256` hashes.
- **Hostile Data Boundary**: Log contents (URLs, User-Agent, headers) are treated as hostile strings. Fields are validated, User-Agent strings are truncated to 200 characters, and parameterized ORM queries are used exclusively.
- **Safe Containment**: Auto-containment explicitly protects localhost and RFC 1918 subnets to prevent self-denial of service.
- **Strict Authentication**: Internal ingestion routes require constant-time API key verification (`hmac.compare_digest`). Dashboard sessions use short-lived JWTs stored in `HttpOnly`, `SameSite=Strict` cookies.

---

## License

Prototype developed for educational and hackathon demonstration purposes under the MIT License.
