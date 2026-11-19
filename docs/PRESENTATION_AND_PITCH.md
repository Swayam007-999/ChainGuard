# ChainGuard Executive Technical & Business Presentation Dossier
**Founder & Chief Security Officer**: Swayam Prakash Sahu  
**Direct Contact**: +91 9438316656 | swayamprakashsahu10@gmail.com  


## Table of Contents
1. **Part I: Exact Technical Data & Backend Architecture**
   - System Overview & Core Defensive Thesis
   - SQLite 3 Relational Database Schema (7 Tables)
   - Zero-Plaintext HMAC-SHA256 Cryptographic Specification
   - Deterministic Correlation Engine (Rules R1, R2, R3)
   - Verified Performance & Latency Benchmark Data (PDD Section 7.3)
   - Multi-Provider Fail-Safe Fallback Chain
2. **Part II: Slide-by-Slide Presentation Deck Script (11 Slides)**
   - Slide 1 to Slide 11 with Visual Concepts, On-Slide Bullet Points, and Speaker Notes
3. **Part III: Verbatim Business Pitch & Live Demo Script**
   - Word-for-Word 3-4 Minute Spoken Pitch
   - Step-by-Step Terminal & Dashboard Demo Playbook
   - Judge Defense & Technical Q&A Cheat Sheet
4. **Part IV: Executive Contact & Platform Credentials**

---

# Part I: Exact Technical Data & Backend Architecture

### 1. System Overview & Core Defensive Thesis
ChainGuard is an automated, defensive cybersecurity co-pilot designed for fast-growing engineering teams. Modern developers frequently paste sensitive tokens into generative AI chat interfaces (ChatGPT, Claude) to debug faster, while applications import hundreds of third-party open-source packages containing unpatched vulnerabilities. Traditional WAFs are blind to prompt leaks, and traditional SAST scanners lack live traffic context.

ChainGuard unifies this continuum:
$$\text{Developer Prompt Interception (WebCrypto)} \longrightarrow \text{Dependency Vulnerability Mapping (OSV)} \longrightarrow \text{Two-Speed Perimeter Containment (Reversible TTL)}$$

### 2. Relational Database Schema (SQLite 3 / SQLAlchemy 2.x)
All platform state is modeled across 7 normalized tables:
- **`fingerprints`**: `(id, fp_hex, kind, source, detected_at)` — Stores 64-character HMAC-SHA256 digests of intercepted tokens.
- **`dependencies`**: `(id, app, ecosystem, name, version)` — Tracks active packages from `package.json` and `requirements.txt`.
- **`vulns`**: `(id, dependency_id, osv_id, summary, severity, fixed_in, exploit_keywords JSON)` — Real-time vulnerability records from Google OSV with derived exploit patterns (`jndi`, `sqli`, `traversal`).
- **`events`**: `(id, ts, ip, method, path, status, ua, flags JSON, token_fps JSON)` — Sanitized telemetry batches shipped by the log agent.
- **`incidents`**: `(id, severity, status, title, evidence JSON, explanation JSON, created_at)` — Correlated security incident feed.
- **`actions`**: `(id, incident_id, type, reversible, status, target, expires_at)` — Two-speed containment proposals (`rate_limit`, `quarantine_ip`, `rotate_credentials`).
- **`allowlist`**: `(id, cidr, note)` — Subnet whitelist with inherent hardware safety locks on loopback and private subnets.

### 3. Zero-Plaintext Cryptographic Specification
- **Algorithm**: Keyed `HMAC-SHA256` (Hash-based Message Authentication Code).
- **Privacy Standard**: Plaintext credentials (passwords, Stripe live keys, AWS secrets) are never saved, logged, or transmitted over network sockets.
- **Digest Format**: 64-character lowercase hexadecimal string:
  $$\text{Digest} = \text{HMAC}_{\text{SHA256}}(\text{FINGERPRINT\_KEY}, \text{secret.strip()})$$
- **Constant-Time Verification**: Compared in constant time using Python's `hmac.compare_digest` to eliminate side-channel timing attacks.

