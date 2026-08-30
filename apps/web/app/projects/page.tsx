"use client";

import { FormEvent, useEffect, useState } from "react";
import { ArrowRight, FileText, Github, Sparkles } from "lucide-react";

import { Panel } from "@/components/ui/panel";
import { api } from "@/lib/api";
import { DocumentRecord, ProjectRecord, RepositoryRecord } from "@/lib/types";

export default function ProjectsPage() {
  const [projects, setProjects] = useState<ProjectRecord[]>([]);
  const [repositories, setRepositories] = useState<RepositoryRecord[]>([]);
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [title, setTitle] = useState("");
  const [goal, setGoal] = useState("");
  const [description, setDescription] = useState("");
  const [repositoryId, setRepositoryId] = useState("");
  const [documentIds, setDocumentIds] = useState<string[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([api.projects(), api.repositories(), api.documents()])
      .then(([projectItems, repositoryItems, documentItems]) => {
        setProjects(projectItems);
        setRepositories(repositoryItems);
        setDocuments(documentItems);
        setSelectedId(projectItems[0]?.id ?? null);
      })
      .catch(() => setError("Could not load your project context. Refresh and try again."));
  }, []);

  const selectedProject = projects.find((project) => project.id === selectedId) ?? null;

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      const project = await api.createProject(title, goal, description, repositoryId || null, documentIds);
      setProjects((current) => [project, ...current]);
      setSelectedId(project.id);
      setTitle("");
      setGoal("");
      setDescription("");
      setRepositoryId("");
      setDocumentIds([]);
    } catch (submissionError) {
      setError(submissionError instanceof Error ? submissionError.message : "Could not create the project.");
    } finally {
      setLoading(false);
    }
  }

  async function generateBrief() {
    if (!selectedProject) return;
    setError("");
    setLoading(true);
    try {
      const refreshed = await api.generateProjectBrief(selectedProject.id);
      setProjects((current) => current.map((project) => project.id === refreshed.id ? refreshed : project));
    } catch (generationError) {
      setError(generationError instanceof Error ? generationError.message : "Could not generate the project brief.");
    } finally {
      setLoading(false);
    }
  }

  async function deleteProject() {
    if (!selectedProject || !window.confirm(`Delete ${selectedProject.title}?`)) return;
    await api.deleteProject(selectedProject.id);
    setProjects((current) => current.filter((project) => project.id !== selectedProject.id));
    setSelectedId(null);
  }

  function toggleDocument(id: string) {
    setDocumentIds((current) => current.includes(id) ? current.filter((item) => item !== id) : [...current, id]);
  }

  return (
    <div className="space-y-6 pb-8">
      <header className="px-1 pt-2">
        <p className="text-xs font-bold uppercase tracking-[0.22em] text-accent">Project intelligence</p>
        <h1 className="mt-2 font-serif text-3xl font-bold tracking-tight md:text-4xl">Turn context into momentum.</h1>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-muted">Build a workspace around one outcome. Link a repository and knowledge files, then let NEXUS create a focused brief, risks, milestones, and next actions.</p>
      </header>

      <div className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
        <Panel title="Create a project" description="Start with a goal. Context is optional, but makes the brief more useful.">
          <form onSubmit={onSubmit} className="space-y-4">
            <input value={title} onChange={(event) => setTitle(event.target.value)} required minLength={2} placeholder="Project name, e.g. AI internship portfolio" className="w-full rounded-2xl border border-border bg-black/20 px-4 py-3 outline-none" />
            <textarea value={goal} onChange={(event) => setGoal(event.target.value)} required minLength={5} placeholder="What outcome do you want to achieve?" className="min-h-28 w-full rounded-2xl border border-border bg-black/20 p-4 outline-none" />
            <textarea value={description} onChange={(event) => setDescription(event.target.value)} placeholder="Optional notes, deadline, or constraints" className="min-h-20 w-full rounded-2xl border border-border bg-black/20 p-4 outline-none" />
            <label className="block text-sm font-medium">Linked repository
              <select value={repositoryId} onChange={(event) => setRepositoryId(event.target.value)} className="mt-2 w-full rounded-2xl border border-border bg-black/20 px-4 py-3 text-sm outline-none">
                <option value="">No repository yet</option>
                {repositories.map((repository) => <option key={repository.id} value={repository.id}>{repository.owner}/{repository.name}</option>)}
              </select>
            </label>
            <fieldset className="rounded-2xl border border-border bg-black/10 p-3">
              <legend className="px-1 text-sm font-medium">Knowledge files</legend>
              {documents.length ? <div className="mt-2 space-y-2">{documents.map((document) => <label key={document.id} className="flex cursor-pointer items-center gap-3 rounded-xl px-2 py-1.5 text-sm text-muted hover:bg-white/5"><input type="checkbox" checked={documentIds.includes(document.id)} onChange={() => toggleDocument(document.id)} /><FileText size={15} />{document.filename}</label>)}</div> : <p className="mt-2 text-sm text-muted">Upload files in Knowledge first, then attach them here.</p>}
            </fieldset>
            {error ? <p className="rounded-xl border border-red-400/40 bg-red-500/10 p-3 text-sm text-red-200">{error}</p> : null}
            <button disabled={loading} type="submit" className="inline-flex items-center gap-2 rounded-2xl bg-accent px-4 py-3 font-medium text-slate-950 disabled:opacity-60"><Sparkles size={16} />{loading ? "Creating..." : "Create project"}</button>
          </form>
        </Panel>

        <Panel title="Your projects" description="Select a workspace and turn its context into an execution plan.">
          {projects.length ? <div className="grid gap-3 sm:grid-cols-2">{projects.map((project) => <button key={project.id} onClick={() => setSelectedId(project.id)} className={`rounded-2xl border p-4 text-left transition ${project.id === selectedId ? "border-accent/60 bg-accent/10" : "border-border bg-black/10 hover:border-accent/30"}`}><div className="flex items-start justify-between gap-3"><div className="font-medium">{project.title}</div><span className="rounded-full border border-border px-2 py-0.5 text-[10px] uppercase tracking-wide text-muted">{project.status}</span></div><p className="mt-2 line-clamp-2 text-sm leading-5 text-muted">{project.goal}</p><div className="mt-4 flex flex-wrap gap-2 text-xs text-muted">{project.repository_name ? <span className="inline-flex items-center gap-1"><Github size={13} />{project.repository_name}</span> : null}{project.document_names.length ? <span>{project.document_names.length} file{project.document_names.length === 1 ? "" : "s"}</span> : null}</div></button>)}</div> : <div className="rounded-2xl border border-dashed border-border p-8 text-center text-sm text-muted">Create your first project workspace to give NEXUS something meaningful to organize.</div>}
        </Panel>
      </div>

      {selectedProject ? <ProjectBrief project={selectedProject} loading={loading} onGenerate={generateBrief} onDelete={deleteProject} /> : null}
    </div>
  );
}

