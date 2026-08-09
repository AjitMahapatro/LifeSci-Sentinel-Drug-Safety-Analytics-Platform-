import { api } from "../api";
import { useFetch } from "../hooks/useFetch";
import { BarChart, TrendChart } from "../components/charts";
import { Card, EmptyState, ErrorState, KpiCard, Loading } from "../components/ui";
import { Link } from "react-router-dom";

export function OverviewPage() {
  const { data, loading, error } = useFetch(() => api.overview());

  if (loading) return <Loading label="Loading executive overview…" />;
  if (error || !data) return <ErrorState message={error ?? "No data"} />;

  const s = data.summary;
  const topDrugs = data.top_drugs.slice(0, 8).map((d) => ({
    label: d.name.length > 14 ? d.name.slice(0, 13) + "…" : d.name,
    value: d.count,
  }));
  const topReactions = data.top_reactions.slice(0, 8).map((r) => ({
    label: r.name.length > 14 ? r.name.slice(0, 13) + "…" : r.name,
    value: r.count,
  }));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">Executive Overview</h1>
        <p className="text-sm text-slate-500">
          Real-world pharmacovigilance analytics from OpenFDA / FAERS adverse-event data.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <KpiCard label="Total Reports" value={s.total_reports.toLocaleString()} />
        <KpiCard label="Total Drugs" value={s.total_drugs.toLocaleString()} />
        <KpiCard label="Serious Reports" value={s.serious_reports.toLocaleString()} />
        <KpiCard
          label="Serious Rate"
          value={`${Math.round(s.serious_rate * 100)}%`}
          accent="text-brand-700"
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card title="Reporting Trend">
          {data.trends.length ? (
            <TrendChart points={data.trends} />
          ) : (
            <EmptyState message="No trend data available." />
          )}
        </Card>
        <Card title="Top Reactions">
          {topReactions.length ? (
            <BarChart data={topReactions} color="#0f766e" />
          ) : (
            <EmptyState message="No reaction data available." />
          )}
        </Card>
        <Card title="Top Reported Drugs">
          {topDrugs.length ? (
            <BarChart data={topDrugs} />
          ) : (
            <EmptyState message="No drug data available." />
          )}
        </Card>
        <Card title="Top Reactions by Count">
          <ul className="divide-y divide-slate-100 text-sm">
            {data.top_reactions.slice(0, 8).map((r) => (
              <li key={r.name} className="flex items-center justify-between py-1.5">
                <span className="truncate text-slate-700">{r.name}</span>
                <span className="font-medium text-slate-500">{r.count}</span>
              </li>
            ))}
          </ul>
        </Card>
      </div>

      <Card title="Top Drugs">
        <div className="overflow-x-auto">
          <table className="table-base">
            <thead>
              <tr>
                <th>Drug</th>
                <th className="text-right">Reports</th>
              </tr>
            </thead>
            <tbody>
              {data.top_drugs.slice(0, 10).map((d) => (
                <tr key={d.name}>
                  <td>
                    <Link
                      to={`/drugs/${encodeURIComponent(d.name)}`}
                      className="text-brand-700 hover:underline"
                    >
                      {d.name}
                    </Link>
                  </td>
                  <td className="text-right">{d.count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
