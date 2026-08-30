"use client";

import { FormEvent, useState } from "react";

import { api } from "@/lib/api";
import { CareerAnalysis } from "@/lib/types";
import { Panel } from "@/components/ui/panel";

export default function CareerPage() {
  const [resume, setResume] = useState("");
  const [job, setJob] = useState("");
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [jobFile, setJobFile] = useState<File | null>(null);
  const [analysis, setAnalysis] = useState<CareerAnalysis | null>(null);
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);
    try {
      const result = resumeFile || jobFile
        ? await api.analyzeCareerUpload(resume, job, resumeFile, jobFile)
        : await api.analyzeCareer(resume, job);
      setAnalysis(result);
    } catch (submissionError) {
      setError(submissionError instanceof Error ? submissionError.message : "Career analysis failed. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
      <Panel title="Career Analysis" description="Paste or upload your resume and a job description to compare them using your project and memory context.">
        <form onSubmit={onSubmit} className="space-y-4">
          <SourceInput
            label="Resume"
            value={resume}
            onChange={setResume}
            file={resumeFile}
            onFileChange={setResumeFile}
            placeholder="Paste your resume text, or upload a file below"
          />
          <SourceInput
            label="Job description"
            value={job}
            onChange={setJob}
            file={jobFile}
            onFileChange={setJobFile}
            placeholder="Paste the job description, or upload a file below"
          />
          {error ? <p className="rounded-xl border border-red-400/40 bg-red-500/10 p-3 text-sm text-red-200">{error}</p> : null}
          <button disabled={isSubmitting} type="submit" className="rounded-2xl bg-accent px-4 py-3 font-medium text-slate-950 disabled:cursor-not-allowed disabled:opacity-60">
            {isSubmitting ? "Comparing..." : "Compare resume and role"}
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

function SourceInput({
  label,
  value,
  onChange,
  file,
  onFileChange,
  placeholder,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  file: File | null;
  onFileChange: (file: File | null) => void;
  placeholder: string;
}) {
  return (
    <fieldset className="space-y-2 rounded-2xl border border-border bg-black/10 p-3">
      <legend className="px-1 text-sm font-medium">{label}</legend>
      <textarea
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        className="min-h-36 w-full rounded-xl border border-border bg-black/20 p-3 outline-none"
      />
      <label className="flex cursor-pointer items-center justify-between gap-3 rounded-xl border border-dashed border-border px-3 py-2 text-sm text-muted">
        <span>{file ? file.name : "Upload PDF, Word (.docx), TXT, or Markdown"}</span>
        <span className="text-accent">Choose file</span>
        <input
          type="file"
          accept=".pdf,.docx,.txt,.md,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain,text/markdown"
          className="sr-only"
          onChange={(event) => onFileChange(event.target.files?.[0] ?? null)}
        />
      </label>
      {file ? <button type="button" onClick={() => onFileChange(null)} className="text-xs text-muted underline">Remove selected file</button> : null}
    </fieldset>
  );
}
