"use client";

import { useEffect, useState } from "react";

import { api } from "@/lib/api";
import { AgentRun, EvaluationRun } from "@/lib/types";
import { Panel } from "@/components/ui/panel";

export default function AgentsPage() {
  const [runs, setRuns] = useState<AgentRun[]>([]);
  const [evaluations, setEvaluations] = useState<EvaluationRun[]>([]);

  useEffect(() => {
    api.agentRuns().then(setRuns).catch(() => undefined);
    api.evaluations().then(setEvaluations).catch(() => undefined);
  }, []);

  return (
    <div className="grid gap-6 xl:grid-cols-2">
      <Panel title="Agent Runs">
        <div className="space-y-3">
          {runs.length ? runs.map((run) => (
            <div key={run.id} className="rounded-2xl border border-border p-4">
              <div className="font-medium">{run.agent_name}</div>
              <div className="text-sm text-muted">{run.status} / {run.duration_ms}ms</div>
              <div className="mt-2 text-sm">{run.output_summary}</div>
            </div>
          )) : <div className="text-sm text-muted">No agent executions recorded yet.</div>}
        </div>
      </Panel>
      <Panel title="Evaluation Runs">
        <div className="space-y-3">
          {evaluations.length ? evaluations.map((evaluation) => (
            <div key={evaluation.id} className="rounded-2xl border border-border p-4 text-sm">
              <div className="font-medium">{evaluation.evaluation_type}</div>
              <div className="text-muted">{JSON.stringify(evaluation.metrics)}</div>
            </div>
          )) : <div className="text-sm text-muted">No evaluations recorded yet.</div>}
        </div>
      </Panel>
    </div>
  );
}