function ProjectBrief({ project, loading, onGenerate, onDelete }: { project: ProjectRecord; loading: boolean; onGenerate: () => void; onDelete: () => void }) {
  const hasBrief = Boolean(project.brief);
  return (
    <section className="panel-glow rounded-[2rem] border border-border bg-panel/80 p-5 md:p-7">
      <div className="flex flex-wrap items-start justify-between gap-4"><div><p className="text-xs font-bold uppercase tracking-[0.18em] text-accent">{project.status}</p><h2 className="mt-2 font-serif text-2xl font-bold">{project.title}</h2><p className="mt-2 max-w-3xl text-sm leading-6 text-muted">{project.goal}</p></div><div className="flex gap-2"><button disabled={loading} onClick={onGenerate} className="inline-flex items-center gap-2 rounded-2xl bg-accent px-4 py-3 text-sm font-medium text-slate-950 disabled:opacity-60"><Sparkles size={16} />{hasBrief ? "Refresh brief" : "Generate brief"}</button><button onClick={onDelete} className="rounded-2xl border border-border px-4 py-3 text-sm text-muted hover:text-red-200">Delete</button></div></div>
      {hasBrief ? <div className="mt-7 space-y-6"><div className="rounded-2xl border border-accent/20 bg-accent/10 p-5"><h3 className="text-sm font-semibold uppercase tracking-[0.16em] text-accent">AI project brief</h3><p className="mt-3 whitespace-pre-line leading-7 text-text/90">{project.brief}</p></div><div className="grid gap-4 lg:grid-cols-3"><BriefList title="Milestones" items={project.milestones} tone="border-sky-400/25 bg-sky-400/10" /><BriefList title="Risks to manage" items={project.risks} tone="border-amber-400/25 bg-amber-400/10" /><BriefList title="Next actions" items={project.next_steps} tone="border-emerald-400/25 bg-emerald-400/10" /></div></div> : <div className="mt-7 rounded-2xl border border-dashed border-border p-6 text-sm text-muted">Your project is saved. Select <strong className="text-text">Generate brief</strong> to combine its goal, notes, repository, and knowledge files into an execution view.</div>}
    </section>
  );
}

function BriefList({ title, items, tone }: { title: string; items: string[]; tone: string }) {
  return <div className={`rounded-2xl border p-4 ${tone}`}><h3 className="font-medium">{title}</h3><ol className="mt-3 space-y-3 text-sm leading-5 text-text/80">{items.map((item, index) => <li key={item} className="flex gap-2"><span className="font-medium text-accent">{index + 1}.</span>{item}</li>)}</ol></div>;
}
