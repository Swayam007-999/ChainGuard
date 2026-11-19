# ChainGuard: 8-Minute Executive Pitch & Live Prototype Demo Script
**Founder & Presenter**: Swayam Prakash Sahu  
**Direct Contact**: +91 9438316656 | swayamprakashsahu10@gmail.com  
**Company Slogan**: *"Your business moves faster. Our security moves faster."*  
**Total Target Time**: 8 Minutes (Strict Timer)

---

## Master Timing Breakdown
| Section | Allocated Time | Cumulative Time | Purpose |
| :--- | :--- | :--- | :--- |
| **Part 1: PPT & Business Pitch** | 2 min 30 sec | 0:00 – 2:30 | Hook judges, define problem, market size, business model |
| **Part 2: Live Prototype Demo** | 4 min 00 sec | 2:30 – 6:30 | Live SBOM scan, attack simulation, AI explanation, containment |
| **Part 3: Autonomous AI & SOC Close** | 1 min 30 sec | 6:30 – 8:00 | Copilot agent, 24/7 SOC escalation, final judge call to action |

---

# Part 1: PPT & Business Idea (0:00 – 2:30)

### [0:00 – 0:30] Slide 1: The Hook & Company Slogan
*(Stand tall, look directly at the judges with confidence)*

> **Spoken Script**:  
> "Good morning, respected judges. Let me start with a question every engineering leader dreads:  
> *How many developers on your team pasted sensitive code, database connection strings, or Stripe API keys into ChatGPT this morning to debug an urgent production bug?*  
> 
> In fast-growing companies, developers move at lightning speed. But speed creates blind spots. At ChainGuard, our mission is simple:  
> **'Your business moves faster. Our security moves faster.'**  
> 
> I am Swayam Prakash Sahu, founder of ChainGuard — the world’s first unified **Code-to-Breach Defensive Co-Pilot** built specifically for agile engineering teams."

---

### [0:30 – 1:15] Slide 2 & 3: The Critical Security Gap
*(Point to the PPT architecture diagram)*

> **Spoken Script**:  
> "Today, security is completely broken because it is fragmented across silos:  
> 1. **Static code scanners (SAST)** only check your GitHub repos, completely blind to what developers paste into browser AI tools.  
> 2. **Web Application Firewalls (WAFs)** inspect network traffic, but have zero context on which internal credentials were just leaked or which package versions your app actually runs.  
> 3. **Enterprise SIEMs** cost \$40,000 a year and require a 10-person SOC team just to filter out thousands of false alarms.  
> 
> The result? When a developer accidentally leaks an API token into an AI prompt, botnets scrape and replay that token against your production servers in less than 4 hours. By the time an engineer wakes up, the database is already breached."

---

### [1:15 – 2:00] Slide 4 & 5: The ChainGuard Defense Engine
*(Highlight the four unified pillars)*

> **Spoken Script**:  
> "ChainGuard closes this gap through a unified 4-pillar defense pipeline:  
> 1. **Browser Paste Guard**: Intercepts developer pastes on AI chat sites and computes on-device HMAC-SHA256 cryptographic fingerprints. Plaintext secrets are never stored or transmitted.  
> 2. **Dependency Register**: Scans project lockfiles against Google OSV to build a live Software Bill of Materials (SBOM) and tag exploit keywords.  
> 3. **Deterministic Correlator**: Links leaked token replays and package exploits directly to live Nginx access logs in less than 4.2 milliseconds.  
> 4. **Two-Speed Autonomous Containment**: Automatically rate-limits hostile IPs with a 15-minute reversible TTL while requiring human approval for destructive actions."

---

### [2:00 – 2:30] Slide 6: Business Model & Market Traction
*(Present the business numbers clearly)*

> **Spoken Script**:  
> "Our market opportunity is massive. There are over 100,000 mid-market B2B startups adopting Generative AI daily that cannot afford an enterprise CrowdStrike or Splunk contract.  
> 
> ChainGuard operates on a high-margin B2B SaaS model:  
> - **Developer Seat Tier**: \$15/developer/month for the Chrome extension & SBOM registry.  
> - **Production Cluster Tier**: \$199/month per cluster with autonomous reverse-proxy containment and Gemini 2.0 forensic intelligence.  
> 
> Now, let me step away from the slides and prove this live in our prototype."

---

# Part 2: Live Prototype Walkthrough & Demo (2:30 – 6:30)

