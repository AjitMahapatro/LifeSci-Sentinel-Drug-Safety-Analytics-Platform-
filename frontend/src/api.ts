import type {
  AIResponse,
  Drug,
  DrugDetail,
  Overview,
  ReactionSummary,
  Signal,
  SignalInvestigation,
} from "./types";

const BASE = ""; // Vite dev proxy forwards /api to FastAPI

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, init);
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

export const api = {
  health: () => request<Record<string, unknown>>("/health"),

  overview: () => request<Overview>("/api/analytics/overview"),

  trends: () => request<{ trends: Overview["trends"] }>("/api/analytics/trends"),

  drugs: (params?: { search?: string; risk_level?: string; min_reports?: number; limit?: number }) => {
    const q = new URLSearchParams();
    if (params?.search) q.set("search", params.search);
    if (params?.risk_level) q.set("risk_level", params.risk_level);
    if (params?.min_reports) q.set("min_reports", String(params.min_reports));
    q.set("limit", String(params?.limit ?? 100));
    return request<{ count: number; drugs: Drug[] }>(`/api/drugs?${q.toString()}`);
  },

  drug: (name: string) =>
    request<DrugDetail>(`/api/drugs/${encodeURIComponent(name)}`),

  drugReactions: (name: string) =>
    request<{ drug_name: string; reactions: { reaction_name: string; count: number }[] }>(
      `/api/drugs/${encodeURIComponent(name)}/reactions`
    ),

  reactions: (limit = 100) =>
    request<{ count: number; reactions: ReactionSummary[] }>(
      `/api/reactions?limit=${limit}`
    ),

  signs: (params?: { risk_level?: string; min_reports?: number; limit?: number }) => {
    const q = new URLSearchParams();
    if (params?.risk_level) q.set("risk_level", params.risk_level);
    if (params?.min_reports) q.set("min_reports", String(params.min_reports));
    q.set("limit", String(params?.limit ?? 100));
    return request<{ count: number; signals: Signal[] }>(`/api/signals?${q.toString()}`);
  },

  signal: (drug: string, reaction: string) =>
    request<SignalInvestigation>(
      `/api/signals/${encodeURIComponent(drug)}/${encodeURIComponent(reaction)}/investigation`
    ),

  ai: (question: string, drug?: string, reaction?: string) =>
    request<AIResponse>("/api/ai/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, drug, reaction }),
    }),
};
