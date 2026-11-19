# ChainGuard: Official 7-Minute Pitch Deck Script (Slides 1–13)
**Event**: Innovathon 2026 // NIT Rourkela  
**Team**: Last Minute Coders (SUIIT, Burla)  
**Lead Presenter**: Swayam Prakash Sahu (Founder & Chief Security Officer)  
**Team Members**: Swayam Prakash Sahu, Bhupen Biswal, Satya Prakash Mohanty, Samir Kumar Seth, Subhransu Mahapatra  
**Company Slogan**: *"Your business moves faster. Our security moves faster."*  
**Direct Contact**: +91 9438316656 | swayamprakashsahu10@gmail.com  
**Console**: `http://localhost:5173` | **API**: `http://127.0.0.1:8000`

---

## Master 7-Minute Timing Architecture (Strict 420 Seconds)

| Slide | Exact Header on Slide | Timing Bracket | Duration | Core Goal |
| :---: | :--- | :---: | :---: | :--- |
| **01** | **ChainGuard — Code-to-Breach Defensive Co-Pilot** | 0:00 – 0:30 | 30s | Hook judges, introduce slogan & team credentials |
| **02** | **The Problem Is a Connected Chain** | 0:30 – 1:05 | 35s | Expose the 4-stage breach progression & 94-day exposure |
| **03** | **Why Now: The 2026 Threat Convergence** | 1:05 – 1:40 | 35s | Regulatory urgency (DPDP ₹250 Cr cap) & shadow AI spike |
| **04** | **Validated With Engineering Teams** | 1:40 – 2:15 | 35s | Prove founder problem-market fit (78.9% leak data, 100% WTP) |
| **05** | **Why Existing Security Tools Fail** | 2:15 – 2:50 | 35s | Demolish SIEM, WAF, & SCA silos with differentiation matrix |
| **06** | **Four Synchronized Defensive Pillars** | 2:50 – 3:20 | 30s | Explain the 4 modules + Observe vs. Action mode |
| **07** | **Zero-Plaintext Cryptographic Core** | 3:20 – 3:50 | 30s | Prove zero-knowledge HMAC-SHA256 privacy & SQLite schema |
| **08** | **Deterministic Rules & AI Synthesis** | 3:50 – 4:20 | 30s | Rules R1-R3 zero hallucination + 4-tier AI fallback |
| **09** | **Live Demo: Acme Attack Simulation** | 4:20 – 5:35 | 75s | Live prototype execution: terminal attack $\rightarrow$ incident $\rightarrow$ Gemini |
| **10** | **Verified Sub-Second Lab Benchmarks** | 5:35 – 6:00 | 25s | Defend engineering rigor: 0.35s detection, 0% FP, 55/55 tests |
| **11** | **Market Opportunity & SaaS Model** | 6:00 – 6:30 | 30s | Deliver the core business pitch: ₹4.0 Cr beachhead ARR & 3 tiers |
| **12** | **Audit-Ready Standards Alignment** | 6:30 – 6:45 | 15s | Compliance proof: DPDP 2025, OWASP Top 10, NIST CSF |
| **13** | **Autonomous Perimeter Resilience** | 6:45 – 7:00 | 15s | Final call to action, roadmap (K8s), slogan close |

---

# Word-for-Word Slide Script (Slides 1 to 13)

---

### Slide 1: Title & Vision (0:00 – 0:30 | 30 Seconds)
**Slide Header**: `CODE-TO-BREACH DEFENSIVE CO-PILOT — CHAINGUARD`  
**Subtext**: *"Your business moves faster. Our security moves faster."*  
**Key Visuals on Slide**: Emerald/cyan hexagonal CG emblem, 0.35s Detection, 0.0% False Alerts, 15m Auto-TTL.