*(Switch screen to browser displaying `http://localhost:5173`)*

```
PRE-DEMO SETUP CHECKLIST:
1. Browser open at http://localhost:5173 (Logged into Operator Console).
2. Terminal 1 open: Backend running (uvicorn app.main:app).
3. Terminal 2 open: Ready in d:\Chain-Guard with command typed:
   python -m lab.simulator acme_chain
4. Test files ready in d:\Chain-Guard\lab:
   - demo_package.json
   - demo_requirements.txt
```

---

### [2:30 – 3:00] Demo Step 1: Constellation Navigation & Zero-Trust Architecture
*(Show the Top Header and Brand)*

> **Spoken Script & Action**:  
> `[HOVER ON HEADER LOGO]`  
> "Judges, welcome to the **ChainGuard Sovereign Operator Console**. The platform is built with a cybermorphic, zero-trust telemetry interface.  
> Notice our top navigation: we provide an instant executive **Constellation** overview, our real-time **Operator Console**, and our third-party **SBOM Register**."

---

### [3:00 – 4:00] Demo Step 2: Third-Party Dependencies (SBOM Scanning)
*(This directly answers what files to scan and how it works!)*

> **Spoken Script & Action**:  
> `[CLICK TAB: DEPENDENCIES]`  
> "First, let's look at the software supply chain. Fast teams import hundreds of open-source packages without knowing what zero-days are hidden inside.  
> 
> `[POINT TO UPLOAD FORM]`  
> Here, an engineering team uploads their application manifest — such as a `package.json` for Node.js or `requirements.txt` for Python.  
> 
> `[CLICK 'Choose File' -> SELECT d:\Chain-Guard\lab\demo_package.json]`  
> `[TYPE Application Label: acme-production]`  
> `[CLICK: 'Scan Against OSV.dev']`  
> 
> `[WAIT 1 SECOND FOR TABLE TO UPDATE]`  
> Look at the screen: ChainGuard instantly ingested the manifest and queried the Google Open Source Vulnerability database.  
> It identified **Lodash 4.17.15** running in production, flagged with **CVE-2019-10744 Prototype Pollution**, and highlighted the fixed patch version: **4.17.21**.  
> 
> Crucially, ChainGuard extracts exploit trigger patterns — like `__proto__` and JNDI LDAP tags — into our SQLite backend so our log correlator knows exactly what exploit traffic looks like."

---

### [4:00 – 4:30] Demo Step 3: Browser Extension (Paste Guard)
*(Explain the on-device privacy guarantee)*

> **Spoken Script & Action**:  
> `[SWITCH TO OPERATOR CONSOLE / POINT TO EXTENSION ICON]`  
> "Now, what happens when an engineer accidentally pastes a secret into an AI tool like ChatGPT?  
> 
> Our Manifest V3 browser extension intercepts the clipboard event directly in memory. Using the WebCrypto API, it computes an **HMAC-SHA256 fingerprint** of the token.  
> **Privacy is absolute**: Plaintext keys, passwords, and prompt text are NEVER sent to our server. Only a 64-character mathematical fingerprint is stored."

---

### [4:30 – 5:30] Demo Step 4: The Live Attack Simulation & Correlation
*(Trigger the live attack in the terminal and watch it hit the dashboard)*

> **Spoken Script & Action**:  
> `[CLICK TAB: OPERATOR CONSOLE]`  
> "Right now, the console shows **All Perimeters Clean • 0 Active Threats**.  
> 
> `[SWITCH TO TERMINAL WINDOW]`  
> I am now going to run our attack simulator against our localhost lab container. This simulator mimics an attacker who acquired that leaked developer token and is now attacking our production endpoints:  
> 
> `[RUN COMMAND: python -m lab.simulator acme_chain]`  
> 
> `[SWITCH BACK TO BROWSER]`  
> Look at Terminal 2:  
> 1. The attacker replays the leaked Stripe key against `/rest/user/whoami`.  
> 2. The attacker sends a Log4j JNDI exploit payload `${jndi:ldap:...}`.  
> 3. The attacker launches an SQL injection probe and brute forces logins.  
> 
> `[CLICK REFRESH IN CONSOLE]`  
> In under 4 milliseconds, our deterministic correlator linked the leaked token fingerprint and the vulnerable package keywords to the live IP: **198.51.100.42**! A **CRITICAL** incident has been created live on the board!"

