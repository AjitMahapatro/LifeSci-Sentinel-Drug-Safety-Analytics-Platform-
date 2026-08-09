import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api";
import { useFetch } from "../hooks/useFetch";
import { TrendChart, BarChart } from "../components/charts";
import {
  Card,
  EmptyState,
  ErrorState,
  KpiCard,
  Loading,
  RiskBadge,
} from "../components/ui";

export function DrugPage() {
  const { name } = useParams();
  const [query, setQuery] = useState("");
  const [search, setSearch] = useState(name ?? "");

  const list = useFetch(
    () => api.drugs({ search, limit: 50 }),
    [search]
  );

  const selected = name ?? (search || null);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">Drug Investigation</h1>
        <p className="text-sm text-slate-500">
          Search a drug to view its safety profile, signals, and reporting trends.
        </p>
      </div>

      <form
        className="flex gap-2"
        onSubmit={(e) => {
          e.preventDefault();
          setSearch(query.trim());
        }}
      >
        <input
          className="input-base max-w-sm"
          placeholder="e.g. LIPITOR, HUMIRA"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button className="btn-primary" type="submit">
          Search
        </button>
      </form>

      {list.data && list.data.drugs.length > 0 && (
        <div className="card max-h-52 overflow-y-auto p-2">
          <ul className="text-sm">
            {list.data.drugs.slice(0, 25).map((d) => (
              <li key={d.drug_name}>
                <Link
                  to={`/drugs/${encodeURIComponent(d.drug_name)}`}
                  onClick={() => setSearch(d.drug_name)}
                  className="flex items-center justify-between rounded px-2 py-1.5 hover:bg-slate-50"
                >
                  <span className="text-slate-700">{d.drug_name}</span>
                  <span className="text-xs text-slate-400">
                    {d.total_reports} reports
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        </div>
      )}

      {selected ? (
        <DrugDetail name={selected} />
      ) : (
        <EmptyState message="Search or select a drug to begin." />
      )}
    </div>
  );
}

function DrugDetail({ name }: { name: string }) {
  const { data, loading, error } = useFetch(() => api.drug(name), [name]);

  if (loading) return <Loading label="Loading drug profile…" />;
  if (error || !data) return <ErrorState message={error ?? "Drug not found"} />;

  const d = data;
  const topReactions = d.top_reactions.slice(0, 10).map((r) => ({
    label:
      r.reaction_name.length > 14
        ? r.reaction_name.slice(0, 13) + "…"
        : r.reaction_name,
    value: r.count,
  }));

  return (
    <div className="space-y-6">
      <div className="card flex flex-wrap items-center gap-4 p-4">
        <div>
          <h2 className="text-lg font-semibold text-slate-900">{d.drug_name}</h2>
          <div className="mt-1 flex items-center gap-2">
            <RiskBadge level={d.risk.risk_level} />
            <span className="text-xs text-slate-500">
              Priority {d.priority_score.toFixed(2)} ({d.priority_level})
            </span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <KpiCard label="Reports" value={d.total_reports.toLocaleString()} />
        <KpiCard label="Serious" value={d.serious_reports.toLocaleString()} />
        <KpiCard
          label="Serious Rate"
          value={`${Math.round(d.serious_rate * 100)}%`}
        />
        <KpiCard label="Risk" value={<RiskBadge level={d.risk.risk_level} />} />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card title="Top Reactions">
          {topReactions.length ? (
            <BarChart data={topReactions} color="#0f766e" />
          ) : (
            <EmptyState message="No reaction data." />
          )}
        </Card>
        <Card title="Reporting Trend">
          {d.trends.length ? (
            <TrendChart points={d.trends} />
          ) : (
            <EmptyState message="No trend data." />
          )}
        </Card>
      </div>

      <Card title="Signal Rationale">
        <ul className="list-disc space-y-1 pl-5 text-sm text-slate-600">
          {d.risk.rationale.map((r, i) => (
            <li key={i}>{r}</li>
          ))}
        </ul>
      </Card>

      <Card title="Safety Signals">
        {d.signals.length ? (
          <div className="overflow-x-auto">
            <table className="table-base">
              <thead>
                <tr>
                  <th>Reaction</th>
                  <th className="text-right">Reports</th>
                  <th className="text-right">Serious</th>
                  <th className="text-right">Serious Rate</th>
                  <th>Risk</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {d.signals.slice(0, 10).map((s, i) => (
                  <tr key={i}>
                    <td>{s.reaction}</td>
                    <td className="text-right">{s.reports}</td>
                    <td className="text-right">{s.serious_reports}</td>
                    <td className="text-right">
                      {Math.round(s.serious_rate * 100)}%
                    </td>
                    <td>
                      <RiskBadge level={s.risk_level} />
                    </td>
                    <td>
                      <Link
                        to={`/signals/${encodeURIComponent(d.drug_name)}/${encodeURIComponent(s.reaction)}`}
                        className="text-brand-700 hover:underline"
                      >
                        Investigate
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <EmptyState message="No signals for this drug." />
        )}
      </Card>
    </div>
  );
}