> **Spoken Script**:  
> *"Good morning, respected judges. I am Swayam Prakash Sahu, presenting alongside Team Last Minute Coders from SUIIT, Burla.*  
> 
> *In 2026, every fast-growing engineering team is racing to build at record speed. But speed creates devastating blind spots. Developers paste secrets into AI chatbots to debug faster, while applications import hundreds of open-source packages containing unpatched zero-days.*  
> 
> *At ChainGuard, we believe small engineering teams shouldn't have to choose between developer velocity and enterprise security. Our philosophy is simple:*  
> **'Your business moves faster. Our security moves faster.'**  
> *ChainGuard is the world's first unified, sub-second defensive security co-pilot designed specifically for agile engineering teams."*

---

### Slide 2: The Problem Is a Connected Chain (0:30 – 1:05 | 35 Seconds)
**Slide Header**: `01 // THE ANATOMY OF A SMALL-TEAM BREACH — The Problem Is a Connected Chain`  
**Key Visuals on Slide**: 4-stage pipeline (Human Prompt Leak $\rightarrow$ Supply-Chain Flaw $\rightarrow$ Live API Exploit $\rightarrow$ Fatal Delay). Callout: *"94 Days Median Secret Exposure (DBIR)"*.

> **Spoken Script**:  
> *"Here is how modern breaches actually happen. It is never an isolated event — it is an interconnected chain:*  
> 
> *On **Day 0**, an engineer debugs an urgent bug and pastes a live Stripe or database token into an AI chat.*  
> *On **Day 2**, a vulnerable npm or pip package slips into the production build.*  
> *By **Day 6**, automated botnets discover that leaked key and replay it against production endpoints while launching exploit payloads.*  
> *And by **Stage 4**, the company enters the fatal delay: according to IBM and Verizon, the average Indian breach lifecycle lasts **263 days**, with a median secret exposure of **94 days**.*  
> 
> *Traditional tools only look at one point in time. **ChainGuard joins all four signals on Day 0 in under 1.2 seconds**."*

---

### Slide 3: Why Now: The 2026 Threat Convergence (1:05 – 1:40 | 35 Seconds)
**Slide Header**: `02 // VERIZON DBIR 2026 & IBM INDIA 2025 EVIDENCE — Why Now: The 2026 Threat Convergence`  
**Key Visuals on Slide**: Progress bars (58% Shadow AI, 48% Supply Chain, 45% AI usage, 31% Vulnerability Exploitation). Bottom banner: DPDP penalty up to ₹250 Crore.

> **Spoken Script**:  
> *"Why is this problem exploding right now in 2026? Look at the hard macro data:*  
> 
> *- **58% of Indian organizations** have zero formal shadow-AI policy.*  
> *- **48% of all breaches** now involve third-party software supply chains — up from 30%.*  
> *- Regular employee AI usage has surged **threefold to 45%**.*  
> *- For the first time in 19 years of Verizon DBIR history, **vulnerability exploitation is the #1 entry point for attackers**.*  
> 
> *And the stakes have fundamentally changed: under India's **DPDP Rules 2025**, statutory penalties reach up to **₹250 Crore**, with full enforcement mandated by May 2027. For a startup or SME, a single un-contained prompt leak is now an existential company-killing event."*

---

### Slide 4: Validated With Engineering Teams (1:40 – 2:15 | 35 Seconds)
**Slide Header**: `03 // PRIMARY 16-QUESTION PRACTITIONER SURVEY — Validated With Engineering Teams`  
**Key Visuals on Slide**: 78.9% Paste into AI, 70.6% Broke Production, 47.4% Need 1+ Week, 100% Willing to Pay. Founder quote.

> **Spoken Script**:  
> *"We didn't just guess these problems — we validated them across engineering teams in a rigorous 16-question practitioner survey:*  
> 
> *- **78.9% of developers** admitted to pasting internal code or API keys into AI chats.*  
> *- **70.6%** had firewalls accidentally break live production by blocking real paying customers.*  
> *- **47.4%** require more than a full week to even notice active API probing.*  
> *- And **100% of respondents** stated they are actively willing to pay monthly for an automated defensive solution.*  
> 
> *As one surveyed founder told us: 'Current tools dump raw hex logs or CVE numbers on me without explaining in plain English if I am actually in danger or how to fix it.' ChainGuard solves this exact pain point."*

