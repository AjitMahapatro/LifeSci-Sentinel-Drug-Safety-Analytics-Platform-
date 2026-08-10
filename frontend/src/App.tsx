import { useEffect, useState } from "react";
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
  const [theme, setTheme] = useState<"light" | "dark">("light");

  useEffect(() => {
    const stored = localStorage.getItem("theme");
    setTheme(stored === "dark" ? "dark" : "light");
  }, []);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
    localStorage.setItem("theme", theme);
  }, [theme]);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      <header className="sticky top-0 z-10 border-b border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-950">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-3 px-4 py-3">
          <div className="flex items-center gap-2">
            <NavLink to="/" className="flex items-center gap-2">
              <span className="flex h-8 w-8 items-center justify-center rounded-md bg-brand-600 text-sm font-bold text-white">
                LS
              </span>
              <span className="text-sm font-semibold text-slate-800 dark:text-slate-100">
                LifeSci Sentinel
              </span>
            </NavLink>
          </div>
          <div className="flex items-center gap-2">
            <nav className="flex items-center gap-1 overflow-x-auto" aria-label="Main">
              {nav.map((n) => (
                <NavLink
                  key={n.to}
                  to={n.to}
                  end={n.end}
                  className={({ isActive }) =>
                    `whitespace-nowrap rounded-md px-3 py-1.5 text-sm font-medium ${
                      isActive
                        ? "bg-brand-50 text-brand-700 dark:bg-brand-900/20 dark:text-brand-300"
                        : "text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
                    }`
                  }
                >
                  {n.label}
                </NavLink>
              ))}
            </nav>
            <button
              type="button"
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
              className="rounded-md border border-slate-200 bg-white px-3 py-1.5 text-sm font-medium text-slate-600 hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200 dark:hover:bg-slate-800"
              aria-label={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
            >
              {theme === "dark" ? "☀ Light" : "🌙 Dark"}
            </button>
          </div>
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
