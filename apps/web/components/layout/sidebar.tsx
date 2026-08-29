import Link from "next/link";

const links = [
  ["Dashboard", "/"],
  ["Chat", "/chat"],
  ["Knowledge", "/knowledge"],
  ["GitHub", "/github"],
  ["Career", "/career"],
  ["Memory", "/memory"],
  ["Agents", "/agents"],
  ["Settings", "/settings"],
];

export function Sidebar() {
  return (
    <aside className="w-full max-w-xs rounded-3xl border border-border bg-panel/90 p-6">
      <div className="mb-8">
        <div className="text-xs uppercase tracking-[0.3em] text-muted">NEXUS AI</div>
        <div className="mt-2 text-2xl font-semibold">Engineering Workspace</div>
      </div>
      <nav className="space-y-2">
        {links.map(([label, href]) => (
          <Link
            key={href}
            href={href}
            className="block rounded-2xl border border-transparent px-4 py-3 text-sm text-muted transition hover:border-border hover:bg-black/20 hover:text-text"
          >
            {label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}

