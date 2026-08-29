"use client";

import { FormEvent, useEffect, useState } from "react";
import { ArrowUp, Bot, History, LoaderCircle, MessageSquarePlus, MoreHorizontal, Sparkles, Trash2, UserRound } from "lucide-react";

import { api } from "@/lib/api";
import { Conversation, Message } from "@/lib/types";

type Turn = Pick<Message, "role" | "content">;
const prompts = ["Help me turn a rough idea into a plan", "What should I learn next for an AI engineering role?", "Review the risks in this product decision"];

function formatDate(value: string) {
  const date = new Date(value);
  return date.toDateString() === new Date().toDateString() ? "Today" : date.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

export default function ChatPage() {
  const [message, setMessage] = useState("");
  const [turns, setTurns] = useState<Turn[]>([]);
  const [history, setHistory] = useState<Conversation[]>([]);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [loading, setLoading] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [error, setError] = useState("");

  async function loadHistory() {
    try { setHistory(await api.conversations()); } catch { setError("Your conversation history could not be loaded."); } finally { setLoadingHistory(false); }
  }
  useEffect(() => { void loadHistory(); }, []);

  function newChat() { setConversationId(undefined); setTurns([]); setMessage(""); setError(""); }
  async function openChat(id: string) {
    setLoading(true); setError("");
    try { const chat = await api.conversation(id); setConversationId(chat.id); setTurns(chat.messages); }
    catch { setError("That conversation could not be opened."); }
    finally { setLoading(false); }
  }
  async function removeChat(event: React.SyntheticEvent, id: string) {
    event.stopPropagation();
    try { await api.deleteConversation(id); if (conversationId === id) newChat(); await loadHistory(); }
    catch { setError("That conversation could not be deleted."); }
  }
  async function send(event?: FormEvent) {
    event?.preventDefault(); const prompt = message.trim(); if (!prompt || loading) return;
    setTurns((current) => [...current, { role: "user", content: prompt }]); setMessage(""); setError(""); setLoading(true);
    try { const result = await api.chat(prompt, conversationId); setConversationId(result.conversation_id); setTurns((current) => [...current, { role: "assistant", content: result.reply.content }]); await loadHistory(); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Nexus could not send that message."); }
    finally { setLoading(false); }
  }

  return <div className="mx-auto flex min-h-[calc(100vh-3rem)] max-w-6xl flex-col pb-3"><header className="flex items-center justify-between px-1 py-4"><div><p className="text-xs font-bold uppercase tracking-[0.22em] text-accent">Nexus conversation</p><h1 className="mt-1 font-serif text-3xl font-bold tracking-tight">Think out loud.</h1></div><div className="hidden items-center gap-2 rounded-full border border-border bg-panel/80 px-3 py-2 text-xs text-muted sm:flex"><Sparkles size={14} className="text-accent" />Your private workspace</div></header><div className="grid flex-1 gap-4 lg:grid-cols-[15.5rem_1fr]"><aside className="panel-glow flex min-h-0 flex-col rounded-[1.75rem] border border-border/80 bg-panel/85 p-3"><button onClick={newChat} className="flex items-center justify-center gap-2 rounded-2xl bg-accent px-3 py-3 text-sm font-bold text-bg transition hover:bg-[#d2ff91]"><MessageSquarePlus size={17} />New chat</button><div className="mt-5 flex items-center gap-2 px-2 text-xs font-bold uppercase tracking-[0.15em] text-muted"><History size={14} />History</div><div className="mt-2 flex max-h-48 gap-1 overflow-x-auto pb-1 lg:max-h-none lg:flex-1 lg:flex-col lg:overflow-y-auto lg:overflow-x-hidden">{loadingHistory ? <div className="flex items-center gap-2 px-2 py-3 text-sm text-muted"><LoaderCircle size={15} className="animate-spin" />Loading</div> : history.length ? history.map((item) => <button key={item.id} onClick={() => void openChat(item.id)} className={`group flex min-w-48 items-center gap-2 rounded-xl px-3 py-2.5 text-left transition lg:min-w-0 ${conversationId === item.id ? "bg-white/10 text-text" : "text-muted hover:bg-white/5 hover:text-text"}`}><Bot size={15} className="shrink-0 text-accent" /><span className="min-w-0 flex-1"><span className="block truncate text-sm font-medium">{item.title}</span><span className="mt-0.5 block text-[11px] text-muted">{formatDate(item.updated_at)}</span></span><span className="relative grid h-6 w-6 place-items-center"><MoreHorizontal size={16} className="group-hover:hidden" /><Trash2 onClick={(event) => void removeChat(event, item.id)} size={14} className="hidden text-red-300 group-hover:block" /></span></button>) : <p className="px-2 py-3 text-sm leading-5 text-muted">Your saved conversations will appear here.</p>}</div></aside><section className="panel-glow flex min-h-[620px] flex-col rounded-[2rem] border border-border/80 bg-panel/85 p-4 md:p-6"><div className="flex-1 space-y-5">{turns.length === 0 ? <div className="flex min-h-[420px] flex-col items-center justify-center text-center"><div className="grid h-14 w-14 place-items-center rounded-2xl bg-accent text-bg"><Bot size={25} /></div><h2 className="mt-5 font-serif text-2xl font-bold">Where should we begin?</h2><p className="mt-2 max-w-md text-sm leading-6 text-muted">Ask a question, unpack a decision, or bring in a goal. Every conversation is saved privately to your workspace.</p><div className="mt-7 flex max-w-xl flex-wrap justify-center gap-2">{prompts.map((prompt) => <button key={prompt} onClick={() => setMessage(prompt)} className="rounded-full border border-border bg-black/10 px-3 py-2 text-xs text-muted transition hover:border-accent/50 hover:text-text">{prompt}</button>)}</div></div> : turns.map((turn, index) => <div key={`${turn.role}-${index}`} className={`flex gap-3 ${turn.role === "user" ? "justify-end" : ""}`}><div className={`grid h-8 w-8 shrink-0 place-items-center rounded-xl ${turn.role === "assistant" ? "bg-accent text-bg" : "order-2 bg-white/10 text-text"}`}>{turn.role === "assistant" ? <Bot size={16} /> : <UserRound size={15} />}</div><div className={`max-w-[80%] whitespace-pre-wrap rounded-2xl px-4 py-3 text-sm leading-6 ${turn.role === "assistant" ? "rounded-tl-sm bg-black/15 text-text/90" : "order-1 rounded-tr-sm bg-accent text-bg"}`}>{turn.content}</div></div>)}{loading && <div className="flex items-center gap-3 text-sm text-muted"><div className="grid h-8 w-8 place-items-center rounded-xl bg-accent text-bg"><Bot size={16} /></div><span className="animate-pulse">Nexus is thinking...</span></div>}</div>{error && <div className="mt-4 rounded-xl border border-amber-300/20 bg-amber-200/10 px-3 py-2 text-sm text-amber-100">{error}</div>}<form onSubmit={send} className="mt-5 flex items-end gap-3 rounded-[1.5rem] border border-border bg-black/15 p-2"><textarea value={message} onChange={(event) => setMessage(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); void send(); } }} placeholder="Message Nexus..." rows={2} className="min-h-[48px] flex-1 resize-none bg-transparent px-3 py-2 text-sm outline-none placeholder:text-muted" /><button type="submit" disabled={!message.trim() || loading} className="grid h-11 w-11 shrink-0 place-items-center rounded-2xl bg-accent text-bg transition hover:bg-[#d2ff91] disabled:opacity-40"><ArrowUp size={19} /></button></form><p className="mt-3 text-center text-[11px] text-muted">Enter to send · Shift + Enter for a new line</p></section></div></div>;
}