---

### Slide 5: Why Existing Security Tools Fail (2:15 – 2:50 | 35 Seconds)
**Slide Header**: `04 // COMPETITIVE DIFFERENTIATION MATRIX — Why Existing Security Tools Fail`  
**Key Visuals on Slide**: Matrix comparing Enterprise SIEM, Edge WAF, Point SCA, and ChainGuard across 5 dimensions.

> **Spoken Script**:  
> *"When you look at existing solutions, the market is completely broken:*  
> 
> *- **Enterprise SIEMs** cost tens of lakhs, require dedicated security analysts, and dump thousands of raw, cryptic logs.*  
> *- **Edge WAFs** like Cloudflare only inspect inbound packets. They have zero visibility into developer prompt leaks, and when they block, they cause blunt production outages.*  
> *- **Point SCA tools** like Snyk only scan Git repositories at rest, completely blind to live traffic.*  
> 
> *Only **ChainGuard** delivers zero-plaintext prompt guarding via on-device HMAC, links live OSV packages directly to HTTP traffic, translates attacks into sub-1.8s plain-English briefs, and enforces a reversible two-speed response with a 15-minute auto-expiry TTL."*

---

### Slide 6: Four Synchronized Defensive Pillars (2:50 – 3:20 | 30 Seconds)
**Slide Header**: `05 // UNIFIED CODE-TO-BREACH ARCHITECTURE — Four Synchronized Defensive Pillars`  
**Key Visuals on Slide**: 4 Cards (Browser Paste Guard, Dependency Register, Access Log Agent, Two-Speed Engine) + Dual Operation Modes banner.

> **Spoken Script**:  
> *"Our technical architecture synchronizes four lightweight modules:*  
> 
> *1. **Browser Paste Guard**: Chrome Manifest V3 extension intercepting clipboard pastes on AI domains.*  
> *2. **Dependency Register**: Continuous SBOM parser mapping packages against Google OSV.*  
> *3. **Access Log Agent**: A microsecond reverse-proxy stream tailer running under 45MB of RAM.*  
> *4. **Two-Speed Containment Engine**: Automatically imposing reversible 15-minute rate limits on hostile IPs.*  
> 
> *We offer two operational modes: **Observe Mode** for zero-risk auditing, and **Action Mode** for autonomous edge enforcement."*

---

### Slide 7: Zero-Plaintext Cryptographic Core (3:20 – 3:50 | 30 Seconds)
**Slide Header**: `06 // ZERO-KNOWLEDGE SECURITY & PERSISTENT STATE — Zero-Plaintext Cryptographic Core`  
**Key Visuals on Slide**: Left box: `Digest = HMAC_SHA256 KeySecret`, 4 security properties. Right box: 7 SQLite relational tables.

> **Spoken Script**:  
> *"Privacy is our core architectural moat. ChainGuard operates on a strict zero-knowledge security model.*  
> 
> *Plaintext keys and developer prompt texts **never leave browser memory**. The extension computes an on-device HMAC-SHA256 fingerprint. The server only ever sees a 64-character mathematical digest.*  
> 
> *Our backend verifies digests using constant-time comparison to prevent timing attacks, while our database persists state across 7 strictly parameterized SQLite relational tables — complete with hardware-level CIDR lockouts that make it mathematically impossible to block localhost or internal private subnets."*

---

### Slide 8: Deterministic Rules & AI Synthesis (3:50 – 4:20 | 30 Seconds)
**Slide Header**: `07 // ZERO-HALLUCINATION DETECTION ENGINE — Deterministic Rules & AI Synthesis`  
**Key Visuals on Slide**: Rule R1 (Token Replay), Rule R2 (OSV Matching), Rule R3 (Brute-Force). 4-Tier Fallback: Groq $\rightarrow$ OpenRouter $\rightarrow$ Gemini 2.0 $\rightarrow$ Local Template.

