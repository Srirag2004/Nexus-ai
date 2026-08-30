"use client";

import Link from "next/link";
import { ArrowRight, BookOpen, CircleCheck, FolderKanban, Github, MessageSquareText, Plus, Sparkles } from "lucide-react";
import { useEffect, useState } from "react";

import { api } from "@/lib/api";

type WorkspaceState = { conversations: number; documents: number; repositories: number; projects: number; online: boolean };

const quickStarts = [
  { title: "Ask anything", text: "Get help connecting your ideas, code, and context.", href: "/chat", icon: MessageSquareText },
  { title: "Build your library", text: "Add notes, specs, PDFs, and docs you want to use later.", href: "/knowledge", icon: BookOpen },
  { title: "Understand a repository", text: "Turn a GitHub URL into a concise engineering brief.", href: "/github", icon: Github },
  { title: "Move a project forward", text: "Build an execution brief from a goal, repository, and knowledge files.", href: "/projects", icon: FolderKanban },
];

export default function DashboardPage() {
  const [workspace, setWorkspace] = useState<WorkspaceState>({ conversations: 0, documents: 0, repositories: 0, projects: 0, online: false });

  useEffect(() => {
    Promise.all([api.health(), api.conversations(), api.documents(), api.repositories(), api.projects()])
      .then(([health, conversations, documents, repositories, projects]) => setWorkspace({ conversations: conversations.length, documents: documents.length, repositories: repositories.length, projects: projects.length, online: health.status === "ok" }))
      .catch(() => setWorkspace((current) => ({ ...current, online: false })));
  }, []);

  return (
    <div className="space-y-6 pb-8">
      <header className="flex flex-wrap items-center justify-between gap-4 px-1 pt-2">
        <div><p className="text-xs font-bold uppercase tracking-[0.22em] text-accent">Personal intelligence system</p><h1 className="mt-2 font-serif text-3xl font-bold tracking-tight md:text-4xl">Welcome to your thinking space.</h1></div>
        <div className={`flex items-center gap-2 rounded-full border px-3 py-2 text-xs font-semibold ${workspace.online ? "border-accent/35 bg-accent/10 text-accent" : "border-border bg-black/10 text-muted"}`}><span className={`h-2 w-2 rounded-full ${workspace.online ? "bg-accent" : "bg-muted"}`} />{workspace.online ? "Nexus is ready" : "Connect the API to begin"}</div>
      </header>

      <section className="panel-glow relative overflow-hidden rounded-[2rem] border border-accent/20 bg-[#173442] p-6 md:p-9">
        <div className="absolute -right-12 -top-16 h-56 w-56 rounded-full bg-accent/15 blur-3xl" />
        <div className="relative max-w-2xl"><div className="mb-5 grid h-11 w-11 place-items-center rounded-2xl bg-accent text-bg"><Sparkles size={21} /></div><p className="text-sm font-medium text-accent">Start with a single thought</p><h2 className="mt-2 font-serif text-3xl font-bold leading-tight tracking-tight md:text-5xl">What do you want to move forward today?</h2><p className="mt-4 max-w-xl text-sm leading-6 text-text/75 md:text-base">Nexus brings your documents, projects, and career goals into one calm place so you can get from question to next step faster.</p><Link href="/chat" className="mt-7 inline-flex items-center gap-2 rounded-2xl bg-accent px-5 py-3 text-sm font-bold text-bg transition hover:-translate-y-0.5 hover:bg-[#d2ff91]">Open a new conversation <ArrowRight size={16} /></Link></div>
      </section>

      <section><div className="mb-3 flex items-center justify-between px-1"><h2 className="font-serif text-xl font-bold">Choose a starting point</h2><span className="text-xs text-muted">You can return here anytime</span></div><div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">{quickStarts.map(({ title, text, href, icon: Icon }) => <Link key={href} href={href} className="group panel-glow rounded-[1.5rem] border border-border/80 bg-panel/80 p-5 transition hover:-translate-y-1 hover:border-accent/40"><div className="flex items-start justify-between"><div className="grid h-10 w-10 place-items-center rounded-2xl bg-white/5 text-accent"><Icon size={19} /></div><ArrowRight size={17} className="text-muted transition group-hover:translate-x-1 group-hover:text-accent" /></div><h3 className="mt-7 font-serif text-lg font-bold">{title}</h3><p className="mt-2 text-sm leading-5 text-muted">{text}</p></Link>)}</div></section>

      <section className="grid gap-4 md:grid-cols-[1.4fr_0.8fr]"><div className="panel-glow rounded-[1.5rem] border border-border/80 bg-panel/80 p-5"><div className="flex items-center justify-between"><div><p className="text-xs font-bold uppercase tracking-[0.16em] text-muted">Workspace pulse</p><h2 className="mt-1 font-serif text-xl font-bold">Everything in one view</h2></div><CircleCheck size={20} className="text-accent" /></div><div className="mt-5 grid grid-cols-2 gap-3 md:grid-cols-4">{[["Conversations", workspace.conversations], ["Knowledge", workspace.documents], ["Repositories", workspace.repositories], ["Projects", workspace.projects]].map(([label, value]) => <div key={String(label)} className="rounded-2xl bg-black/15 p-4"><div className="font-serif text-3xl font-bold">{value}</div><div className="mt-1 text-xs text-muted">{label}</div></div>)}</div></div><Link href="/projects" className="panel-glow flex min-h-44 flex-col justify-between rounded-[1.5rem] border border-border/80 bg-[#17303a] p-5 transition hover:border-accent/40"><Plus size={20} className="text-accent" /><div><h2 className="font-serif text-xl font-bold">Start a project</h2><p className="mt-1 text-sm leading-5 text-muted">Turn a goal into focused, visible progress.</p></div></Link></section>
    </div>
  );
}
