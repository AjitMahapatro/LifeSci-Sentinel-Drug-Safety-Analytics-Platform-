import type { TrendPoint } from "../types";

/** Minimal, dependency-free bar chart to visualize report volumes. */
export function BarChart({
  data,
  height = 180,
  color = "#1d6ef5",
}: {
  data: { label: string; value: number; sub?: string }[];
  height?: number;
  color?: string;
}) {
  const max = Math.max(1, ...data.map((d) => d.value));
  return (
    <div className="flex items-end gap-1" style={{ height }} aria-hidden="true">
      {data.map((d, i) => {
        const h = Math.max(2, (d.value / max) * height);
        return (
          <div
            key={i}
            className="flex flex-1 flex-col items-center justify-end"
            style={{ height }}
          >
            <div
              className="w-full rounded-t-sm"
              style={{ height: h, backgroundColor: color, minWidth: 6 }}
              title={`${d.label}: ${d.value}`}
            />
          </div>
        );
      })}
    </div>
  );
}

/** Simple line/area chart for reporting trends. */
export function TrendChart({
  points,
  height = 180,
}: {
  points: TrendPoint[];
  height?: number;
}) {
  if (!points.length) return null;
  const max = Math.max(1, ...points.map((p) => p.total_reports));
  const w = 100;
  const h = height;
  const step = w / Math.max(1, points.length - 1);
  const coords = points.map((p, i) => ({
    x: i * step,
    y: h - (p.total_reports / max) * (h - 8) - 4,
  }));
  const line = coords.map((c, i) => `${i === 0 ? "M" : "L"}${c.x},${c.y}`).join(" ");
  const area = `${line} L${w},${h} L0,${h} Z`;
  const labels = points.filter((_, i) => i % Math.ceil(points.length / 6) === 0);

  return (
    <div>
      <svg
        viewBox={`0 0 ${w} ${h}`}
        preserveAspectRatio="none"
        className="h-40 w-full"
        role="img"
        aria-label="Reporting trend chart"
      >
        <path d={area} fill="#1d6ef5" opacity={0.12} />
        <path
          d={line}
          fill="none"
          stroke="#1d6ef5"
          strokeWidth={1.5}
          vectorEffect="non-scaling-stroke"
        />
      </svg>
      <div className="mt-1 flex justify-between text-[10px] text-slate-400">
        {labels.map((p, i) => (
          <span key={i}>
            {p.month_name.substring(0, 3)} {p.year}
          </span>
        ))}
      </div>
    </div>
  );
}