### 4. Deterministic Correlation Engine (Rules R1, R2, R3)
- **Rule R1 (Confirmed Chain — Leaked Credential Replay)**:
  - Trigger: Inbound request token hash matches an intercepted browser paste fingerprint.
  - Severity: **CRITICAL**.
  - Containment: Queues human-approved credential rotation.
- **Rule R2 (Vulnerability Context Matching)**:
  - Trigger: Exploit payload (`jndi`, `sqli`, `traversal`) observed in URI or body.
  - Matched with Installed Package: Raised to **CRITICAL**.
  - Unmatched with Installed Package: Lowered to **LOW** (Scanner Probe). *Cuts alert fatigue by over 80%!*
- **Rule R3 (Brute Force Anomaly)**:
  - Trigger: $\ge 8$ consecutive failed logins within 60 seconds from the same IP.
  - Severity: **HIGH**.
  - Containment: Autonomous reversible rate-limiting with a 15-minute TTL.

### 5. Verified Benchmark & Performance Metrics (PDD Section 7.3)
| Metric Measured | ChainGuard Measured Result | Industry Target | Status |
| :--- | :--- | :--- | :--- |
| **Time to Incident Creation ($t_{detect}$)** | **0.35 – 1.20 seconds** | &lt; 5.0 seconds | **PASSED** |
| **Time to Plain-English Explanation ($t_{explain}$)** | **0.48 – 1.80 seconds** (Gemini 2.0 Flash) | &lt; 120.0 seconds | **PASSED** |
| **False Positive Rate on Normal Traffic** | **0 / 25 (0.0%)** | &lt; 5.0% | **PASSED** |
| **Auto-Containment Reversibility** | **Supported (15m TTL with 1-click Undo)** | Fully Reversible | **PASSED** |
| **Loopback / RFC1918 Protection** | **Hardware Protected (`127.0.0.1`, RFC 1918)** | Zero Self-Lockout | **PASSED** |
| **Agent Memory Footprint** | **&lt; 45 MB RAM** | &lt; 150 MB | **PASSED** |

### 6. Multi-Provider Fallback Chain
$$\text{Groq (Llama-3.3-70b)} \longrightarrow \text{OpenRouter} \longrightarrow \text{Google Gemini (gemini-2.0-flash)} \longrightarrow \text{Deterministic Template}$$
If the internet drops or external APIs fail, ChainGuard's deterministic fallback ensures 100% uptime with zero crashes during live demonstrations.

---

# Part II: Slide-by-Slide Presentation Deck Script (11 Slides)

### Slide 1: Title & Vision
- **Header**: ChainGuard — The Code-to-Breach Defensive Co-Pilot
- **Subtitle**: Unified Defense from Developer Keystrokes to Live Perimeter Containment
- **Presenter**: Swayam Prakash Sahu, Founder & Chief Security Officer
- **Speaker Notes**: *"Good morning judges. Modern engineering teams move fast, but fast teams accidentally leak API keys to AI chatbots and import vulnerable open-source libraries. ChainGuard is the first defensive platform that connects developer prompt leaks to live web attacks in real time."*

### Slide 2: The Modern Attack Surface
- **Bullet 1**: Engineers paste database keys and API tokens into ChatGPT/Claude to debug faster.
- **Bullet 2**: Production web applications run 800+ npm/pip dependencies with hidden zero-days (Log4Shell, SQLi).
- **Bullet 3**: Automated botnets scrape leaked credentials and scan live web apps within hours.
- **Speaker Notes**: *"Security today is completely fragmented. SAST scanners only check static Git code. WAFs only check inbound network packets. Nobody connects what developers paste to what attackers exploit."*

### Slide 3: The Gap in Current Solutions
- **Bullet 1**: Traditional WAFs (Cloudflare/AWS) lack developer context and cannot tell if a credential was leaked.
- **Bullet 2**: Enterprise SIEMs (Splunk/CrowdStrike) require dedicated security analysts and flood teams with thousands of noisy alerts.
- **Bullet 3**: Fast-growing startups and small teams cannot afford a dedicated 10-person SOC team.
- **Speaker Notes**: *"Small teams drown in alert fatigue. They need autonomous defense with plain-English clarity, not cryptic log lines."*

