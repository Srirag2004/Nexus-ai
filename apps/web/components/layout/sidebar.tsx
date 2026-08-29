"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Bot, BrainCircuit, BriefcaseBusiness, Github, LayoutDashboard, LibraryBig, LucideIcon, MessageSquareText, Settings, Sparkles } from "lucide-react";

const links: Array<[string, string, LucideIcon]> = [
  ["Dashboard", "/", LayoutDashboard], ["Ask Nexus", "/chat", MessageSquareText],
  ["Knowledge", "/knowledge", LibraryBig], ["GitHub", "/github", Github],
  ["Career", "/career", BriefcaseBusiness], ["Memory", "/memory", BrainCircuit],
  ["Agents", "/agents", Bot], ["Settings", "/settings", Settings],
];

export function Sidebar() {
  const pathname = usePathname();
  return (
    <aside className="panel-glow w-full rounded-[1.75rem] border border-border/80 bg-panel/85 p-4 backdrop-blur-md lg:sticky lg:top-6 lg:flex lg:h-[calc(100vh-3rem)] lg:max-w-[17rem] lg:flex-col lg:p-5">
      <div className="mb-5 flex items-center gap-3 px-2 pt-1">
        <div className="grid h-10 w-10 place-items-center rounded-2xl bg-accent text-bg shadow-lg shadow-accent/10"><Sparkles size={19} /></div>
        <div><div className="font-serif text-xl font-bold tracking-tight">nexus</div><div className="text-[10px] font-bold uppercase tracking-[0.2em] text-muted">AI workbench</div></div>
      </div>
      <nav className="grid grid-cols-2 gap-1 sm:grid-cols-4 lg:block lg:shrink-0 lg:space-y-1">
        {links.map(([label, href, Icon]) => {
          const active = pathname === href;
          return <Link key={href} href={href} className={`flex items-center gap-3 rounded-2xl px-3 py-2.5 text-sm font-medium transition ${active ? "bg-accent text-bg shadow-lg shadow-accent/10" : "text-muted hover:bg-white/5 hover:text-text"}`}><Icon size={17} strokeWidth={1.8} />{label}</Link>;
        })}
      </nav>
      <div className="mt-6 hidden rounded-2xl border border-border/70 bg-black/10 p-4 lg:mt-auto lg:block [@media(max-height:850px)]:hidden"><div className="text-xs font-bold uppercase tracking-[0.16em] text-muted">Your workspace</div><p className="mt-2 text-sm leading-5 text-text/80">Bring in a project, a document, or a question. Nexus connects the dots.</p></div>
    </aside>
  );
}
