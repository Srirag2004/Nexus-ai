"use client";

import { ChangeEvent, FormEvent, useEffect, useState } from "react";
import { FileText, LoaderCircle, Search, Sparkles, UploadCloud } from "lucide-react";

import { api } from "@/lib/api";
import { DocumentRecord } from "@/lib/types";
import { Panel } from "@/components/ui/panel";

export default function KnowledgePage() {
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState("");

  useEffect(() => { api.documents().then(setDocuments).catch(() => setNotice("Start the API to see your saved knowledge.")); }, []);

  async function upload(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    setBusy(true); setNotice("");
    try { const document = await api.uploadDocument(file); setDocuments((current) => [document, ...current]); setNotice(`${file.name} is ready to use.`); }
    catch { setNotice("Could not upload. Make sure the API is running, then try again."); }
    finally { setBusy(false); event.target.value = ""; }
  }

  async function ask(event: FormEvent) {
    event.preventDefault(); if (!question.trim()) return;
    setBusy(true); setAnswer("");
    try { setAnswer((await api.askDocuments(question)).answer); }
    catch { setAnswer("Nexus could not reach your knowledge base. Start the API and try again."); }
    finally { setBusy(false); }
  }

  return <div className="space-y-6 pb-8"><header className="px-1 pt-2"><p className="text-xs font-bold uppercase tracking-[0.22em] text-accent">Knowledge library</p><h1 className="mt-2 font-serif text-3xl font-bold tracking-tight">Make your material useful.</h1><p className="mt-2 max-w-2xl text-sm leading-6 text-muted">Upload the documents you actually rely on, then ask a plain-English question instead of digging through tabs.</p></header><div className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]"><Panel title="Add to Nexus" description="TXT, Markdown, and PDF files up to 10 MB."><label className="flex min-h-56 cursor-pointer flex-col items-center justify-center rounded-3xl border border-dashed border-accent/40 bg-accent/5 p-6 text-center transition hover:bg-accent/10"><input type="file" accept=".txt,.md,.pdf,text/plain,text/markdown,application/pdf" className="hidden" onChange={upload} disabled={busy} /><div className="grid h-12 w-12 place-items-center rounded-2xl bg-accent text-bg">{busy ? <LoaderCircle className="animate-spin" /> : <UploadCloud />}</div><div className="mt-4 font-semibold">Drop a file here or choose one</div><div className="mt-1 text-sm text-muted">Your material stays in your local workspace.</div></label>{notice && <p className="mt-4 rounded-xl bg-black/15 px-3 py-2 text-sm text-muted">{notice}</p>}</Panel><Panel title="Ask your library" description="Answers are grounded in your uploaded material."><form onSubmit={ask} className="flex gap-2"><input value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="What does the project brief say about launch timing?" className="min-w-0 flex-1 rounded-2xl border border-border bg-black/20 px-4 py-3 text-sm outline-none transition focus:border-accent/60" /><button disabled={busy || !question.trim()} className="grid h-11 w-11 place-items-center rounded-2xl bg-accent text-bg disabled:opacity-50"><Search size={18} /></button></form><div className="mt-5 min-h-36 rounded-2xl border border-border/70 bg-black/10 p-4 text-sm leading-6 text-text/85">{answer || <div className="flex gap-3 text-muted"><Sparkles size={17} className="mt-1 shrink-0 text-accent" />Add a document, then ask the question you usually lose time answering.</div>}</div></Panel></div><Panel title="Your library" description={`${documents.length} ${documents.length === 1 ? "document" : "documents"} ready for retrieval.`}>{documents.length ? <div className="grid gap-3 md:grid-cols-2">{documents.map((document) => <div key={document.id} className="flex items-center gap-3 rounded-2xl border border-border/70 bg-black/10 p-4"><div className="grid h-10 w-10 place-items-center rounded-xl bg-white/5 text-accent"><FileText size={18} /></div><div className="min-w-0"><div className="truncate font-medium">{document.filename}</div><div className="mt-1 text-xs text-muted">{document.status} · {new Date(document.created_at).toLocaleDateString()}</div></div></div>)}</div> : <div className="rounded-2xl border border-dashed border-border p-8 text-center text-sm text-muted">Your library is empty. Add a useful document above to begin.</div>}</Panel></div>;
}
