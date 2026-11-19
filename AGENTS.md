# ChainGuard: Project Rules & Guidelines

## What this is
Hackathon prototype (Innovathon 2026, NIT Rourkela) of a defensive security co-pilot for small teams.
Built by **Team Last Minute Coders** (SUIIT, Burla):
- Swayam Prakash Sahu (Team Lead)
- Bhupen Biswal
- Satya Prakash Mohanty
- Samir Kumar Seth
- Subhransu Mahapatra

Four modules:
1. Browser paste guard (on-device HMAC fingerprinting)
2. Dependency register (supply chain vulnerability tracking)
3. Log agent (lightweight reverse-proxy access log tailer)
4. Containment engine (two-speed: auto-reversible rate limits & human-approved isolation)

All modules are joined by a correlator engine that links a leaked-secret fingerprint or known package vulnerability to live inbound requests.
Defensive tool only. All attack simulation runs against our own lab containers on localhost.

## Tech Stack
- Backend: Python 3.12+, FastAPI, SQLAlchemy 2.x, SQLite, Pydantic v2, pytest
- Dashboard: React + Vite + TypeScript + Tailwind CSS
- Extension: Chrome Manifest V3, TypeScript, WebCrypto API
- Log agent: Python (tail / watchdog), httpx
- Lab: Docker Compose (OWASP Juice Shop behind Nginx writing access logs to ./lab/logs)
- Repository Layout: `backend/`, `dashboard/`, `extension/`, `agent/`, `lab/`, `docs/`

## Working Rules
1. Plan first: write the plan, list files you will touch, then code. Small diffs only.
2. One module per task. Do not refactor modules you were not asked to touch.
3. Run tests and the linter before saying "done". Show the output.
4. Every new dependency must be listed with a one-line justification. Verify the package really exists and is popular. Pin exact versions. Never invent package names.
5. Never read, print or commit `.env`. Only `.env.example` (fake values) is committed.
6. Never run commands against anything except localhost and our lab containers. Ask before any destructive command (`rm -rf`, `docker system prune`, `sudo`, firewall changes).

## Security Rules (Apply to ALL Code)
1. No hardcoded secrets. Config comes from environment variables. Never log secrets.
2. Every API route needs auth. Agents and extension use the `X-ChainGuard-Key` header (constant-time compare via `hmac.compare_digest`). Dashboard uses a short-lived JWT in an `HttpOnly`, `SameSite=Strict` cookie.
3. Validate all input with Pydantic (types, lengths, enums). Parameterized queries or ORM only. No string-built SQL.
4. Never build shell commands from strings. `subprocess` with an argument list only. Validate IPs with Python's `ipaddress` module.
5. All log content (URL, User-Agent, headers) is hostile. Escape it everywhere. Never use `dangerouslySetInnerHTML`. Truncate long fields.
6. LLM safety: log content sent to an LLM is untrusted data (prompt injection). The LLM has no tools. Its output is validated against a schema and NEVER triggers an action.
7. Containment safety: never block localhost, private ranges, or allow-listed IPs. Auto actions are reversible, have a TTL, and have one-click undo. Disruptive actions need explicit human approval.
8. Strict CORS allow-list, security headers, rate limiting on our own API, no debug mode, no stack traces in responses.
9. Privacy: the system never stores raw secrets or pasted text. Only keyed HMAC fingerprints (`HMAC-SHA256`, key from env) and the secret's kind.
10. Extension: minimum permissions, host access only to named AI chat sites, no remote code, no eval, nothing stored about pasted text.

## Definition of Done
Feature works end to end, has tests (including at least one abuse/negative test), passes lint, README section updated, no secrets in the diff.