---

### [5:30 – 6:30] Demo Step 5: Gemini 2.0 Flash Threat Briefing & Containment
*(Click on the newly created incident)*

> **Spoken Script & Action**:  
> `[CLICK ON THE CRITICAL INCIDENT CARD]`  
> "Let's click into the incident modal. Instead of forcing tired on-call engineers to read hundreds of raw hex logs, ChainGuard invokes **Google Gemini 2.0 Flash**.  
> 
> `[POINT TO GEMINI BRIEFING BOX]`  
> Look at this plain-English forensic intelligence:  
> - **Summary**: Identifies that an external IP is replaying the leaked developer key.  
> - **Why it matters**: Explains the exact business risk to the company.  
> - **Remediation**: Gives step-by-step instructions to revoke the key and patch dependencies.  
> 
> `[SCROLL TO TWO-SPEED CONTAINMENT ACTIONS]`  
> Next, observe our **Two-Speed Containment Engine**:  
> - **Speed 1 (Autonomous)**: Rate-limits attacker IP `198.51.100.42` for 15 minutes. It has a built-in TTL and a one-click **Revert** button so no customer is ever accidentally locked out.  
> - **Speed 2 (Human Approval)**: High-impact actions — like isolating the database or rotating live API secrets — require a human operator's explicit one-click authorization."

---

# Part 3: Autonomous AI & SOC Close (6:30 – 8:00)

### [6:30 – 7:15] Demo Step 6: The Autonomous AI Copilot
*(Open the floating AI Copilot in bottom-right)*

> **Spoken Script & Action**:  
> `[CLICK BOTTOM-RIGHT 'AI COPILOT' BUTTON]`  
> "Finally, let's inspect the **ChainGuard AI Copilot**, powered by Gemini 2.0 Flash.  
> If an operator is unsure what to do, they can simply type:  
> 
> `[TYPE: 'What happened to our server and what should I do?']`  
> `[PRESS ENTER]`  
> 
> The Sovereign Copilot acts as a virtual Tier-3 Security Analyst. It inspects platform state, explains the exact incident timeline, clarifies the differences between **Observe Mode** and **Action Mode**, and guides the operator through containment."

---

### [7:15 – 8:00] Closing: 24/7 SOC Escalation & Final Judge Pitch
*(Open the SOC Helpline and conclude)*

> **Spoken Script & Action**:  
> `[CLICK '24/7 SOC INCIDENT ESCALATION']`  
> "If a critical zero-day strikes, operators have direct one-click escalation to our SOC response desk with guaranteed 15-minute response times.  
> 
> `[CLOSE MODAL, TURN AND ADDRESS JUDGES DIRECTLY]`  
> Judges, to summarize:  
> While traditional security tools monitor code in storage or packets on the wire, **ChainGuard is the only platform that connects developer keystrokes in AI prompts directly to live perimeter defense**.  
> 
> We make defensive security automatic, privacy-first, and lightning fast.  
> 
> **'Your business moves faster. Our security moves faster.'**  
> 
> Thank you, and I am now ready for your questions."

---

## Technical Q&A Cheat Sheet (For Judges' Tough Questions)

| Question | Winning Answer |
| :--- | :--- |
| **"Doesn't storing leaked tokens pose a security risk?"** | *"Zero risk. We NEVER store plaintext secrets. The browser extension hashes the token on the client's machine using `crypto.subtle.digest` with an HMAC key. The backend only sees a 64-character SHA-256 fingerprint. Even if our database was breached, the attacker gets zero readable credentials."* |
| **"What if the LLM hallucinates an answer?"** | *"Our containment engine is 100% deterministic code (Rule R1, R2, R3). The LLM is strictly used for read-only explanation and translation. The LLM has zero direct tool access to block IPs or drop tables, preventing prompt injection attacks."* |
| **"What if an automated rate-limit blocks our CEO or customer?"** | *"We enforce Rule 7: RFC 1918 private subnets and localhost are hardware-locked and impossible to block. Furthermore, all rate-limits have a 15-minute auto-expiry TTL and a 1-click 'Undo Revert' button in the operator UI."* |
| **"How is this different from Snyk or GitHub Dependabot?"** | *"Dependabot only alerts you on GitHub that a package is old. It has no idea if someone is actively hitting your production server right now. ChainGuard correlates that vulnerable package to live Nginx access logs and neutralizes the attacker in real time."* |
