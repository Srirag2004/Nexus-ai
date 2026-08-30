"use client";

import { FormEvent, useEffect, useState } from "react";
import { Github, LockKeyhole } from "lucide-react";

import { api } from "@/lib/api";
import { RepositoryRecord } from "@/lib/types";
import { Panel } from "@/components/ui/panel";

export default function GitHubPage() {
  const [url, setUrl] = useState("");
  const [repositories, setRepositories] = useState<RepositoryRecord[]>([]);
  const [available, setAvailable] = useState<Array<{ id: number; full_name: string; url: string; private: boolean; description: string }>>([]);
  const [connected, setConnected] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.repositories().then(setRepositories).catch(() => undefined);
    api.githubConnection().then((result) => {
      setConnected(result.connected);
      if (result.connected) api.availableGitHubRepositories().then(setAvailable).catch(() => undefined);
    }).catch(() => undefined);
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

  async function importRepository(repositoryUrl: string) {
    setLoading(true);
    try {
      const result = await api.importGitHubRepository(repositoryUrl);
      setRepositories((current) => [result, ...current]);
      setAvailable((current) => current.filter((repository) => repository.url !== repositoryUrl));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <Panel title="GitHub connection" description="Connect your GitHub account to browse and import repositories you explicitly authorize, including private repositories.">
        {connected ? <div className="flex items-center gap-2 text-sm text-accent"><Github size={17} /> GitHub connected. Select a repository below to import it into NEXUS.</div> : <button onClick={() => window.location.assign(api.oauthStartUrl("github"))} className="inline-flex items-center gap-2 rounded-2xl bg-accent px-4 py-3 text-sm font-medium text-slate-950"><LockKeyhole size={16} />Connect GitHub</button>}
      </Panel>
      {connected && available.length ? <Panel title="Your GitHub repositories" description="Import a repository to create an architecture brief and make it available in Projects."><div className="space-y-3">{available.map((repository) => <div key={repository.id} className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-border p-4"><div><div className="font-medium">{repository.full_name} {repository.private ? <span className="ml-2 text-xs text-amber-200">Private</span> : null}</div><div className="mt-1 text-sm text-muted">{repository.description || "No description"}</div></div><button disabled={loading} onClick={() => importRepository(repository.url)} className="rounded-xl border border-accent/40 px-3 py-2 text-sm text-accent disabled:opacity-50">Import</button></div>)}</div></Panel> : null}
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