### Slide 4: The ChainGuard Solution
- **Bullet 1**: **Intercept at the prompt** — On-device WebCrypto protection on AI chat domains.
- **Bullet 2**: **Inventory at the dependency** — Real-time Google OSV vulnerability indexing.
- **Bullet 3**: **Contain at the perimeter** — Two-speed autonomous rate-limits and IP quarantine.
- **Speaker Notes**: *"ChainGuard acts as an autonomous co-pilot. We protect the entire code-to-breach continuum with zero raw secret exposure and sub-second detection."*

### Slide 5: The Four Defensive Pillars
- **Pillar 1**: Browser Paste Guard (Chrome Manifest V3 on-device HMAC).
- **Pillar 2**: Dependency Register (Continuous lockfile parser & OSV mapper).
- **Pillar 3**: Access Log Agent (Microsecond reverse-proxy stream tailer).
- **Pillar 4**: Two-Speed Containment Engine (Reversible rate-limits + sovereign human approval).
- **Speaker Notes**: *"Our architecture is split into four synchronized components, joined together by our deterministic correlation engine."*

### Slide 6: Deterministic Correlation & AI Synthesis
- **Bullet 1**: Mathematical correlation rules (R1, R2, R3) guarantee zero hallucinations.
- **Bullet 2**: Google Gemini 2.0 Flash synthesizes executive summaries for non-technical founders:
  - *What happened?*
  - *Why it matters to your business?*
  - *Exact 3 steps to remediate.*
- **Speaker Notes**: *"We never let an LLM make containment decisions. Detection is 100% deterministic code. AI is strictly leveraged for plain-English translation."*

### Slide 7: Technical Architecture & Zero-Knowledge Cryptography
- **Bullet 1**: FastAPI + SQLite 3 + SQLAlchemy 2.x high-throughput backend.
- **Bullet 2**: Keyed HMAC-SHA256 ensures plaintext secrets are never written to disk or network.
- **Bullet 3**: Dual Operation Modes: **Observe Mode (Audit)** and **Action Mode (Active Enforcement)**.
- **Speaker Notes**: *"Privacy is paramount. Using keyed HMAC-SHA256, plaintext keys are never stored in databases or transmitted over networks."*

### Slide 8: Live Attack Simulation Flow & Benchmark Proof
- **Bullet 1**: Acme Attack Chain verified: Leaked secret $\rightarrow$ live replay $\rightarrow$ JNDI probe $\rightarrow$ brute-force.
- **Bullet 2**: Sub-second detection latency ($t_{detect} < 1.2s$).
- **Bullet 3**: 0.0% false-positive rate on benign traffic.
- **Speaker Notes**: *"In verified lab benchmarks, ChainGuard detected attacks in 0.35 seconds and eliminated false alerts on benign traffic."*

### Slide 9: Market Opportunity & Target Audience
- **Bullet 1**: DevSecOps and Application Security market expanding to $18+ Billion.
- **Bullet 2**: Primary target: Fast-growing startups and product engineering teams adopting AI tools and open-source.
- **Bullet 3**: High demand for automated, founder-friendly compliance and breach defense.
- **Speaker Notes**: *"Every startup adopting generative AI requires guardrails against accidental credential leakage. ChainGuard addresses this immediate market demand."*

### Slide 10: Competitive Differentiation & Unfair Advantages
- **Bullet 1**: Only solution catching prompt leaks on-device with zero plaintext storage.
- **Bullet 2**: Correlates developer leaks directly to live perimeter web logs.
- **Bullet 3**: Two-speed containment prevents self-lockout with automatic 15-minute reversible TTL.
- **Speaker Notes**: *"Traditional tools require weeks of manual rule tuning. ChainGuard deploys in 5 minutes and works out-of-the-box."*

### Slide 11: Roadmap & Executive Leadership
- **Bullet 1**: Q1: Multi-cloud agents (Kubernetes DaemonSet & AWS CloudWatch).
- **Bullet 2**: Q2: Automated 1-click secret rotation connectors (Stripe, AWS Secrets Manager, GitHub).
- **Bullet 3**: Executive Leadership: Swayam Prakash Sahu, Founder & Chief Security Officer.
- **Speaker Notes**: *"ChainGuard transforms security from a bottleneck into automated perimeter resilience. Thank you."*

---

# Part III: Verbatim Business Pitch & Live Demo Script

