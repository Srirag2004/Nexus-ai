"use client";

import { FormEvent, ReactNode, useEffect, useState } from "react";
import { ArrowRight, Sparkles } from "lucide-react";

import { api } from "@/lib/api";

export function AuthGate({ children }: { children: ReactNode }) {
  const [ready, setReady] = useState(false);
  const [signedIn, setSignedIn] = useState(false);
  const [register, setRegister] = useState(false);
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => { api.me().then(() => setSignedIn(true)).catch(() => localStorage.removeItem("nexus_token")).finally(() => setReady(true)); }, []);
  async function submit(event: FormEvent) { event.preventDefault(); setLoading(true); setError(""); try { const response = register ? await api.signUp(email, password, name) : await api.signIn(email, password); localStorage.setItem("nexus_token", response.access_token); setSignedIn(true); } catch (reason) { setError(reason instanceof Error ? reason.message : "We could not sign you in. Please try again."); } finally { setLoading(false); } }
  if (!ready) return <div className="grid min-h-screen place-items-center text-sm text-muted">Opening your workspace…</div>;
  if (signedIn) return <>{children}</>;
  return <main className="mesh grid min-h-screen place-items-center p-5"><section className="panel-glow w-full max-w-md rounded-[2rem] border border-border bg-panel/95 p-7"><div className="grid h-12 w-12 place-items-center rounded-2xl bg-accent text-bg"><Sparkles /></div><p className="mt-6 text-xs font-bold uppercase tracking-[0.2em] text-accent">Nexus AI workbench</p><h1 className="mt-2 font-serif text-3xl font-bold">Your context, kept yours.</h1><p className="mt-3 text-sm leading-6 text-muted">Sign in to keep conversations, knowledge, and project work private to your account.</p><form onSubmit={submit} className="mt-7 space-y-3">{register && <input value={name} onChange={(event) => setName(event.target.value)} placeholder="Your name" required className="w-full rounded-2xl border border-border bg-black/15 px-4 py-3 text-sm outline-none focus:border-accent" />}<input value={email} onChange={(event) => setEmail(event.target.value)} type="email" placeholder="you@example.com" required className="w-full rounded-2xl border border-border bg-black/15 px-4 py-3 text-sm outline-none focus:border-accent" /><input value={password} onChange={(event) => setPassword(event.target.value)} type="password" minLength={8} placeholder="Password (at least 8 characters)" required className="w-full rounded-2xl border border-border bg-black/15 px-4 py-3 text-sm outline-none focus:border-accent" />{error && <p className="text-sm text-red-300">{error}</p>}<button disabled={loading} className="flex w-full items-center justify-center gap-2 rounded-2xl bg-accent px-4 py-3 font-bold text-bg disabled:opacity-50">{loading ? "Please wait…" : register ? "Create my workspace" : "Sign in"}<ArrowRight size={16} /></button></form><button onClick={() => { setRegister(!register); setError(""); }} className="mt-5 text-sm text-muted underline underline-offset-4 hover:text-text">{register ? "Already have an account? Sign in" : "New here? Create an account"}</button></section></main>;
}
