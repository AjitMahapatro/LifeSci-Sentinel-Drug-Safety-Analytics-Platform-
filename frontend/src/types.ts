export interface OverviewSummary {
  total_reports: number;
  total_drugs: number;
  total_reactions: number;
  serious_reports: number;
  serious_rate: number;
}

export interface TopItem {
  name: string;
  count: number;
}

export interface Overview {
  summary: OverviewSummary;
  top_drugs: TopItem[];
  top_reactions: TopItem[];
  trends: TrendPoint[];
}

export interface TrendPoint {
  date_key: number;
  year: number;
  month: number;
  month_name: string;
  total_reports: number;
  serious_reports: number;
  serious_rate: number;
}

export interface RiskInfo {
  risk_level: string;
  rationale: string[];
}

export interface Drug {
  drug_name: string;
  total_reports: number;
  serious_reports: number;
  serious_rate: number;
  priority_score: number;
  priority_level: string;
  risk: RiskInfo;
}

export interface ReactionCount {
  reaction_name: string;
  count: number;
}

export interface DrugDetail extends Drug {
  top_reactions: ReactionCount[];
  trends: TrendPoint[];
  signals: Signal[];
}

export interface ReactionSummary {
  reaction_name: string;
  total_reports: number;
  serious_reports: number;
  serious_rate: number;
  affected_drugs: number;
}

export interface Signal {
  drug: string;
  reaction: string;
  reports: number;
  serious_reports: number;
  serious_rate: number;
  priority_score: number;
  risk_level: string;
}

export interface AssociatedItem {
  name: string;
  count: number;
}

export interface DataQuality {
  status: string;
  duplicate_checks_passed?: boolean;
  required_fields_validated?: boolean;
  null_counts?: Record<string, number>;
  duplicate_events?: number;
  note?: string;
}

export interface SignalInvestigation {
  drug: string;
  reaction: string;
  risk_level: string;
  priority_score: number;
  reports: number;
  serious_reports: number;
  serious_rate: number;
  reporting_trend: TrendPoint[];
  associated_reactions: AssociatedItem[];
  associated_drugs: AssociatedItem[];
  data_quality: DataQuality;
  rationale: string[];
}

export interface AIResponse {
  answer: string;
  evidence: Record<string, unknown>[];
  sources: { type: string; description: string }[];
  question: string;
}
