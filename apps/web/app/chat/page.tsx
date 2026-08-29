"use client";

import { FormEvent, useState } from "react";

import { api } from "@/lib/api";
import { Panel } from "@/components/ui/panel";

export default function ChatPage() {
  const [message, setMessage] = useState("");
  const [reply, setReply] = useState("");
  const [provider, setProvider] = useState("");
  const [sources, setSources] = useState<Array<Record<string, unknown>>>([]);
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    try {
      const result = await api.chat(message);
      setReply(result.reply.content);
      setProvider(result.provider);
      setSources(result.citations);
      setMessage("");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
      <Panel title="Chat" description="Persistent conversation flow with memory and document retrieval support.">
        <form onSubmit={onSubmit} className="space-y-4">
          <textarea
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            placeholder="Ask NEXUS about your projects, documents, skills, or goals."
            className="min-h-40 w-full rounded-2xl border border-border bg-black/20 p-4 outline-none"
          />
          <button
            type="submit"
            disabled={!message || loading}
            className="rounded-2xl bg-accent px-4 py-2 font-medium text-slate-950 disabled:opacity-50"
          >
            {loading ? "Thinking..." : "Send"}
          </button>
        </form>
      </Panel>
      <Panel title="Response" description={provider ? `Provider: ${provider}` : "No response yet"}>
        <div className="whitespace-pre-wrap text-sm text-zinc-200">{reply || "Send a message to start."}</div>
        {sources.length ? (
          <div className="mt-6 space-y-3">
            {sources.map((source, index) => (
              <div key={index} className="rounded-2xl border border-border px-4 py-3 text-sm text-muted">
                {JSON.stringify(source)}
              </div>
            ))}
          </div>
        ) : null}
      </Panel>
    </div>
  );
}

