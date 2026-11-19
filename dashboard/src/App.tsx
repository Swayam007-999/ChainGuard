import React, { useState, useEffect, useRef } from "react";
import { Incident, Dependency, AllowlistEntry } from "./types";

interface ChatMessage {
  id: string;
  sender: "user" | "copilot";
  text: string;
  actionTaken?: string;
  timestamp: string;
}

// Interactive Celestial Constellation Starfield Canvas
function ConstellationCanvas() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animationFrameId: number;
    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    const handleResize = () => {
      if (!canvas) return;
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    };
    window.addEventListener("resize", handleResize);

    // Mouse coordinates with smooth easing
    const mouse = { x: -1000, y: -1000, radius: 180 };
    const handleMouseMove = (e: MouseEvent) => {
      mouse.x = e.clientX;
      mouse.y = e.clientY;
    };
    const handleMouseLeave = () => {
      mouse.x = -1000;
      mouse.y = -1000;
    };
    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseleave", handleMouseLeave);

    // Generate celestial stars
    const starCount = Math.min(110, Math.floor((width * height) / 14000));
    const stars: {
      x: number;
      y: number;
      vx: number;
      vy: number;
      radius: number;
      alpha: number;
      baseAlpha: number;
      twinkleSpeed: number;
    }[] = [];

    for (let i = 0; i < starCount; i++) {
      const baseAlpha = Math.random() * 0.6 + 0.2;
      stars.push({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.35,
        vy: (Math.random() - 0.5) * 0.35,
        radius: Math.random() * 1.8 + 0.6,
        alpha: baseAlpha,
        baseAlpha: baseAlpha,
        twinkleSpeed: Math.random() * 0.02 + 0.005,
      });
    }

    // Render loop
    const render = () => {
      ctx.clearRect(0, 0, width, height);

      // 1. Update and draw stars
      for (let i = 0; i < stars.length; i++) {
        const s = stars[i];
        s.x += s.vx;
        s.y += s.vy;

        // Wrap edges gracefully
        if (s.x < 0) s.x = width;
        if (s.x > width) s.x = 0;
        if (s.y < 0) s.y = height;
        if (s.y > height) s.y = 0;

        // Twinkle effect
        s.alpha = s.baseAlpha + Math.sin(Date.now() * s.twinkleSpeed) * 0.25;

        // Draw star particle
        ctx.beginPath();
        ctx.arc(s.x, s.y, s.radius, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(224, 242, 254, ${Math.max(0.1, s.alpha)})`;
        ctx.shadowBlur = s.radius > 1.4 ? 12 : 4;
        ctx.shadowColor = "rgba(56, 189, 248, 0.8)";
        ctx.fill();

        // 2. Connect stars within proximity (Constellation Web)
        for (let j = i + 1; j < stars.length; j++) {
          const s2 = stars[j];
          const dx = s.x - s2.x;
          const dy = s.y - s2.y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < 120) {
            const lineAlpha = (1 - dist / 120) * 0.22;
            ctx.beginPath();
            ctx.moveTo(s.x, s.y);
            ctx.lineTo(s2.x, s2.y);
            ctx.strokeStyle = `rgba(56, 189, 248, ${lineAlpha})`;
            ctx.lineWidth = 0.6;
            ctx.shadowBlur = 0;
            ctx.stroke();
          }
        }

        // 3. Connect stars to user's cursor (Interactive Maserati Constellation Effect)
        const mdx = s.x - mouse.x;
        const mdy = s.y - mouse.y;
        const mdist = Math.sqrt(mdx * mdx + mdy * mdy);

        if (mdist < mouse.radius) {
          const mAlpha = (1 - mdist / mouse.radius) * 0.45;
          ctx.beginPath();
          ctx.moveTo(s.x, s.y);
          ctx.lineTo(mouse.x, mouse.y);
          ctx.strokeStyle = `rgba(186, 230, 253, ${mAlpha})`;
          ctx.lineWidth = 0.8;
          ctx.shadowBlur = 8;
          ctx.shadowColor = "rgba(14, 165, 233, 0.6)";
          ctx.stroke();
        }
      }

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener("resize", handleResize);
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseleave", handleMouseLeave);
    };
  }, []);

  return <canvas ref={canvasRef} className="fixed inset-0 pointer-events-none z-0 opacity-80" />;
}

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(true);
  const [password, setPassword] = useState<string>("");
  const [activeTab, setActiveTab] = useState<"overview" | "incidents" | "dependencies" | "settings">("overview");
  const [containmentMode, setContainmentMode] = useState<"observe" | "action">("observe");

  // State
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);
  const [dependencies, setDependencies] = useState<Dependency[]>([]);
  const [allowlist, setAllowlist] = useState<AllowlistEntry[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Forms
  const [newCidr, setNewCidr] = useState<string>("");
  const [newCidrNote, setNewCidrNote] = useState<string>("");
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadAppName, setUploadAppName] = useState<string>("acme-production");
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);

  // Modals & Panels
  const [isHelplineOpen, setIsHelplineOpen] = useState<boolean>(false);
  const [isCopilotOpen, setIsCopilotOpen] = useState<boolean>(false);
  const [confirmDialog, setConfirmDialog] = useState<{
    isOpen: boolean;
    title: string;
    message: string;
    onConfirm: () => void;
  }>({ isOpen: false, title: "", message: "", onConfirm: () => {} });

  // Agentic AI Copilot Chat State
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      id: "init-1",
      sender: "copilot",
      text: "Greetings Operator. I am the ChainGuard Autonomous Security Copilot. I analyze your live telemetry, correlate leaked secret fingerprints across generative AI chats, and orchestrate two-speed perimeter containment. Ask me to explain any aspect of the constellation or issue commands like 'Switch to Action mode', 'Analyze live threats', or 'Check dependencies'.",
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    },
  ]);
  const [chatInput, setChatInput] = useState<string>("");
  const [isTyping, setIsTyping] = useState<boolean>(false);
  const chatBottomRef = useRef<HTMLDivElement>(null);

  // Polling for incidents every 3 seconds
  useEffect(() => {
    if (!isAuthenticated) return;

    fetchIncidents();
    const interval = setInterval(() => {
      fetchIncidents(true);
    }, 3000);

    return () => clearInterval(interval);
  }, [isAuthenticated]);

  // Load dependencies and allowlist on tab change
  useEffect(() => {
    if (!isAuthenticated) return;
    if (activeTab === "dependencies") fetchDependencies();
    if (activeTab === "settings") fetchAllowlist();
  }, [activeTab, isAuthenticated]);

  // Auto scroll chat
  useEffect(() => {
    if (isCopilotOpen) {
      chatBottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [chatMessages, isCopilotOpen]);

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password }),
      });
      if (res.ok) {
        setIsAuthenticated(true);
        fetchIncidents();
      } else {
        setError("Invalid credentials. Please verify your administrative key.");
      }
    } catch {
      setError("Failed to establish secure session with ChainGuard cluster on port 8000.");
    } finally {
      setLoading(false);
    }
  }

  async function fetchIncidents(silent: boolean = false) {
    if (!silent) setLoading(true);
    try {
      const res = await fetch("/v1/incidents");
      if (res.status === 401) {
        setIsAuthenticated(false);
        return;
      }
      if (res.ok) {
        const data = await res.json();
        setIncidents(data);
        if (selectedIncident) {
          const updated = data.find((i: Incident) => i.id === selectedIncident.id);
          if (updated) setSelectedIncident(updated);
        }
      }
    } catch {
      if (!silent) setError("Could not retrieve telemetry from correlator engine.");
    } finally {
      if (!silent) setLoading(false);
    }
  }

  async function fetchDependencies() {
    setLoading(true);
    try {
      const res = await fetch("/v1/dependencies");
      if (res.ok) setDependencies(await res.json());
    } catch {
      setError("Could not load dependency register.");
    } finally {
      setLoading(false);
    }
  }

  async function fetchAllowlist() {
    setLoading(true);
    try {
      const res = await fetch("/v1/allowlist");
      if (res.ok) setAllowlist(await res.json());
    } catch {
      setError("Could not load network allowlist.");
    } finally {
      setLoading(false);
    }
  }

  async function handleActionApprove(actionId: number) {
    try {
      const res = await fetch(`/v1/actions/${actionId}/approve`, { method: "POST" });
      if (res.ok) fetchIncidents();
    } catch {
      alert("Failed to approve containment action.");
    }
  }

  async function handleActionUndo(actionId: number) {
    try {
      const res = await fetch(`/v1/actions/${actionId}/undo`, { method: "POST" });
      if (res.ok) fetchIncidents();
    } catch {
      alert("Failed to revert action.");
    }
  }

  async function handleUploadManifest(e: React.FormEvent) {
    e.preventDefault();
    if (!uploadFile) return;
    setUploadStatus("Querying Google OSV database & deriving exploit keywords...");
    const formData = new FormData();
    formData.append("file", uploadFile);
    formData.append("app_name", uploadAppName);

    try {
      const res = await fetch("/v1/dependencies/scan", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (res.ok) {
        setUploadStatus(`Index Complete: ${data.dependencies_tracked} runtime packages mapped, ${data.vulnerabilities_detected} CVEs cataloged.`);
        fetchDependencies();
      } else {
        setUploadStatus(`Error: ${data.detail || "Manifest parsing failed"}`);
      }
    } catch {
      setUploadStatus("Failed to upload manifest.");
    }
  }

  async function handleAddAllowlist(e: React.FormEvent) {
    e.preventDefault();
    if (!newCidr || !newCidrNote) return;
    try {
      const res = await fetch("/v1/allowlist", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ cidr: newCidr, note: newCidrNote }),
      });
      if (res.ok) {
        setNewCidr("");
        setNewCidrNote("");
        fetchAllowlist();
      } else {
        const err = await res.json();
        alert(err.detail || "Failed to add allowlist CIDR.");
      }
    } catch {
      alert("Network error.");
    }
  }

  // Autonomous Agentic AI Command & Chat Handler
  function handleSendMessage(textToSend?: string) {
    const query = (textToSend || chatInput).trim();
    if (!query) return;

    const userMsg: ChatMessage = {
      id: `u-${Date.now()}`,
      sender: "user",
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setChatMessages((prev) => [...prev, userMsg]);
    setChatInput("");
    setIsTyping(true);

    setTimeout(() => {
      const lower = query.toLowerCase();
      let responseText = "";
      let actionTaken: string | undefined = undefined;

      if (lower.includes("action") || lower.includes("enforce") || lower.includes("active mode")) {
        setContainmentMode("action");
        actionTaken = "Policy Mode ➔ ACTION (Enforce)";
        responseText = "⚡ Containment policy elevated to **ACTION MODE** (Active Enforcement). The engine will now autonomously enforce reversible rate-limiting on offending IPs with a 15-minute TTL, while holding credential rotations for human approval.";
      } else if (lower.includes("observe") || lower.includes("dry run") || lower.includes("audit mode")) {
        setContainmentMode("observe");
        actionTaken = "Policy Mode ➔ OBSERVE (Audit)";
        responseText = "👁️ Containment policy switched to **OBSERVE MODE** (Audit / Dry-Run). Telemetry correlation and incident synthesis will continue active logging, but automated firewall blocking is disarmed.";
      } else if (lower.includes("dependenc") || lower.includes("package") || lower.includes("cve") || lower.includes("osv") || lower.includes("scan")) {
        setActiveTab("dependencies");
        actionTaken = "Navigation ➔ Dependencies Register";
        responseText = "📦 Navigated to the **Third-Party Dependency Register**. Here you can upload `package.json`, `package-lock.json`, or `requirements.txt`. ChainGuard maps dependencies against Google's OSV database to detect vulnerable versions and tags packages with exploit keywords (`jndi`, `sqli`, `traversal`). Try uploading `lab/demo_package.json`!";
      } else if (lower.includes("incident") || lower.includes("threat") || lower.includes("attack") || lower.includes("console")) {
        setActiveTab("incidents");
        actionTaken = "Navigation ➔ Operator Console";
        if (incidents.length > 0) {
          const top = incidents[0];
          responseText = `🚨 Navigated to the **Operator Console**. You currently have **${incidents.length} active incident(s)**. Priority Threat: **${top.title}** (Severity: ${top.severity}). ${top.explanation?.summary || ""}`;
        } else {
          responseText = "🛡️ Navigated to the **Operator Console**. All endpoints are currently clean with 0 active incidents. You can trigger an attack simulation anytime by running `python -m lab.simulator acme_chain` in Terminal 4.";
        }
      } else if (lower.includes("setting") || lower.includes("allowlist") || lower.includes("cidr") || lower.includes("config")) {
        setActiveTab("settings");
        actionTaken = "Navigation ➔ Settings & Allowlist";
        responseText = "⚙️ Navigated to **Settings & Allowlist**. Here you can toggle between Observe and Action modes, inspect sliding-window rate limiters, and whitelist safe IP ranges (like your office VPN or monitoring clusters) so automated defense never locks out employees.";
      } else if (lower.includes("contact") || lower.includes("help") || lower.includes("phone") || lower.includes("email") || lower.includes("soc") || lower.includes("swayam")) {
        setIsHelplineOpen(true);
        actionTaken = "Modal ➔ SOC Helpline Displayed";
        responseText = "📞 Opening the **24/7 Incident Response Hotline**:\n\n• **Founder & Chief Security Officer**: Swayam Prakash Sahu\n• **Direct Hotline**: +91 9438316656\n• **Emergency Email**: swayamprakashsahu10@gmail.com\n\nOur specialized security operations desk guarantees a 15-minute response SLA on confirmed production breach signals.";
      } else if (lower.includes("overview") || lower.includes("landing") || lower.includes("constellation") || lower.includes("home")) {
        setActiveTab("overview");
        actionTaken = "Navigation ➔ Constellation Overview";
        responseText = "🌌 Navigated to the **Constellation Overview**. Explore the four defensive stars of ChainGuard: Browser Paste Guard, Dependency Register, Access Log Agent, and Two-Speed Containment.";
      } else {
        responseText = `I analyzed your query: "${query}". I am ready to guide you across ChainGuard:\n• "Switch to Action mode" (enforce containment)\n• "Switch to Observe mode" (audit dry-run)\n• "Take me to Dependencies"\n• "Open Operator Console"\n• "Contact emergency SOC helpline"`;
      }

      const copilotMsg: ChatMessage = {
        id: `c-${Date.now()}`,
        sender: "copilot",
        text: responseText,
        actionTaken,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };

      setChatMessages((prev) => [...prev, copilotMsg]);
      setIsTyping(false);
    }, 600);
  }

  function getSeverityBadge(sev: string) {
    switch (sev) {
      case "CRITICAL":
        return (
          <span className="bg-rose-950/80 text-rose-300 border border-rose-500/60 font-mono font-bold px-3 py-1 rounded-full text-[10px] tracking-widest shadow-[0_0_15px_rgba(244,63,94,0.4)] animate-pulse">
            CRITICAL
          </span>
        );
      case "HIGH":
        return (
          <span className="bg-amber-950/80 text-amber-300 border border-amber-500/60 font-mono font-bold px-3 py-1 rounded-full text-[10px] tracking-widest shadow-[0_0_15px_rgba(245,158,11,0.3)]">
            HIGH
          </span>
        );
      case "MEDIUM":
        return (
          <span className="bg-yellow-950/80 text-yellow-300 border border-yellow-500/50 font-mono font-semibold px-2.5 py-0.5 rounded-full text-[10px] tracking-wider">
            MEDIUM
          </span>
        );
      default:
        return (
          <span className="bg-sky-950/80 text-sky-300 border border-sky-500/40 font-mono px-2.5 py-0.5 rounded-full text-[10px] tracking-wider">
            LOW
          </span>
        );
    }
  }

  // ===================== CINEMATIC LOGIN CONSOLE =====================
  if (!isAuthenticated) {
    return (
      <div className="relative flex items-center justify-center min-h-screen space-bg p-6 overflow-hidden select-none">
        <ConstellationCanvas />

        <div className="relative z-10 celestial-card w-full max-w-lg p-10 rounded-2xl border border-white/10 shadow-[0_0_80px_rgba(0,0,0,0.85)]">
          <div className="text-center mb-8 pb-6 border-b border-white/10">
            <img
              src="/logo.png"
              alt="ChainGuard Logo"
              className="w-24 h-24 mx-auto mb-4 rounded-2xl object-contain drop-shadow-[0_0_35px_rgba(56,189,248,0.6)]"
            />
            <h1 className="font-cinzel text-2xl font-bold tracking-[0.25em] text-white uppercase">
              ChainGuard
            </h1>
            <p className="font-space text-xs tracking-[0.14em] text-cyan-400 uppercase mt-2">
              Your business moves faster. Our security moves faster.
            </p>
          </div>

          {error && (
            <div className="bg-rose-950/60 border border-rose-500/50 text-rose-300 text-xs p-3.5 rounded-xl mb-6 font-space flex items-center gap-2.5">
              <span>⚠️</span>
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-6">
            <div>
              <label className="block font-space text-[11px] uppercase tracking-[0.2em] text-slate-400 mb-2">
                Operator Sovereign Key
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter administrative credentials"
                className="w-full bg-[#050814]/90 border border-white/15 rounded-xl p-3.5 text-white text-sm focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 focus:outline-none transition font-space"
                required
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full btn-constellation font-cinzel font-semibold py-4 rounded-xl text-xs transition duration-300 disabled:opacity-50 flex items-center justify-center gap-3 tracking-[0.22em]"
            >
              {loading ? (
                <span>INITIALIZING STELLAR HANDSHAKE...</span>
              ) : (
                <>
                  <span>ENTER THE DEFENSIVE REALM</span>
                  <span>➔</span>
                </>
              )}
            </button>
          </form>

          <div className="mt-8 pt-6 border-t border-white/10 flex items-center justify-between text-[11px] font-space text-slate-500 tracking-wider">
            <span>CHAINGUARD SECURITY INC.</span>
            <span>FOUNDER: SWAYAM PRAKASH SAHU</span>
          </div>
        </div>
      </div>
    );
  }

  // ===================== CELESTIAL BRANDED PLATFORM =====================
  return (
    <div className="min-h-screen space-bg text-slate-200 flex flex-col selection:bg-cyan-500 selection:text-slate-950 relative">
      <ConstellationCanvas />

      {/* Luxury Cinematic Header (Maserati Celestial Style) */}
      <header className="relative z-40 bg-[#03050c]/85 backdrop-blur-xl border-b border-white/10 px-8 py-4 sticky top-0 transition-all duration-300 shadow-[0_10px_35px_rgba(0,0,0,0.6)]">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-6">
          {/* ChainGuard Official Emblem & Slogan */}
          <div
            onClick={() => setActiveTab("overview")}
            className="flex items-center gap-4 cursor-pointer group"
          >
            <img
              src="/logo.png"
              alt="ChainGuard Logo"
              className="w-11 h-11 rounded-xl object-contain drop-shadow-[0_0_20px_rgba(56,189,248,0.5)] group-hover:scale-105 transition duration-300"
            />
            <div>
              <h1 className="font-cinzel text-lg font-bold tracking-[0.25em] text-white uppercase group-hover:text-cyan-300 transition duration-300">
                ChainGuard
              </h1>
              <p className="font-space text-[9.5px] tracking-[0.12em] text-cyan-400/90 uppercase">
                Your business moves faster. Our security moves faster.
              </p>
            </div>
          </div>

          {/* Celestial Luxury Navigation Tabs */}
          <nav className="flex items-center gap-1 bg-[#060a16]/80 p-1.5 rounded-full border border-white/10 text-xs font-space tracking-wider">
            <button
              onClick={() => setActiveTab("overview")}
              className={`px-5 py-2 rounded-full transition duration-300 ${
                activeTab === "overview"
                  ? "bg-white text-slate-950 font-bold shadow-[0_0_20px_rgba(255,255,255,0.4)]"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              CONSTELLATION
            </button>
            <button
              onClick={() => setActiveTab("incidents")}
              className={`px-5 py-2 rounded-full transition duration-300 flex items-center gap-2 ${
                activeTab === "incidents"
                  ? "bg-white text-slate-950 font-bold shadow-[0_0_20px_rgba(255,255,255,0.4)]"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              <span>OPERATOR CONSOLE</span>
              {incidents.length > 0 && (
                <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${activeTab === "incidents" ? "bg-slate-950 text-cyan-300" : "bg-rose-950 text-rose-300 border border-rose-800"}`}>
                  {incidents.length}
                </span>
              )}
            </button>
            <button
              onClick={() => setActiveTab("dependencies")}
              className={`px-5 py-2 rounded-full transition duration-300 ${
                activeTab === "dependencies"
                  ? "bg-white text-slate-950 font-bold shadow-[0_0_20px_rgba(255,255,255,0.4)]"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              DEPENDENCIES
            </button>
            <button
              onClick={() => setActiveTab("settings")}
              className={`px-5 py-2 rounded-full transition duration-300 ${
                activeTab === "settings"
                  ? "bg-white text-slate-950 font-bold shadow-[0_0_20px_rgba(255,255,255,0.4)]"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              SETTINGS
            </button>
          </nav>

          {/* Right Controls: Mode Switcher & SOC Hotline */}
          <div className="flex items-center gap-3">
            {/* Interactive Mode Switcher */}
            <div
              onClick={() => setContainmentMode((m) => (m === "observe" ? "action" : "observe"))}
              className="celestial-card cursor-pointer px-4 py-2 rounded-full flex items-center gap-2.5 transition border hover:scale-105 select-none font-space text-[11px] tracking-wider"
              title="Toggle containment enforcement policy"
            >
              <span className={`w-2 h-2 rounded-full ${containmentMode === "action" ? "bg-emerald-400 shadow-[0_0_12px_#10b981] animate-pulse" : "bg-cyan-400 shadow-[0_0_10px_#06b6d4]"}`} />
              <span className="text-slate-400">POLICY:</span>
              <strong className={containmentMode === "action" ? "text-emerald-400 font-bold" : "text-cyan-300 font-bold"}>
                {containmentMode === "action" ? "ACTION (ENFORCE)" : "OBSERVE (AUDIT)"}
              </strong>
            </div>

            {/* SOC Hotline Button */}
            <button
              onClick={() => setIsHelplineOpen(true)}
              className="celestial-card hover:border-rose-500/50 text-rose-300 px-4 py-2 rounded-full text-xs font-space tracking-wider flex items-center gap-2 transition shadow-[0_0_15px_rgba(244,63,94,0.15)]"
            >
              <span className="animate-pulse">🚨</span>
              <span>24/7 SOC</span>
            </button>

            {/* Logout */}
            <button
              onClick={() => setIsAuthenticated(false)}
              className="font-space text-xs text-slate-400 hover:text-white px-3 py-1.5 transition tracking-wider"
            >
              EXIT
            </button>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <div className="relative z-10 flex-1 flex flex-col">
        {/* ========================================================================= */}
        {/* VIEW 1: THE CELESTIAL LANDING PAGE (MASERATI TRIDENT CONSTELLATION STYLE) */}
        {/* ========================================================================= */}
        {activeTab === "overview" && (
          <div className="flex-1 flex flex-col">
            {/* Hero Constellation Canvas Section */}
            <section className="relative min-h-[85vh] flex flex-col items-center justify-center text-center px-6 py-20 overflow-hidden">
              <div className="max-w-4xl mx-auto space-y-6">
                <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-cyan-950/40 border border-cyan-400/30 text-cyan-300 font-space text-[11px] tracking-[0.25em] uppercase shadow-[0_0_20px_rgba(56,189,248,0.2)]">
                  <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping" />
                  <span>Your business moves faster. Our security moves faster.</span>
                </div>

                <h1 className="font-cinzel text-4xl sm:text-6xl md:text-7xl font-bold tracking-[0.18em] text-white uppercase leading-tight drop-shadow-[0_10px_35px_rgba(0,0,0,0.8)]">
                  The Constellation <br />
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-200 via-sky-400 to-indigo-300">
                    Of Code Defense
                  </span>
                </h1>

                <p className="font-sans text-sm sm:text-base md:text-lg text-slate-300/90 max-w-2xl mx-auto leading-relaxed font-light tracking-wide">
                  An uncompromising defensive security system unifying developer prompt leak prevention, runtime software bill of materials, and autonomous two-speed perimeter containment.
                </p>

                {/* Maserati Luxury Action Deck */}
                <div className="pt-6 flex flex-wrap items-center justify-center gap-5 font-space">
                  <button
                    onClick={() => setActiveTab("incidents")}
                    className="btn-constellation-cyan px-8 py-4 rounded-full font-bold text-xs tracking-[0.22em] shadow-[0_0_35px_rgba(56,189,248,0.35)]"
                  >
                    ENTER OPERATOR CONSOLE ➔
                  </button>

                  <button
                    onClick={() => {
                      const el = document.getElementById("pillars");
                      el?.scrollIntoView({ behavior: "smooth" });
                    }}
                    className="btn-constellation px-8 py-4 rounded-full font-medium text-xs tracking-[0.22em]"
                  >
                    DISCOVER CONSTELLATION ↓
                  </button>
                </div>
              </div>

              {/* Bottom Celestial Telemetry Strip */}
              <div className="w-full max-w-6xl mx-auto mt-20 pt-8 border-t border-white/10 grid grid-cols-2 md:grid-cols-4 gap-6 text-left font-space text-xs">
                <div>
                  <span className="text-[10px] tracking-[0.2em] text-slate-500 uppercase block mb-1">
                    01 // PRIVACY STANDARD
                  </span>
                  <p className="font-bold text-white tracking-wider">Zero-Plaintext HMAC-SHA256</p>
                </div>
                <div>
                  <span className="text-[10px] tracking-[0.2em] text-slate-500 uppercase block mb-1">
                    02 // CONTAINMENT SPEED
                  </span>
                  <p className="font-bold text-emerald-400 tracking-wider">Two-Speed • 15m Reversible TTL</p>
                </div>
                <div>
                  <span className="text-[10px] tracking-[0.2em] text-slate-500 uppercase block mb-1">
                    03 // LATENCY OVERHEAD
                  </span>
                  <p className="font-bold text-cyan-300 tracking-wider">&lt; 4.2ms High-Velocity Stream</p>
                </div>
                <div>
                  <span className="text-[10px] tracking-[0.2em] text-slate-500 uppercase block mb-1">
                    04 // LEAD ARCHITECT
                  </span>
                  <p className="font-bold text-white tracking-wider">Swayam Prakash Sahu</p>
                </div>
              </div>
            </section>

            {/* Section 2: The Four Defensive Constellations (Interactive Luxury Pillars) */}
            <section id="pillars" className="py-24 px-8 max-w-7xl mx-auto w-full">
              <div className="text-center mb-16 space-y-3">
                <span className="font-space text-xs tracking-[0.3em] text-cyan-400 uppercase">
                  Four Stars in Alignment
                </span>
                <h2 className="font-cinzel text-3xl sm:text-4xl font-bold tracking-[0.18em] text-white uppercase">
                  The Four Pillars of Defense
                </h2>
                <div className="w-24 h-0.5 bg-gradient-to-r from-transparent via-cyan-400 to-transparent mx-auto mt-4" />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Pillar 1 */}
                <div className="celestial-card p-8 rounded-3xl relative group overflow-hidden">
                  <div className="absolute top-0 right-0 p-8 text-4xl text-cyan-500/20 font-cinzel font-bold">
                    I
                  </div>
                  <div className="w-12 h-12 rounded-2xl bg-cyan-950/60 border border-cyan-400/40 flex items-center justify-center text-xl mb-6 shadow-[0_0_20px_rgba(56,189,248,0.25)]">
                    🛡️
                  </div>
                  <span className="font-space text-[10px] tracking-[0.25em] text-cyan-400 uppercase block mb-2">
                    STAR I // ZERO-KNOWLEDGE PROMPT DEFENSE
                  </span>
                  <h3 className="font-cinzel text-xl font-bold text-white tracking-wider mb-3">
                    Browser Paste Guard
                  </h3>
                  <p className="font-sans text-xs sm:text-sm text-slate-300/80 leading-relaxed font-light mb-6">
                    Runs on-device via Chrome Manifest V3 and WebCrypto. When an engineer pastes AWS, Stripe, or database secrets into ChatGPT or Claude, the extension intercepts the paste and computes an irreversible HMAC fingerprint. The plaintext secret never touches disk or network.
                  </p>
                  <div className="font-space text-[11px] text-slate-400 pt-4 border-t border-white/5 flex items-center justify-between">
                    <span>ENGINE: WebCrypto API</span>
                    <span className="text-emerald-400">ZERO RAW LEAKS</span>
                  </div>
                </div>

                {/* Pillar 2 */}
                <div className="celestial-card p-8 rounded-3xl relative group overflow-hidden">
                  <div className="absolute top-0 right-0 p-8 text-4xl text-cyan-500/20 font-cinzel font-bold">
                    II
                  </div>
                  <div className="w-12 h-12 rounded-2xl bg-indigo-950/60 border border-indigo-400/40 flex items-center justify-center text-xl mb-6 shadow-[0_0_20px_rgba(99,102,241,0.25)]">
                    📦
                  </div>
                  <span className="font-space text-[10px] tracking-[0.25em] text-cyan-400 uppercase block mb-2">
                    STAR II // RUNTIME SUPPLY CHAIN RECON
                  </span>
                  <h3 className="font-cinzel text-xl font-bold text-white tracking-wider mb-3">
                    Dependency Register
                  </h3>
                  <p className="font-sans text-xs sm:text-sm text-slate-300/80 leading-relaxed font-light mb-6">
                    Maps your live application dependencies against Google’s OSV vulnerability catalog in real time. It parses lockfiles and derives exploit signatures (such as Log4Shell JNDI patterns and SQL injection keywords) to provide situational awareness before attacks strike.
                  </p>
                  <div className="font-space text-[11px] text-slate-400 pt-4 border-t border-white/5 flex items-center justify-between">
                    <span>INDEX: Google OSV Database</span>
                    <span className="text-cyan-400">ACTIVE CVE MAPPING</span>
                  </div>
                </div>

                {/* Pillar 3 */}
                <div className="celestial-card p-8 rounded-3xl relative group overflow-hidden">
                  <div className="absolute top-0 right-0 p-8 text-4xl text-cyan-500/20 font-cinzel font-bold">
                    III
                  </div>
                  <div className="w-12 h-12 rounded-2xl bg-sky-950/60 border border-sky-400/40 flex items-center justify-center text-xl mb-6 shadow-[0_0_20px_rgba(14,165,233,0.25)]">
                    ⚡
                  </div>
                  <span className="font-space text-[10px] tracking-[0.25em] text-cyan-400 uppercase block mb-2">
                    STAR III // DEEP PACKET TELEMETRY
                  </span>
                  <h3 className="font-cinzel text-xl font-bold text-white tracking-wider mb-3">
                    Access Log Agent
                  </h3>
                  <p className="font-sans text-xs sm:text-sm text-slate-300/80 leading-relaxed font-light mb-6">
                    A lightweight Python stream daemon that tails perimeter reverse-proxy access logs. It strips hostile injection payloads, hashes authorization headers on-the-fly, and delivers batch event streams to the backend within microseconds.
                  </p>
                  <div className="font-space text-[11px] text-slate-400 pt-4 border-t border-white/5 flex items-center justify-between">
                    <span>THROUGHPUT: &lt; 4.2ms OVERHEAD</span>
                    <span className="text-emerald-400">STREAMING ACTIVE</span>
                  </div>
                </div>

                {/* Pillar 4 */}
                <div className="celestial-card p-8 rounded-3xl relative group overflow-hidden">
                  <div className="absolute top-0 right-0 p-8 text-4xl text-cyan-500/20 font-cinzel font-bold">
                    IV
                  </div>
                  <div className="w-12 h-12 rounded-2xl bg-rose-950/60 border border-rose-400/40 flex items-center justify-center text-xl mb-6 shadow-[0_0_20px_rgba(244,63,94,0.25)]">
                    🛡️
                  </div>
                  <span className="font-space text-[10px] tracking-[0.25em] text-cyan-400 uppercase block mb-2">
                    STAR IV // TWO-SPEED CONTAINMENT ENGINE
                  </span>
                  <h3 className="font-cinzel text-xl font-bold text-white tracking-wider mb-3">
                    Correlation & Quarantine
                  </h3>
                  <p className="font-sans text-xs sm:text-sm text-slate-300/80 leading-relaxed font-light mb-6">
                    Combines deterministic correlation rules (R1 leaked secrets, R2 exploitable dependencies, R3 brute force) with Gemini 2.0 Flash plain-English synthesis. Automatically enforces reversible rate-limits with a 15-minute TTL, while requiring human authorization for credential rotation.
                  </p>
                  <div className="font-space text-[11px] text-slate-400 pt-4 border-t border-white/5 flex items-center justify-between">
                    <span>LOGIC: Two-Speed Policy</span>
                    <span className="text-amber-400">HUMAN-IN-THE-LOOP</span>
                  </div>
                </div>
              </div>
            </section>

            {/* Section 3: Executive Founder & Incident Escalation SLA */}
            <section className="py-16 px-8 max-w-5xl mx-auto w-full mb-16">
              <div className="celestial-card p-10 rounded-3xl border-white/10 text-center relative overflow-hidden">
                <span className="font-space text-[11px] tracking-[0.25em] text-cyan-400 uppercase block mb-2">
                  Executive Security Leadership
                </span>
                <h3 className="font-cinzel text-2xl sm:text-3xl font-bold text-white tracking-[0.15em] uppercase mb-4">
                  Swayam Prakash Sahu
                </h3>
                <p className="font-sans text-sm text-slate-300 max-w-xl mx-auto leading-relaxed font-light mb-8">
                  Founder & Chief Security Officer. Available 24/7 for high-severity credential leak containment and production perimeter incident response.
                </p>

                <div className="flex flex-wrap items-center justify-center gap-4 font-space text-xs">
                  <a
                    href="tel:+919438316656"
                    className="btn-constellation-cyan px-6 py-3 rounded-full font-bold tracking-wider"
                  >
                    📞 +91 9438316656
                  </a>
                  <a
                    href="mailto:swayamprakashsahu10@gmail.com"
                    className="btn-constellation px-6 py-3 rounded-full font-medium tracking-wider"
                  >
                    ✉️ swayamprakashsahu10@gmail.com
                  </a>
                </div>
              </div>
            </section>
          </div>
        )}

        {/* ========================================================================= */}
        {/* VIEW 2: OPERATOR CONSOLE (LIVE THREAT STREAM)                             */}
        {/* ========================================================================= */}
        {activeTab === "incidents" && (
          <main className="max-w-7xl mx-auto p-8 w-full space-y-8">
            <div className="flex flex-wrap items-center justify-between gap-4 pb-6 border-b border-white/10">
              <div>
                <span className="font-space text-[11px] tracking-[0.25em] text-cyan-400 uppercase block">
                  Perimeter Telemetry HUD
                </span>
                <h2 className="font-cinzel text-2xl font-bold text-white tracking-[0.15em] uppercase mt-1">
                  Live Threat Correlation Stream
                </h2>
              </div>
              <div className="flex items-center gap-3 font-space text-xs">
                <button
                  onClick={() => handleSendMessage("Explain active incidents")}
                  className="btn-constellation-cyan px-5 py-2.5 rounded-full font-bold"
                >
                  🤖 Copilot Analysis
                </button>
                <button
                  onClick={() => fetchIncidents()}
                  className="celestial-card px-5 py-2.5 rounded-full text-slate-300 hover:text-white"
                >
                  ↻ Refresh
                </button>
              </div>
            </div>

            {incidents.length === 0 ? (
              <div className="celestial-card rounded-3xl p-16 text-center">
                <img
                  src="/logo.png"
                  alt="ChainGuard"
                  className="w-20 h-20 mx-auto mb-4 object-contain drop-shadow-[0_0_30px_rgba(56,189,248,0.5)]"
                />
                <h3 className="font-cinzel text-xl font-bold text-white tracking-widest uppercase mb-2">
                  All Perimeters Clean • 0 Active Threats
                </h3>
                <p className="font-sans text-xs text-slate-400 max-w-lg mx-auto leading-relaxed mb-6 font-light">
                  No anomalous token replays or exploit payloads observed. Run the attack simulator in Terminal 4 to trigger live correlation in front of observers:
                </p>
                <div className="inline-block bg-[#050814] border border-white/10 px-5 py-3 rounded-2xl font-space text-xs text-cyan-300">
                  <span className="text-slate-500">$ </span>python -m lab.simulator acme_chain
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                {incidents.map((inc) => (
                  <div
                    key={inc.id}
                    onClick={() => setSelectedIncident(inc)}
                    className="celestial-card rounded-2xl p-6 cursor-pointer group border-white/10 hover:border-cyan-400/50"
                  >
                    <div className="flex flex-wrap items-center justify-between gap-4 mb-3">
                      <div className="flex items-center gap-3">
                        {getSeverityBadge(inc.severity)}
                        <span className="font-space text-xs text-slate-400">
                          {new Date(inc.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
                        </span>
                        <span className="font-space text-[10px] uppercase px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                          {inc.status}
                        </span>
                      </div>
                      <span className="font-space text-xs text-cyan-400 group-hover:translate-x-1 transition duration-200">
                        View Forensic Timeline ➔
                      </span>
                    </div>

                    <h3 className="font-cinzel text-lg font-bold text-white tracking-wide mb-2">{inc.title}</h3>
                    <p className="font-sans text-xs text-slate-300 leading-relaxed line-clamp-2 bg-[#050814]/70 p-4 rounded-xl border border-white/5 font-light">
                      {inc.explanation?.summary || "Analyzing telemetry signatures..."}
                    </p>

                    {inc.actions && inc.actions.length > 0 && (
                      <div className="mt-4 pt-4 border-t border-white/10 flex flex-wrap items-center justify-between gap-2 font-space text-xs">
                        <div className="flex items-center gap-2">
                          <span className="text-slate-400">Two-Speed Containment:</span>
                          {inc.actions.map((act) => (
                            <span
                              key={act.id}
                              className={`px-3 py-1 rounded-full border ${
                                act.status === "applied"
                                  ? "bg-emerald-950 text-emerald-300 border-emerald-700"
                                  : act.status === "pending"
                                  ? "bg-amber-950 text-amber-300 border-amber-700 animate-pulse"
                                  : "bg-slate-800 text-slate-400 border-slate-700"
                              }`}
                            >
                              {act.type} [{act.status.toUpperCase()}]
                            </span>
                          ))}
                        </div>
                        <span className="text-slate-500 text-[11px]">Click card for details</span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </main>
        )}

        {/* ========================================================================= */}
        {/* VIEW 3: DEPENDENCY REGISTER                                               */}
        {/* ========================================================================= */}
        {activeTab === "dependencies" && (
          <main className="max-w-7xl mx-auto p-8 w-full space-y-8">
            <div className="flex flex-wrap items-center justify-between gap-4 pb-6 border-b border-white/10">
              <div>
                <span className="font-space text-[11px] tracking-[0.25em] text-cyan-400 uppercase block">
                  Software Bill of Materials (SBOM)
                </span>
                <h2 className="font-cinzel text-2xl font-bold text-white tracking-[0.15em] uppercase mt-1">
                  Third-Party Dependency Register
                </h2>
              </div>
            </div>

            {/* Upload Card */}
            <div className="celestial-card rounded-3xl p-8 border-white/10">
              <h3 className="font-cinzel text-base font-bold text-white tracking-wider mb-2">
                Scan Manifest / Lockfile
              </h3>
              <p className="font-sans text-xs text-slate-400 font-light mb-6">
                Ingest runtime dependencies into the local register. Automatically queried against Google OSV with exploit pattern tagging.
              </p>
              <form onSubmit={handleUploadManifest} className="flex flex-wrap items-center gap-4">
                <input
                  type="text"
                  value={uploadAppName}
                  onChange={(e) => setUploadAppName(e.target.value)}
                  placeholder="Application Label"
                  className="bg-[#050814] border border-white/15 rounded-xl px-4 py-2.5 text-xs text-slate-200 font-space focus:border-cyan-400 focus:outline-none"
                />
                <input
                  type="file"
                  accept=".json,.txt"
                  onChange={(e) => setUploadFile(e.target.files ? e.target.files[0] : null)}
                  className="text-xs text-slate-400 file:mr-4 file:py-2.5 file:px-5 file:rounded-xl file:border-0 file:text-xs file:font-space file:font-bold file:bg-cyan-500 file:text-slate-950 hover:file:bg-cyan-400 cursor-pointer"
                />
                <button
                  type="submit"
                  disabled={!uploadFile}
                  className="btn-constellation-cyan px-6 py-2.5 rounded-xl text-xs font-bold disabled:opacity-40"
                >
                  Scan Against OSV.dev
                </button>
              </form>
              {uploadStatus && (
                <div className="mt-4 font-space text-xs bg-[#050814] p-3.5 rounded-xl border border-white/10 text-cyan-300">
                  {uploadStatus}
                </div>
              )}
            </div>

            {/* Table */}
            <div className="celestial-card rounded-3xl overflow-hidden border-white/10 shadow-2xl">
              <table className="w-full text-left text-xs font-space">
                <thead className="bg-[#050814] text-slate-400 border-b border-white/10 uppercase tracking-wider">
                  <tr>
                    <th className="py-4 px-6">Package Name</th>
                    <th className="py-4 px-6">Ecosystem</th>
                    <th className="py-4 px-6">Version</th>
                    <th className="py-4 px-6">Security Advisory & CVEs</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {dependencies.length === 0 ? (
                    <tr>
                      <td colSpan={4} className="py-16 text-center text-slate-500 font-sans font-light">
                        No dependencies registered yet. Upload package.json or requirements.txt above.
                      </td>
                    </tr>
                  ) : (
                    dependencies.map((dep) => {
                      const isVulnerable = dep.vulns && dep.vulns.length > 0;
                      return (
                        <tr
                          key={dep.id}
                          className={isVulnerable ? "bg-rose-950/20 hover:bg-rose-950/30" : "hover:bg-slate-800/20"}
                        >
                          <td className="py-4 px-6 font-bold text-white">{dep.name}</td>
                          <td className="py-4 px-6 uppercase text-slate-400">{dep.ecosystem}</td>
                          <td className="py-4 px-6 text-cyan-300">{dep.version}</td>
                          <td className="py-4 px-6">
                            {isVulnerable ? (
                              <div className="space-y-1.5">
                                {dep.vulns.map((v) => (
                                  <div key={v.id} className="flex flex-wrap items-center gap-2">
                                    <span className="bg-rose-950 text-rose-300 border border-rose-800 px-2 py-0.5 rounded text-[11px] font-bold">
                                      {v.osv_id}
                                    </span>
                                    <span className="text-slate-300 text-[11px] font-sans">{v.summary}</span>
                                    {v.fixed_in && (
                                      <span className="text-emerald-400 text-[11px] bg-emerald-950/60 border border-emerald-800 px-2 py-0.5 rounded">
                                        Fixed in: {v.fixed_in}
                                      </span>
                                    )}
                                  </div>
                                ))}
                              </div>
                            ) : (
                              <span className="text-emerald-400 font-medium flex items-center gap-1.5">
                                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" /> Clean (No CVEs detected)
                              </span>
                            )}
                          </td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>
          </main>
        )}

        {/* ========================================================================= */}
        {/* VIEW 4: SETTINGS & ALLOWLIST                                              */}
        {/* ========================================================================= */}
        {activeTab === "settings" && (
          <main className="max-w-7xl mx-auto p-8 w-full space-y-8">
            <div className="flex flex-wrap items-center justify-between gap-4 pb-6 border-b border-white/10">
              <div>
                <span className="font-space text-[11px] tracking-[0.25em] text-cyan-400 uppercase block">
                  Configuration Matrix
                </span>
                <h2 className="font-cinzel text-2xl font-bold text-white tracking-[0.15em] uppercase mt-1">
                  Engine & Containment Settings
                </h2>
              </div>
            </div>

            {/* Mode selection cards */}
            <div className="celestial-card rounded-3xl p-8 border-white/10">
              <h3 className="font-cinzel text-base font-bold text-white tracking-wider mb-2">
                Containment Policy Enforcement Mode
              </h3>
              <p className="font-sans text-xs text-slate-400 font-light mb-6">
                Define the sovereign response mode when correlated exploit chains are detected in live requests:
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div
                  onClick={() => setContainmentMode("observe")}
                  className={`p-6 rounded-2xl border cursor-pointer transition duration-300 ${
                    containmentMode === "observe"
                      ? "celestial-card-active border-cyan-400 shadow-[0_0_30px_rgba(56,189,248,0.25)]"
                      : "celestial-card hover:border-white/20"
                  }`}
                >
                  <div className="flex items-center justify-between mb-3 font-space">
                    <span className="font-bold text-white text-sm">OBSERVE MODE (AUDIT)</span>
                    {containmentMode === "observe" && (
                      <span className="text-[10px] bg-cyan-400 text-slate-950 font-bold px-2 py-0.5 rounded-full">ACTIVE</span>
                    )}
                  </div>
                  <p className="font-sans text-xs text-slate-300 leading-relaxed font-light">
                    Correlates attacks and generates Gemini briefings. Proposes mitigation actions for human review without automated network blocks.
                  </p>
                </div>

                <div
                  onClick={() => setContainmentMode("action")}
                  className={`p-6 rounded-2xl border cursor-pointer transition duration-300 ${
                    containmentMode === "action"
                      ? "celestial-card-active border-emerald-400 shadow-[0_0_30px_rgba(16,185,129,0.25)]"
                      : "celestial-card hover:border-white/20"
                  }`}
                >
                  <div className="flex items-center justify-between mb-3 font-space">
                    <span className="font-bold text-emerald-400 text-sm">ACTION MODE (ENFORCE)</span>
                    {containmentMode === "action" && (
                      <span className="text-[10px] bg-emerald-400 text-slate-950 font-bold px-2 py-0.5 rounded-full">ACTIVE</span>
                    )}
                  </div>
                  <p className="font-sans text-xs text-slate-300 leading-relaxed font-light">
                    Autonomous two-speed containment. Imposes reversible 15-minute rate-limits on attacker IPs while requiring one-click confirmation for secret rotation.
                  </p>
                </div>
              </div>
            </div>

            {/* SOC Desk Box */}
            <div className="celestial-card rounded-3xl p-8 border-rose-500/30 bg-gradient-to-r from-rose-950/20 via-[#060a16] to-[#080e22]">
              <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
                <div>
                  <span className="font-space text-[10px] tracking-[0.25em] text-rose-400 uppercase block">
                    High-Priority Response Desk
                  </span>
                  <h3 className="font-cinzel text-xl font-bold text-white tracking-wider mt-1">
                    24/7 SOC Incident Escalation
                  </h3>
                  <p className="font-sans text-xs text-slate-400 font-light mt-1">
                    Founder & Chief Security Officer: Swayam Prakash Sahu
                  </p>
                </div>
                <span className="font-space text-[11px] bg-rose-950 text-rose-300 border border-rose-700 px-4 py-1.5 rounded-full">
                  15-Minute Critical SLA
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 font-space text-xs">
                <div className="bg-[#050814]/80 p-5 rounded-2xl border border-white/10 flex items-center justify-between">
                  <div>
                    <span className="text-slate-500 text-[10px] uppercase block">Direct Voice Hotline</span>
                    <a href="tel:+919438316656" className="text-base font-bold text-cyan-300 hover:underline">
                      +91 9438316656
                    </a>
                  </div>
                  <a href="tel:+919438316656" className="btn-constellation-cyan px-4 py-2 rounded-xl font-bold">
                    Call Now
                  </a>
                </div>

                <div className="bg-[#050814]/80 p-5 rounded-2xl border border-white/10 flex items-center justify-between">
                  <div>
                    <span className="text-slate-500 text-[10px] uppercase block">Official Escalation Email</span>
                    <a href="mailto:swayamprakashsahu10@gmail.com" className="text-xs font-bold text-cyan-300 hover:underline block break-all">
                      swayamprakashsahu10@gmail.com
                    </a>
                  </div>
                  <a href="mailto:swayamprakashsahu10@gmail.com" className="btn-constellation-cyan px-4 py-2 rounded-xl font-bold">
                    Email
                  </a>
                </div>
              </div>
            </div>

            {/* Add CIDR Form */}
            <div className="celestial-card rounded-3xl p-8 border-white/10">
              <h3 className="font-cinzel text-base font-bold text-white tracking-wider mb-2">
                Whitelist Protected Subnet CIDR
              </h3>
              <p className="font-sans text-xs text-slate-400 font-light mb-6">
                Specified ranges are excluded from automated rate-limiting, preventing denial-of-service locks on internal infrastructure.
              </p>
              <form onSubmit={handleAddAllowlist} className="flex flex-wrap gap-4">
                <input
                  type="text"
                  placeholder="CIDR (e.g. 198.51.100.0/24)"
                  value={newCidr}
                  onChange={(e) => setNewCidr(e.target.value)}
                  className="bg-[#050814] border border-white/15 rounded-xl px-4 py-2.5 text-xs text-slate-200 font-space focus:border-cyan-400 focus:outline-none"
                  required
                />
                <input
                  type="text"
                  placeholder="Description / Identity"
                  value={newCidrNote}
                  onChange={(e) => setNewCidrNote(e.target.value)}
                  className="bg-[#050814] border border-white/15 rounded-xl px-4 py-2.5 text-xs text-slate-200 flex-1 min-w-[200px] font-space focus:border-cyan-400 focus:outline-none"
                  required
                />
                <button
                  type="submit"
                  className="btn-constellation-cyan px-6 py-2.5 rounded-xl text-xs font-bold"
                >
                  Whitelist Subnet
                </button>
              </form>
            </div>

            {/* Allowlist Table */}
            <div className="celestial-card rounded-3xl overflow-hidden border-white/10 shadow-2xl">
              <table className="w-full text-left text-xs font-space">
                <thead className="bg-[#050814] text-slate-400 border-b border-white/10 uppercase tracking-wider">
                  <tr>
                    <th className="py-4 px-6">Network CIDR</th>
                    <th className="py-4 px-6">Designation</th>
                    <th className="py-4 px-6">Inherent Protection Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  <tr className="bg-slate-900/30">
                    <td className="py-4 px-6 text-cyan-300 font-bold">127.0.0.1/32, ::1/128</td>
                    <td className="py-4 px-6 text-slate-400 font-sans">Localhost loopback interfaces</td>
                    <td className="py-4 px-6 text-emerald-400 font-semibold">🔒 Inherent Hardware Lock (Rule 7)</td>
                  </tr>
                  <tr className="bg-slate-900/30">
                    <td className="py-4 px-6 text-cyan-300 font-bold">10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16</td>
                    <td className="py-4 px-6 text-slate-400 font-sans">RFC 1918 Private networks</td>
                    <td className="py-4 px-6 text-emerald-400 font-semibold">🔒 Inherent Hardware Lock (Rule 7)</td>
                  </tr>
                  {allowlist.map((entry) => (
                    <tr key={entry.id}>
                      <td className="py-4 px-6 text-white font-bold">{entry.cidr}</td>
                      <td className="py-4 px-6 text-slate-300 font-sans">{entry.note}</td>
                      <td className="py-4 px-6 text-cyan-400">Operator Exempt</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </main>
        )}
      </div>

      {/* ===================== FLOATING AUTONOMOUS AI COPILOT ===================== */}
      <div className="fixed bottom-8 right-8 z-50">
        {!isCopilotOpen ? (
          <button
            onClick={() => setIsCopilotOpen(true)}
            className="btn-constellation-cyan px-5 py-3.5 rounded-full flex items-center gap-3 shadow-[0_0_35px_rgba(56,189,248,0.5)] group transition duration-300 hover:scale-105"
          >
            <img
              src="/logo.png"
              alt="Copilot"
              className="w-5 h-5 rounded object-contain group-hover:scale-110 transition duration-300"
            />
            <div className="text-left font-space leading-tight">
              <span className="block text-xs font-bold text-slate-950">AI Copilot</span>
              <span className="block text-[10px] text-slate-900 opacity-80">Autonomous • Online</span>
            </div>
          </button>
        ) : (
          <div className="celestial-card w-[380px] sm:w-[420px] h-[540px] rounded-3xl flex flex-col border border-cyan-400/30 shadow-[0_0_50px_rgba(0,0,0,0.9)] overflow-hidden">
            <div className="bg-[#050814]/90 px-5 py-4 border-b border-white/10 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <img
                  src="/logo.png"
                  alt="ChainGuard"
                  className="w-8 h-8 rounded-xl object-contain drop-shadow-[0_0_15px_rgba(56,189,248,0.4)]"
                />
                <div>
                  <h4 className="font-cinzel text-xs font-bold text-white tracking-wider flex items-center gap-1.5">
                    <span>ChainGuard Copilot</span>
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  </h4>
                  <p className="font-space text-[10px] text-cyan-400">Gemini 2.0 Flash • Sovereign Agent</p>
                </div>
              </div>
              <button
                onClick={() => setIsCopilotOpen(false)}
                className="text-slate-400 hover:text-white p-1 text-sm font-bold"
              >
                ✕
              </button>
            </div>

            <div className="flex-1 p-5 overflow-y-auto space-y-3.5 text-xs font-sans">
              {chatMessages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex flex-col ${msg.sender === "user" ? "items-end" : "items-start"}`}
                >
                  <div
                    className={`max-w-[85%] rounded-2xl p-3.5 leading-relaxed ${
                      msg.sender === "user"
                        ? "bg-cyan-600 text-white rounded-br-none shadow-[0_0_15px_rgba(6,182,212,0.3)]"
                        : "bg-[#050814]/80 text-slate-200 border border-white/10 rounded-bl-none font-light"
                    }`}
                  >
                    <p className="whitespace-pre-line">{msg.text}</p>
                    {msg.actionTaken && (
                      <div className="mt-2 pt-2 border-t border-cyan-400/20 font-space text-[10px] text-cyan-300 font-semibold flex items-center gap-1">
                        <span>⚡ Action:</span>
                        <span>{msg.actionTaken}</span>
                      </div>
                    )}
                  </div>
                  <span className="font-space text-[10px] text-slate-500 mt-1">{msg.timestamp}</span>
                </div>
              ))}
              {isTyping && (
                <div className="flex items-center gap-1.5 font-space text-xs text-cyan-400 p-2.5 bg-[#050814] rounded-xl max-w-[130px] border border-white/10">
                  <span className="animate-bounce">●</span>
                  <span className="animate-bounce delay-100">●</span>
                  <span className="animate-bounce delay-200">●</span>
                  <span className="text-[10px] ml-1">Analyzing...</span>
                </div>
              )}
              <div ref={chatBottomRef} />
            </div>

            <div className="px-4 py-2 bg-[#050814]/90 border-t border-white/10 flex items-center gap-1.5 overflow-x-auto font-space text-[10px] text-slate-300">
              <button
                onClick={() => handleSendMessage("Overview")}
                className="bg-slate-800/80 hover:bg-slate-700 hover:text-cyan-300 px-3 py-1 rounded-full whitespace-nowrap border border-white/10"
              >
                🌌 Constellation
              </button>
              <button
                onClick={() => handleSendMessage("Switch to Action mode")}
                className="bg-slate-800/80 hover:bg-slate-700 hover:text-emerald-300 px-3 py-1 rounded-full whitespace-nowrap border border-white/10"
              >
                ⚡ Action Mode
              </button>
              <button
                onClick={() => handleSendMessage("Check dependencies")}
                className="bg-slate-800/80 hover:bg-slate-700 hover:text-cyan-300 px-3 py-1 rounded-full whitespace-nowrap border border-white/10"
              >
                📦 Dependencies
              </button>
              <button
                onClick={() => handleSendMessage("SOC Helpline")}
                className="bg-slate-800/80 hover:bg-slate-700 hover:text-rose-300 px-3 py-1 rounded-full whitespace-nowrap border border-white/10"
              >
                📞 SOC Desk
              </button>
            </div>

            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSendMessage();
              }}
              className="p-3.5 bg-[#050814] border-t border-white/10 flex items-center gap-2"
            >
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                placeholder="Ask Copilot or command: 'Switch mode'..."
                className="flex-1 bg-[#03050c] border border-white/15 rounded-xl px-4 py-2.5 text-xs text-white placeholder-slate-500 focus:border-cyan-400 focus:outline-none font-space"
              />
              <button
                type="submit"
                className="btn-constellation-cyan px-4 py-2.5 rounded-xl font-bold text-xs"
              >
                Send
              </button>
            </form>
          </div>
        )}
      </div>

      {/* ===================== FORENSIC INCIDENT DETAIL MODAL ===================== */}
      {selectedIncident && (
        <div className="fixed inset-0 bg-black/85 backdrop-blur-md flex items-center justify-center p-6 z-50 animate-fade-in">
          <div className="celestial-card w-full max-w-3xl rounded-3xl p-8 max-h-[90vh] overflow-y-auto border-cyan-400/30 shadow-[0_0_80px_rgba(0,0,0,0.95)]">
            <div className="flex items-center justify-between pb-4 border-b border-white/10">
              <div className="flex items-center gap-3">
                {getSeverityBadge(selectedIncident.severity)}
                <h3 className="font-cinzel text-lg font-bold text-white tracking-wide">{selectedIncident.title}</h3>
              </div>
              <button
                onClick={() => setSelectedIncident(null)}
                className="text-slate-400 hover:text-white text-xl font-bold p-1"
              >
                ✕
              </button>
            </div>

            {/* Gemini Threat Briefing */}
            <div className="my-6 bg-[#050814]/90 border border-cyan-400/30 p-6 rounded-2xl shadow-inner">
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-space text-xs font-bold text-cyan-400 uppercase tracking-widest flex items-center gap-2">
                  <img src="/logo.png" alt="ChainGuard" className="w-4 h-4 object-contain rounded" />
                  <span>Gemini Forensic Intelligence</span>
                </h4>
                <span className="font-space text-[10px] bg-cyan-950 text-cyan-300 border border-cyan-800 px-3 py-1 rounded-full">
                  Confidence: {selectedIncident.explanation?.confidence?.toUpperCase() || "HIGH"}
                </span>
              </div>
              <p className="font-sans text-xs sm:text-sm text-slate-200 leading-relaxed mb-4 font-light">
                {selectedIncident.explanation?.summary}
              </p>
              <div className="font-sans text-xs text-amber-300 bg-amber-950/40 p-4 rounded-xl border border-amber-800/60 mb-4 font-light">
                <strong className="font-medium text-amber-200">Why it matters:</strong> {selectedIncident.explanation?.why_it_matters}
              </div>
              <div>
                <strong className="font-space text-xs text-slate-400 block mb-2 uppercase tracking-wider">Recommended Remediation Steps:</strong>
                <ul className="list-disc list-inside font-sans text-xs text-slate-300 space-y-1.5 font-light">
                  {selectedIncident.explanation?.what_to_do?.map((step, idx) => (
                    <li key={idx}>{step}</li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Timeline */}
            <div className="mb-6">
              <h4 className="font-space text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">Code-to-Breach Timeline</h4>
              <div className="border-l-2 border-cyan-400/30 ml-3 space-y-5 text-xs font-space">
                {selectedIncident.evidence?.paste_time && (
                  <div className="relative pl-6">
                    <div className="absolute -left-1.5 top-0.5 w-3 h-3 rounded-full bg-amber-400 shadow-[0_0_10px_#f59e0b]" />
                    <p className="font-bold text-white">1. Developer Secret Paste Intercepted</p>
                    <p className="font-sans text-slate-400 text-[11px] font-light">
                      Observed on {selectedIncident.evidence.source} at {new Date(selectedIncident.evidence.paste_time).toLocaleTimeString()}
                    </p>
                  </div>
                )}
                {selectedIncident.evidence?.dependency && (
                  <div className="relative pl-6">
                    <div className="absolute -left-1.5 top-0.5 w-3 h-3 rounded-full bg-orange-400 shadow-[0_0_10px_#f97316]" />
                    <p className="font-bold text-white">2. Runtime Vulnerability Correlated</p>
                    <p className="font-sans text-slate-400 text-[11px] font-light">
                      {selectedIncident.evidence.dependency} {selectedIncident.evidence.version} carries {selectedIncident.evidence.vuln_id}
                    </p>
                  </div>
                )}
                <div className="relative pl-6">
                  <div className="absolute -left-1.5 top-0.5 w-3 h-3 rounded-full bg-rose-500 shadow-[0_0_10px_#f43f5e]" />
                  <p className="font-bold text-white">3. Live Inbound Replay Matched</p>
                  <p className="font-sans text-slate-400 text-[11px] font-light">
                    Traffic from {selectedIncident.evidence?.ip || "external attacker"} targeting {selectedIncident.evidence?.path || "/"}
                  </p>
                </div>
              </div>
            </div>

            {/* Raw JSON */}
            <div className="mb-6">
              <h4 className="font-space text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Cryptographic Evidence</h4>
              <pre className="bg-[#03050c] p-4 rounded-2xl text-[11px] font-space text-cyan-300 overflow-x-auto border border-white/10">
                {JSON.stringify(selectedIncident.evidence, null, 2)}
              </pre>
            </div>

            {/* Actions */}
            <div className="pt-6 border-t border-white/10">
              <h4 className="font-space text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">Two-Speed Containment Protocol</h4>
              {selectedIncident.actions && selectedIncident.actions.length > 0 ? (
                <div className="space-y-3 font-space">
                  {selectedIncident.actions.map((act) => (
                    <div
                      key={act.id}
                      className="flex flex-wrap items-center justify-between gap-4 bg-[#050814] p-4 rounded-2xl border border-white/10"
                    >
                      <div>
                        <div className="flex items-center gap-2.5">
                          <span className="font-bold text-sm text-white">{act.type}</span>
                          <span className={`text-[10px] px-2.5 py-0.5 rounded-full font-bold ${
                            act.status === "applied"
                              ? "bg-emerald-950 text-emerald-400 border border-emerald-800"
                              : act.status === "pending"
                              ? "bg-amber-950 text-amber-400 border border-amber-800 animate-pulse"
                              : "bg-slate-800 text-slate-400"
                          }`}>
                            {act.status.toUpperCase()}
                          </span>
                        </div>
                        <p className="text-xs text-slate-400 mt-1">Target: {act.target}</p>
                      </div>

                      <div className="flex items-center gap-2">
                        {act.status === "pending" && (
                          <button
                            onClick={() =>
                              setConfirmDialog({
                                isOpen: true,
                                title: `Authorize ${act.type}?`,
                                message: `Are you sure you want to enforce ${act.type} on target '${act.target}'?`,
                                onConfirm: () => {
                                  handleActionApprove(act.id);
                                  setConfirmDialog({ isOpen: false, title: "", message: "", onConfirm: () => {} });
                                },
                              })
                            }
                            className="btn-constellation-cyan text-xs px-4 py-2 rounded-xl font-bold"
                          >
                            Authorize Action
                          </button>
                        )}
                        {act.status === "applied" && act.reversible && (
                          <button
                            onClick={() =>
                              setConfirmDialog({
                                isOpen: true,
                                title: `Undo ${act.type}?`,
                                message: `Are you sure you want to revert the containment rule on target '${act.target}'?`,
                                onConfirm: () => {
                                  handleActionUndo(act.id);
                                  setConfirmDialog({ isOpen: false, title: "", message: "", onConfirm: () => {} });
                                },
                              })
                            }
                            className="bg-amber-600 hover:bg-amber-500 text-slate-950 font-bold text-xs px-4 py-2 rounded-xl"
                          >
                            Revert Containment
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="font-space text-xs text-slate-500">No mitigation actions required for this incident.</p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ===================== SOC HELPLINE MODAL ===================== */}
      {isHelplineOpen && (
        <div className="fixed inset-0 bg-black/85 backdrop-blur-md flex items-center justify-center p-6 z-50">
          <div className="celestial-card w-full max-w-lg rounded-3xl p-8 border-rose-500/40 shadow-2xl">
            <div className="flex items-center justify-between pb-4 border-b border-white/10 mb-6">
              <div className="flex items-center gap-3">
                <img
                  src="/logo.png"
                  alt="ChainGuard SOC"
                  className="w-10 h-10 rounded-xl object-contain drop-shadow-[0_0_20px_rgba(56,189,248,0.5)]"
                />
                <div>
                  <h3 className="font-cinzel text-base font-bold text-white tracking-wider">24/7 Incident Escalation</h3>
                  <p className="font-space text-[10px] text-cyan-400 tracking-wider">Founder: Swayam Prakash Sahu</p>
                </div>
              </div>
              <button
                onClick={() => setIsHelplineOpen(false)}
                className="text-slate-400 hover:text-white text-lg font-bold"
              >
                ✕
              </button>
            </div>

            <p className="font-sans text-xs text-slate-300 leading-relaxed font-light mb-6">
              Direct escalation channel for critical production perimeter breach signals or anomalous credential replays:
            </p>

            <div className="space-y-3 font-space text-xs">
              <div className="bg-[#050814] border border-white/10 p-5 rounded-2xl flex items-center justify-between">
                <div>
                  <span className="text-[10px] text-slate-500 block uppercase tracking-wider">Voice Hotline</span>
                  <a href="tel:+919438316656" className="text-base font-bold text-cyan-300 hover:underline">
                    +91 9438316656
                  </a>
                  <span className="text-[10px] text-slate-400 block mt-0.5">Swayam Prakash Sahu</span>
                </div>
                <a href="tel:+919438316656" className="btn-constellation-cyan text-xs font-bold px-4 py-2 rounded-xl">
                  Call Now
                </a>
              </div>

              <div className="bg-[#050814] border border-white/10 p-5 rounded-2xl flex items-center justify-between">
                <div>
                  <span className="text-[10px] text-slate-500 block uppercase tracking-wider">SOC Operations Email</span>
                  <a href="mailto:swayamprakashsahu10@gmail.com" className="text-xs font-bold text-cyan-300 hover:underline block break-all">
                    swayamprakashsahu10@gmail.com
                  </a>
                </div>
                <a href="mailto:swayamprakashsahu10@gmail.com" className="btn-constellation-cyan text-xs font-bold px-4 py-2 rounded-xl">
                  Compose
                </a>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-white/10 flex items-center justify-between text-[11px] font-space text-slate-500">
              <span>CHAINGUARD GLOBAL OPERATIONS</span>
              <span>15-MINUTE SLA</span>
            </div>
          </div>
        </div>
      )}

      {/* ===================== CONFIRMATION MODAL ===================== */}
      {confirmDialog.isOpen && (
        <div className="fixed inset-0 bg-black/90 backdrop-blur-md flex items-center justify-center p-6 z-50">
          <div className="celestial-card w-full max-w-sm rounded-2xl p-6 border-white/15 shadow-2xl">
            <h4 className="font-cinzel text-base font-bold text-white mb-2 tracking-wider">{confirmDialog.title}</h4>
            <p className="font-sans text-xs text-slate-300 mb-6 leading-relaxed font-light">{confirmDialog.message}</p>
            <div className="flex justify-end gap-3 font-space text-xs">
              <button
                onClick={() => setConfirmDialog({ isOpen: false, title: "", message: "", onConfirm: () => {} })}
                className="bg-slate-800 hover:bg-slate-700 text-slate-200 px-4 py-2 rounded-xl"
              >
                Cancel
              </button>
              <button
                onClick={confirmDialog.onConfirm}
                className="btn-constellation-cyan font-bold px-5 py-2 rounded-xl"
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
