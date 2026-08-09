import { NavLink, Route, Routes } from "react-router-dom";
import { OverviewPage } from "./pages/Overview";
import { DrugPage } from "./pages/Drug";
import { SignalPage } from "./pages/Signal";
import { SignalsPage } from "./pages/Signals";
import { AiPage } from "./pages/Ai";

const nav = [
  { to: "/", label: "Executive Overview", end: true },
  { to: "/drugs", label: "Drug Investigation" },
  { to: "/signals", label: "Safety Signals" },
  { to: "/ai", label: "AI Assistant" },
];

export default function App() {
  return (
    <div className="min-h-screen bg-slate-50">
      <header className="sticky top-0 z-10 border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3">
          <NavLink to="/" className="flex items-center gap-2">
            <span className="flex h-8 w-8 items-center justify-center rounded-md bg-brand-600 text-sm font-bold text-white">
              LS
            </span>
            <span className="text-sm font-semibold text-slate-800">
              LifeSci Sentinel
            </span>
          </NavLink>
          <nav className="flex items-center gap-1 overflow-x-auto" aria-label="Main">
            {nav.map((n) => (
              <NavLink
                key={n.to}
                to={n.to}
                end={n.end}
                className={({ isActive }) =>
                  `whitespace-nowrap rounded-md px-3 py-1.5 text-sm font-medium ${
                    isActive
                      ? "bg-brand-50 text-brand-700"
                      : "text-slate-600 hover:bg-slate-100"
                  }`
                }
              >
                {n.label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-6">
        <Routes>
          <Route path="/" element={<OverviewPage />} />
          <Route path="/drugs" element={<DrugPage />} />
          <Route path="/drugs/:name" element={<DrugPage />} />
          <Route path="/signals" element={<SignalsPage />} />
          <Route
            path="/signals/:drug/:reaction"
            element={<SignalPage />}
          />
          <Route path="/ai" element={<AiPage />} />
        </Routes>
      </main>
      <footer className="mx-auto max-w-7xl px-4 py-6 text-xs text-slate-400">
        LifeSci Sentinel provides analytical decision support based on available
        adverse-event data. It does not provide medical diagnosis, treatment
        recommendations, or establish causality.
      </footer>
    </div>
  );
}
