import type { ReactNode } from "react";

export function Loading({ label = "Loading data…" }: { label?: string }) {
  return (
    <div
      role="status"
      className="flex items-center justify-center gap-2 py-12 text-sm text-slate-500"
    >
      <svg
        className="h-4 w-4 animate-spin text-brand-600"
        viewBox="0 0 24 24"
        fill="none"
        aria-hidden="true"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
        />
      </svg>
      {label}
    </div>
  );
}

export function ErrorState({ message }: { message: string }) {
  return (
    <div
      role="alert"
      className="rounded-lg border border-red-200 bg-red-50 px-4 py-6 text-center text-sm text-red-700"
    >
      <div className="mb-1 font-semibold">Unable to load data</div>
      <div>{message}</div>
    </div>
  );
}

export function EmptyState({
  title = "No data",
  message,
}: {
  title?: string;
  message?: string;
}) {
  return (
    <div className="rounded-lg border border-dashed border-slate-300 bg-slate-50 px-4 py-10 text-center text-sm text-slate-500">
      <div className="mb-1 font-medium text-slate-600">{title}</div>
      {message && <div>{message}</div>}
    </div>
  );
}

type Level = "LOW" | "MODERATE" | "HIGH" | "CRITICAL" | string;

const levelStyles: Record<string, string> = {
  LOW: "bg-emerald-50 text-emerald-700 border-emerald-200",
  MODERATE: "bg-amber-50 text-amber-700 border-amber-200",
  HIGH: "bg-orange-50 text-orange-700 border-orange-200",
  CRITICAL: "bg-red-50 text-red-700 border-red-200",
};

export function RiskBadge({ level }: { level: Level }) {
  const key = (level || "").toUpperCase();
  const style = levelStyles[key] ?? "bg-slate-100 text-slate-600 border-slate-200";
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold ${style}`}
    >
      {(level || "—").toUpperCase()}
    </span>
  );
}

export function KpiCard({
  label,
  value,
  sub,
  accent = "text-slate-900",
}: {
  label: string;
  value: ReactNode;
  sub?: ReactNode;
  accent?: string;
}) {
  return (
    <div className="card p-4">
      <div className="kpi-label">{label}</div>
      <div className={`kpi-value ${accent}`}>{value}</div>
      {sub && <div className="mt-1 text-xs text-slate-500">{sub}</div>}
    </div>
  );
}

export function Card({
  title,
  children,
  action,
  className = "",
}: {
  title?: string;
  children: ReactNode;
  action?: ReactNode;
  className?: string;
}) {
  return (
    <section className={`card ${className}`}>
      {title && (
        <div className="card-header flex items-center justify-between">
          <h2 className="text-sm font-semibold text-slate-800">{title}</h2>
          {action}
        </div>
      )}
      <div className="p-4">{children}</div>
    </section>
  );
}

export function Percent({ value }: { value: number }) {
  return <>{Math.round(value * 100)}%</>;
}
