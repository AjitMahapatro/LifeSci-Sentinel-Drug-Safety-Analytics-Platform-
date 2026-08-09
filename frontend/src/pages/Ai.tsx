import { useState } from "react";
import { api } from "../api";
import type { AIResponse } from "../types";
import { Card } from "../components/ui";

const SUGGESTIONS = [
  "Which drugs have the highest serious-report rate?",
  "Why is HUMIRA high priority?",
  "Compare LIPITOR and HUMIRA.",
  "What are the top reactions?",
  "What changed in reporting over time?",
];

interface Message {
  role: "user" | "assistant";
  text: string;
  evidence?: Record<string, unknown>[];
}

export function AiPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function ask(question: string) {
    if (!question.trim() || loading) return;
    setMessages((m) => [...m, { role: "user", text: question }]);
    setLoading(true);
    setInput("");
    try {
      const res: AIResponse = await api.ai(question);
      setMessages((m) => [
        ...m,
        { role: "assistant", text: res.answer, evidence: res.evidence },
      ]);
    } catch (e) {
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          text: e instanceof Error ? e.message : "Unable to get an answer.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">AI Assistant</h1>
        <p className="text-sm text-slate-500">
          Grounded analytical assistant. Answers are derived from actual LifeSci
          Sentinel data and never invent statistics.
        </p>
      </div>

      <Card title="Suggested questions">
        <div className="flex flex-wrap gap-2">
          {SUGGESTIONS.map((q) => (
            <button
              key={q}
              className="rounded-full border border-slate-200 px-3 py-1 text-xs text-slate-600 hover:border-brand-400 hover:text-brand-700"
              onClick={() => ask(q)}
            >
              {q}
            </button>
          ))}
        </div>
      </Card>

      <div className="card flex h-[26rem] flex-col">
        <div className="flex-1 space-y-4 overflow-y-auto p-4">
          {messages.length === 0 && (
            <p className="pt-8 text-center text-sm text-slate-400">
              Ask a question about drug safety signals, drug profiles, reactions,
              or reporting trends.
            </p>
          )}
          {messages.map((m, i) => (
            <div
              key={i}
              className={
                m.role === "user"
                  ? "flex justify-end"
                  : "flex justify-start"
              }
            >
              <div
                className={
                  m.role === "user"
                    ? "max-w-[80%] rounded-lg bg-brand-600 px-3 py-2 text-sm text-white"
                    : "max-w-[85%] rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-700"
                }
              >
                <div className="whitespace-pre-line">{m.text}</div>
                {m.evidence && m.evidence.length > 0 && (
                  <details className="mt-2 text-xs text-slate-500">
                    <summary className="cursor-pointer">Data basis</summary>
                    <pre className="mt-2 max-h-40 overflow-auto rounded bg-slate-100 p-2 text-[10px]">
                      {JSON.stringify(m.evidence, null, 2)}
                    </pre>
                  </details>
                )}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-500">
                Analyzing…
              </div>
            </div>
          )}
        </div>
        <form
          className="flex gap-2 border-t border-slate-100 p-3"
          onSubmit={(e) => {
            e.preventDefault();
            ask(input);
          }}
        >
          <input
            className="input-base"
            placeholder="Ask about a drug, signal, reaction, or trend…"
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
          <button className="btn-primary" type="submit" disabled={loading}>
            Ask
          </button>
        </form>
      </div>

      <p className="text-xs text-slate-400">
        LifeSci Sentinel provides analytical decision support based on available
        adverse-event data. It does not provide medical diagnosis, treatment
        recommendations, or establish causality.
      </p>
    </div>
  );
}
