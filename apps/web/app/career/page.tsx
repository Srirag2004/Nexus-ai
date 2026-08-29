"use client";

import { FormEvent, useState } from "react";

import { api } from "@/lib/api";
import { CareerAnalysis } from "@/lib/types";
import { Panel } from "@/components/ui/panel";

export default function CareerPage() {
  const [resume, setResume] = useState("");
  const [job, setJob] = useState("");
  const [analysis, setAnalysis] = useState<CareerAnalysis | null>(null);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setAnalysis(await api.analyzeCareer(resume, job));
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
      <Panel title="Career Analysis" description="Compare a resume with a target role using project and memory context.">
        <form onSubmit={onSubmit} className="space-y-4">
          <textarea
            value={resume}
            onChange={(event) => setResume(event.target.value)}
            placeholder="Paste your resume text"
            className="min-h-48 w-full rounded-2xl border border-border bg-black/20 p-4 outline-none"
          />
          <textarea
            value={job}
            onChange={(event) => setJob(event.target.value)}
            placeholder="Paste the job description"
            className="min-h-48 w-full rounded-2xl border border-border bg-black/20 p-4 outline-none"
          />
          <button type="submit" className="rounded-2xl bg-accent px-4 py-3 font-medium text-slate-950">
            Analyze fit
          </button>
        </form>
      </Panel>
      <Panel title="Result">
        {analysis ? (
          <div className="space-y-4 text-sm">
            <div className="text-3xl font-semibold">{Math.round(analysis.match_score * 100)}%</div>
            <div className="text-muted">{analysis.heuristic}</div>
            <div>{analysis.summary}</div>
            <div>Matched: {analysis.matched_skills.join(", ") || "None"}</div>
            <div>Missing: {analysis.missing_skills.join(", ") || "None"}</div>
          </div>
        ) : (
          <div className="text-sm text-muted">Run an analysis to see the role fit summary.</div>
        )}
      </Panel>
    </div>
  );
}

