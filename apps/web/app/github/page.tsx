"use client";

import { FormEvent, useEffect, useState } from "react";

import { api } from "@/lib/api";
import { RepositoryRecord } from "@/lib/types";
import { Panel } from "@/components/ui/panel";

export default function GitHubPage() {
  const [url, setUrl] = useState("");
  const [repositories, setRepositories] = useState<RepositoryRecord[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.repositories().then(setRepositories).catch(() => undefined);
  }, []);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    try {
      const result = await api.analyzeRepository(url);
      setRepositories((current) => [result, ...current]);
      setUrl("");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <Panel title="GitHub Intelligence" description="Analyze repositories without exposing the GitHub token to the browser.">
        <form onSubmit={onSubmit} className="flex flex-col gap-4 md:flex-row">
          <input
            value={url}
            onChange={(event) => setUrl(event.target.value)}
            placeholder="https://github.com/owner/repository"
            className="flex-1 rounded-2xl border border-border bg-black/20 px-4 py-3 outline-none"
          />
          <button type="submit" disabled={!url || loading} className="rounded-2xl bg-accent px-4 py-3 font-medium text-slate-950 disabled:opacity-50">
            {loading ? "Analyzing..." : "Analyze"}
          </button>
        </form>
      </Panel>

      <Panel title="Repositories">
        <div className="space-y-4">
          {repositories.map((repository) => (
            <div key={repository.id} className="rounded-2xl border border-border p-4">
              <div className="font-medium">
                {repository.owner}/{repository.name}
              </div>
              <div className="mt-2 text-sm text-muted">{repository.latest_analysis?.summary}</div>
              <div className="mt-3 text-sm text-zinc-300">{repository.latest_analysis?.architecture}</div>
            </div>
          ))}
        </div>
      </Panel>
    </div>
  );
}

