export interface Action {
  id: number;
  incident_id: number;
  type: string;
  reversible: boolean;
  status: "pending" | "applied" | "undone" | "expired";
  target: string;
  expires_at: string | null;
}

export interface IncidentExplanation {
  title: string;
  summary: string;
  why_it_matters: string;
  what_to_do: string[];
  confidence: "low" | "medium" | "high";
}

export interface Incident {
  id: number;
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  status: "open" | "contained" | "resolved" | "dismissed";
  title: string;
  evidence: Record<string, any>;
  explanation: IncidentExplanation;
  created_at: string;
  actions: Action[];
}

export interface Vuln {
  id: number;
  osv_id: string;
  summary: string;
  severity: string;
  fixed_in: string | null;
  exploit_keywords: string[];
}

export interface Dependency {
  id: number;
  app: string;
  ecosystem: string;
  name: string;
  version: string;
  vulns: Vuln[];
}

export interface AllowlistEntry {
  id: number;
  cidr: string;
  note: string;
}