> **Spoken Script**:  
> *"Crucially, we enforce a strict separation between containment decisions and AI synthesis.*  
> 
> *Attack detection is **100% deterministic code**: Rule R1 matches leaked token hashes, Rule R2 matches vulnerable OSV package exploit paths, and Rule R3 detects brute-force bursts. This guarantees **zero LLM hallucinations**.*  
> 
> *We leverage LLMs strictly for read-only explanation. Through our 4-tier fallback — Groq, OpenRouter, Google Gemini 2.0 Flash, down to local templates — ChainGuard guarantees 100% uptime with zero crashes even during network outages."*

---

### Slide 9: Live Demo: Acme Attack Simulation (4:20 – 5:35 | 75 Seconds)
**Slide Header**: `08 // DEDICATED 2-MINUTE LIVE PRODUCT WALKTHROUGH — Live Demo: Acme Attack Simulation`  
**Action**: Switch screen to `http://localhost:5173` and Terminal.

> **Spoken Script & Live Action**:  
> `[SHOW DASHBOARD: http://localhost:5173]`  
> *"Let me show you this live in our running prototype.*  
> 
> `[STEP 1: CLICK DEPENDENCIES TAB]`  
> *First, in our Third-Party Register, we scan a production `demo_package.json`. OSV flags **Lodash 4.17.15** with CVE-2019-10744 and loads exploit patterns.*  
> 
> `[STEP 2: SWITCH TO TERMINAL & RUN: python -m lab.simulator acme_chain]`  
> *Now, in Terminal 2, I trigger our attack simulator against our lab container. The simulator simulates an engineer leaking a Stripe key, an external attacker replaying that exact key, injecting a Log4j JNDI string, and launching 12 failed logins.*  
> 
> `[STEP 3: SWITCH TO CONSOLE & CLICK REFRESH]`  
> *In under **0.35 seconds**, our correlator links the leaked token fingerprint and package keywords to IP `198.51.100.42`! A **CRITICAL** incident appears.*  
> 
> `[STEP 4: CLICK INCIDENT MODAL]`  
> *Gemini 2.0 Flash instantly synthesizes the attack in plain English: what happened, why it matters, and exact remediation steps.*  
> *Notice our Two-Speed defense: the attacker IP is throttled with a 15-minute reversible TTL, while high-impact secret rotation requires a human operator's one-click approval!"*

---

### Slide 10: Verified Sub-Second Lab Benchmarks (5:35 – 6:00 | 25 Seconds)
**Slide Header**: `09 // PDD SECTION 7.3 VERIFIED PERFORMANCE DATA — Verified Sub-Second Lab Benchmarks`  
**Key Visuals on Slide**: Benchmark table: 0.35s incident creation, 0.48s AI brief, 0/25 (0.0%) false positives, <45MB RAM. Bottom badges: 55/55 tests passing, 0 warnings.

> **Spoken Script**:  
> *"Every claim on this screen is backed by verified engineering benchmarks from our Product Design Document:*  
> 
> *- **Time to Incident Creation**: 0.35 to 1.20 seconds — well beating the 5-second industry target.*  
> *- **Time to Plain-English Brief**: 0.48 to 1.80 seconds.*  
> *- **False Positive Rate**: Exactly **0.0%** across 25 benign traffic runs.*  
> *- **Memory Footprint**: Under 45MB RAM.*  
> *- And our production codebase passes all **55 unit tests** with zero linter warnings and a 1.95-second bundle build."*

---

