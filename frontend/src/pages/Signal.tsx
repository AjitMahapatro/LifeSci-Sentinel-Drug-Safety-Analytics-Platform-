import { useParams } from "react-router-dom";
import { api } from "../api";
import { useFetch } from "../hooks/useFetch";
import { TrendChart } from "../components/charts";
import {
  Card,
  EmptyState,
  ErrorState,
  KpiCard,
  Loading,
  RiskBadge,
} from "../components/ui";

export function SignalPage() {
  const { drug, reaction } = useParams();
  const { data, loading, error } = useFetch(
    () =>
      drug && reaction
        ? api.signal(drug, reaction)
        : Promise.reject(new Error("Missing drug/reaction")),
    [drug, reaction]
  );

  if (loading) return <Loading label="Loading signal investigation…" />;
  if (error || !data) return <ErrorState message={error ?? "Signal not found"} />;

  const s = data;
  const dq = s.data_quality ?? {};
  const dqStatus = dq.status ?? "UNKNOWN";

  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-center gap-3">
          <h1 className="text-xl font-semibold text-slate-900">Signal Investigation</h1>
          <RiskBadge level={s.risk_level} />
        </div>
        <p className="text-sm text-slate-500">
          {s.drug} &nbsp;/&nbsp; {s.reaction}
        </p>
      </div>

      <div className="card p-4">
        <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-500">
          Signal Identity
        </h2>
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <div>
            <div className="kpi-label">Drug</div>
            <div className="font-medium text-slate-800">{s.drug}</div>
          </div>
          <div>
            <div className="kpi-label">Reaction</div>
            <div className="font-medium text-slate-800">{s.reaction}</div>
          </div>
          <div>
            <div className="kpi-label">Risk Level</div>
            <RiskBadge level={s.risk_level} />
          </div>
          <div>
            <div className="kpi-label">Priority Score</div>
            <div className="font-semibold text-slate-900">
              {s.priority_score.toFixed(2)}
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <KpiCard label="Reports" value={s.reports.toLocaleString()} />
        <KpiCard label="Serious Reports" value={s.serious_reports.toLocaleString()} />
        <KpiCard
          label="Serious Rate"
          value={`${Math.round(s.serious_rate * 100)}%`}
        />
        <KpiCard
          label="Data Quality"
          value={
            <span
              className={
                dqStatus === "PASS"
                  ? "text-emerald-600"
                  : dqStatus === "WARNING"
                  ? "text-amber-600"
                  : "text-slate-500"
              }
            >
              {dqStatus}
            </span>
          }
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card title="Why Was This Flagged?">
          <ul className="list-disc space-y-1 pl-5 text-sm text-slate-600">
            {(s.rationale ?? []).map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ul>
        </Card>

        <Card title="Data Quality">
          <ul className="space-y-1 text-sm text-slate-600">
            <li className="flex items-center gap-2">
              <DqMark ok={dqStatus === "PASS"} />
              Required fields validated
            </li>
            <li className="flex items-center gap-2">
              <DqMark ok={dq.duplicate_checks_passed} />
              Duplicate checks passed
            </li>
            <li className="flex items-center gap-2">
              <DqMark ok={dqStatus === "PASS"} />
              Referential integrity
            </li>
          </ul>
        </Card>
      </div>

      <Card title="Reporting Trend">
        {s.reporting_trend?.length ? (
          <TrendChart points={s.reporting_trend} />
        ) : (
          <EmptyState message="No trend data for this signal." />
        )}
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card title="Associated Reactions">
          {s.associated_reactions?.length ? (
            <ul className="divide-y divide-slate-100 text-sm">
              {(s.associated_reactions ?? []).slice(0, 10).map((r) => (
                <li key={r.name} className="flex justify-between py-1.5">
                  <span className="text-slate-700">{r.name}</span>
                  <span className="text-slate-500">{r.count}</span>
                </li>
              ))}
            </ul>
          ) : (
            <EmptyState message="No associated reactions." />
          )}
        </Card>
        <Card title="Associated Drugs">
          {s.associated_drugs?.length ? (
            <ul className="divide-y divide-slate-100 text-sm">
              {(s.associated_drugs ?? []).slice(0, 10).map((d) => (
                <li key={d.name} className="flex justify-between py-1.5">
                  <span className="text-slate-700">{d.name}</span>
                  <span className="text-slate-500">{d.count}</span>
                </li>
              ))}
            </ul>
          ) : (
            <EmptyState message="No associated drugs." />
          )}
        </Card>
      </div>

      <Card title="Interpretation">
        <p className="text-sm text-slate-600">
          This represents an <strong>analytical safety signal</strong> requiring
          further investigation. It does not establish causality, clinical risk,
          or a regulatory conclusion.
        </p>
      </Card>
    </div>
  );
}

function DqMark({ ok }: { ok?: boolean }) {
  return (
    <span
      aria-hidden="true"
      className={`flex h-4 w-4 items-center justify-center rounded-full text-[10px] font-bold ${
        ok
          ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-200"
          : "bg-amber-100 text-amber-700 dark:bg-amber-500/20 dark:text-amber-200"
      }`}
    >
      {ok ? "✓" : "!"}
    </span>
  );
}
