"use client";

import { useEffect, useState } from "react";

import { api } from "@/lib/api";
import { Panel } from "@/components/ui/panel";
import { Conversation, RepositoryRecord } from "@/lib/types";

type DashboardState = {
  system: string;
  conversations: Conversation[];
  documents: number;
  repositories: RepositoryRecord[];
  memories: number;
  agentRuns: number;
};

export default function DashboardPage() {
  const [state, setState] = useState<DashboardState>({
    system: "loading",
    conversations: [],
    documents: 0,
    repositories: [],
    memories: 0,
    agentRuns: 0,
  });

  useEffect(() => {
    Promise.all([
      api.health(),
      api.conversations(),
      api.documents(),
      api.repositories(),
      api.memories(),
      api.agentRuns(),
    ])
      .then(([health, conversations, documents, repositories, memories, agentRuns]) => {
        setState({
          system: `${health.status} / ${health.database}`,
          conversations,
          documents: documents.length,
          repositories,
          memories: memories.length,
          agentRuns: agentRuns.length,
        });
      })
      .catch(() => {
        setState((current) => ({ ...current, system: "backend unavailable" }));
      });
  }, []);

  const cards = [
    ["System", state.system],
    ["Conversations", `${state.conversations.length}`],
    ["Knowledge Docs", `${state.documents}`],
    ["Repositories", `${state.repositories.length}`],
    ["Memories", `${state.memories}`],
    ["Agent Runs", `${state.agentRuns}`],
  ];

  return (
    <div className="space-y-6">
      <Panel title="NEXUS AI" description="A command center for chat, knowledge, repositories, memory, and career context.">
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {cards.map(([label, value]) => (
            <div key={label} className="rounded-2xl border border-border bg-black/20 p-4">
              <div className="text-xs uppercase tracking-[0.25em] text-muted">{label}</div>
              <div className="mt-3 text-2xl font-semibold">{value}</div>
            </div>
          ))}
        </div>
      </Panel>

      <div className="grid gap-6 xl:grid-cols-2">
        <Panel title="Recent Conversations">
          <div className="space-y-3">
            {state.conversations.slice(0, 5).map((conversation) => (
              <div key={conversation.id} className="rounded-2xl border border-border px-4 py-3">
                <div className="font-medium">{conversation.title}</div>
                <div className="text-sm text-muted">{new Date(conversation.updated_at).toLocaleString()}</div>
              </div>
            ))}
          </div>
        </Panel>

        <Panel title="Repository Activity">
          <div className="space-y-3">
            {state.repositories.slice(0, 5).map((repository) => (
              <div key={repository.id} className="rounded-2xl border border-border px-4 py-3">
                <div className="font-medium">
                  {repository.owner}/{repository.name}
                </div>
                <div className="text-sm text-muted">{repository.latest_analysis?.summary ?? "Awaiting analysis"}</div>
              </div>
            ))}
          </div>
        </Panel>
      </div>
    </div>
  );
}