### Slide 11: Market Opportunity & SaaS Model (6:00 – 6:30 | 30 Seconds)
**Slide Header**: `10 // $18B+ GLOBAL DEVSECOPS & INDIA STARTUP BEACHHEAD — Market Opportunity & SaaS Model`  
**Key Visuals on Slide**: Left: 1% India Beachhead ARR: ₹4.0 Cr. Right: 3 Tiers (Tier 01 Free, Tier 02 Pro ₹1,500–₹3,000/mo, Tier 03 Agency Plan).

> **Spoken Script**:  
> *"Now let's examine the commercial business model. We are addressing a global \$18+ Billion DevSecOps market with a laser-focused beachhead in India:*  
> 
> *Capturing just **1% of India's 2.23 Lakh DPIIT-recognized tech startups** (2,230 companies) at our ₹1,500/month tier yields **₹4.0 Crore in Annual Recurring Revenue (ARR)**.*  
> 
> *Our monetization follows a proven Product-Led Growth model:*  
> *- **Tier 1 (Free)**: Browser paste guard and local lockfile scanner for individual developers.*  
> *- **Tier 2 (Pro - ₹1,500 to ₹3,000/month)**: Live reverse-proxy log correlator, two-speed containment, and Gemini briefings.*  
> *- **Tier 3 (Agency / Enterprise)**: Multi-client tenant console with automated DPDP compliance audit reports."*

---

### Slide 12: Audit-Ready Standards Alignment (6:30 – 6:45 | 15 Seconds)
**Slide Header**: `11 // GLOBAL REGULATORY & FRAMEWORK MAPPING — Audit-Ready Standards Alignment`  
**Key Visuals on Slide**: OWASP Top 10: 2025, NIST CSF 2.0, DPDP Rules 2025, OWASP LLM Top 10 Compliant.

> **Spoken Script**:  
> *"ChainGuard is built audit-ready from day one. We map directly to **OWASP Top 10: 2025** supply chain controls, all six governance functions of **NIST CSF 2.0**, and generate tamper-proof timeline logs required for **India's DPDP Rules 2025** — ensuring startups achieve compliance in minutes without expensive external consultants."*

---

### Slide 13: Autonomous Perimeter Resilience (6:45 – 7:00 | 15 Seconds)
**Slide Header**: `Q1: KUBERNETES DAEMONSET // Q2: 1-CLICK STRIPE ROTATION — Autonomous Perimeter Resilience`  
**Key Visuals on Slide**: Founder Swayam Prakash Sahu, 24/7 Hotline +91 9438316656, Email, Full Team names (Swayam, Bhupen, Satya, Samir, Subhransu).

> **Spoken Script**:  
> *"In conclusion: engineering teams should never have to sacrifice speed to stay safe. ChainGuard deploys in 5 minutes, eliminates false alerts, and connects prompt leaks directly to live edge defense.*  
> 
> *We are Team Last Minute Coders, and our commitment is absolute:*  
> **'Your business moves faster. Our security moves faster.'**  
> *Thank you, and we welcome your questions!"*

---

## 30-Second Technical Q&A Defense (Cheat Sheet for Judges)

| Judge's Question | Winning Verbatim Answer |
| :--- | :--- |
| **"What if an employee uses private browsing or pastes on mobile?"** | *"Our Browser Paste Guard covers developer workstations where code is debugged. But even if a secret leaks on an unmonitored device, our Dependency Register and Log Correlator still catch the inbound exploit payload and brute-force replay at the reverse proxy."* |
| **"Why ₹1,500–₹3,000 per month? Isn't that too cheap?"** | *"That is our beachhead entry price for seed-stage startups, validated by our survey where 36.8% selected this exact bracket. As their request volume and clusters grow, our Tier 3 and Agency pricing scales to ₹15,000–₹50,000/month."* |
| **"How do you prevent blocking legitimate customers who make typos?"** | *"Rule R3 requires a burst threshold of 10+ failed requests within 60 seconds from an unauthenticated IP. Even then, the rate-limit is temporary (15-minute TTL), never an indefinite block, and has a one-click manual revert button."* |
