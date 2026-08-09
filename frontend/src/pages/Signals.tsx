import { useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import { useFetch } from "../hooks/useFetch";
import { Card, EmptyState, ErrorState, Loading, RiskBadge } from "../components/ui";

const LEVELS = ["", "LOW", "MODERATE", "HIGH", "CRITICAL"];

export function SignalsPage() {
  const [risk, setRisk] = useState("");
  const [minReports, setMinReports] = useState("");
  const [search, setSearch] = useState("");

  const { data, loading, error } = useFetch(
    () => api.signs({ risk_level: risk || undefined, min_reports: minReports ? Number(minReports) : undefined, limit: 200 }),
    [risk, minReports]
  );

  const filtered = (data?.signals ?? []).filter((s) => {
    if (!search) return true;
    const q = search.toLowerCase();
    return s.drug.toLowerCase().includes(q) || s.reaction.toLowerCase().includes(q);
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">Safety Signal Monitor</h1>
        <p className="text-sm text-slate-500">
          Analytical drug-reaction signals requiring further investigation.
        </p>
      </div>

      <div className="card p-4">
        <div className="flex flex-wrap gap-3">
          <input
            className="input-base max-w-xs"
            placeholder="Filter by drug or reaction…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <select
            className="input-base max-w-[10rem]"
            value={risk}
            onChange={(e) => setRisk(e.target.value)}
            aria-label="Risk level"
          >
            {LEVELS.map((l) => (
              <option key={l} value={l}>
                {l === "" ? "All risk levels" : l}
              </option>
            ))}
          </select>
          <input
            className="input-base max-w-[10rem]"
            type="number"
            min={0}
            placeholder="Min reports"
            value={minReports}
            onChange={(e) => setMinReports(e.target.value)}
          />
        </div>
      </div>

      {loading && <Loading label="Loading signals…" />}
      {error && <ErrorState message={error} />}

      {!loading && !error && (
        <Card title={`Signals (${filtered.length})`}>
          {filtered.length === 0 ? (
            <EmptyState message="No signals match the current filters." />
          ) : (
            <div className="overflow-x-auto">
              <table className="table-base">
                <thead>
                  <tr>
                    <th>Drug</th>
                    <th>Reaction</th>
                    <th className="text-right">Reports</th>
                    <th className="text-right">Serious</th>
                    <th className="text-right">Serious Rate</th>
                    <th className="text-right">Priority</th>
                    <th>Risk</th>
                    <th />
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((s, i) => (
                    <tr key={`${s.drug}-${s.reaction}-${i}`}>
                      <td className="font-medium text-slate-800">{s.drug}</td>
                      <td>{s.reaction}</td>
                      <td className="text-right">{s.reports}</td>
                      <td className="text-right">{s.serious_reports}</td>
                      <td className="text-right">{Math.round(s.serious_rate * 100)}%</td>
                      <td className="text-right">{s.priority_score.toFixed(2)}</td>
                      <td><RiskBadge level={s.risk_level} /></td>
                      <td>
                        <Link
                          to={`/signals/${encodeURIComponent(s.drug)}/${encodeURIComponent(s.reaction)}`}
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
          )}
        </Card>
      )}
    </div>
  );
}