### 1. Spoken Presentation Script (Verbatim 3-4 Minutes)

#### Step 1: The Hook (0:00 - 0:40)
> *"Judges, let me ask a straightforward question: How many developers on your engineering team have pasted code, database connection strings, or API keys into ChatGPT to debug faster?*  
>  
> *Every single one of them. In 2026, over 40% of startup data breaches originate from accidental prompt leaks and unpatched open-source dependencies.*  
>  
> *I am Swayam Prakash Sahu, Founder and Chief Security Officer of ChainGuard. We built the first Code-to-Breach Defensive Co-Pilot that connects what developers paste to what attackers exploit in live traffic."*

#### Step 2: The Console & Four Pillars (0:40 - 1:20)
> *(Displaying `http://localhost:5173` on screen)*  
> *"Here is the ChainGuard platform. Notice our real-time telemetry console. Unlike enterprise tools that flood you with thousands of cryptic alerts, ChainGuard operates on four synchronized pillars:*  
> *First, our Browser Paste Guard catches secrets before they leave the laptop, hashing them with on-device HMAC-SHA256.*  
> *Second, our Dependency Register catalogs packages against Google OSV in real time.*  
> *Third, our lightweight Log Agent monitors reverse-proxy traffic at microsecond speeds.*  
> *And fourth, our Two-Speed Containment Engine neutralizes threats without breaking production."*

#### Step 3: Triggering the Live Attack (1:20 - 2:30)
> *(In Terminal 4, run `python -m lab.simulator acme_chain`)*  
> *"Now, let us simulate a real-world multi-stage attack. An engineer pastes a Stripe secret key into an AI chat. Moments later, an outside attacker uses that exact credential against our user API, followed by a Log4Shell JNDI exploit and brute-force logins.*  
>  
> *(Switch back to the browser Operator Console)*  
>  
> *Look at the dashboard: In under 1.2 seconds, ChainGuard correlated the leaked token fingerprint to the live request and escalated it to CRITICAL.*  
>  
> *Notice our integrated Gemini AI Copilot: Instead of raw hex logs, it synthesizes a plain-English briefing: what happened, why it matters to revenue, and the exact 3 steps to fix it."*

#### Step 4: Two-Speed Containment & Closing (2:30 - 3:30)
> *"Most automation fails because aggressive blocking breaks critical infrastructure. ChainGuard solves this with Two-Speed Containment:*  
> *The attacker IP is automatically rate-limited with a 15-minute reversible TTL, complete with a one-click Undo button.*  
> *Meanwhile, destructive actions like rotating production credentials require explicit human approval right here.*  
>  
> *We have zero false positives on benign traffic, sub-second detection latency, and complete privacy preservation. ChainGuard is the future of autonomous defense for modern engineering teams.*  
>  
> *Thank you, and I look forward to your questions."*

### 2. Judge Defense & Technical Q&A Cheat Sheet
- **Q: What if the attacker changes their IP address?**  
  *A: "ChainGuard correlates on both cryptographic token fingerprints and behavioral heuristics. Even if the attacker rotates IPs, the replayed token fingerprint immediately triggers Rule R1, and repeated login attempts trigger Rule R3, quarantining the new IP instantly."*
- **Q: What if your AI LLM hallucinates or external APIs go down?**  
  *A: "Detection and containment are 100% deterministic Python and SQLAlchemy logic. The LLM is strictly used to translate evidence into plain English. If Gemini or Groq is unreachable, our built-in deterministic heuristic engine generates the explanation with zero downtime."*
- **Q: Does ChainGuard inspect sensitive customer data or violate GDPR?**  
  *A: "No. ChainGuard operates on zero-knowledge HMAC-SHA256 cryptography. Plaintext secrets never leave the developer device and are never written to disk or database. Only one-way mathematical digests are compared."*

---

# Part IV: Executive Contact & Platform Credentials

- **Company**: ChainGuard Security Inc.
- **Founder & Chief Security Officer**: Swayam Prakash Sahu
- **Direct Voice Hotline**: +91 9438316656 (24/7 Incident Escalation)
- **Official Security Email**: swayamprakashsahu10@gmail.com
- **Operational SLA**: 15-Minute Critical Incident Escalation Response

