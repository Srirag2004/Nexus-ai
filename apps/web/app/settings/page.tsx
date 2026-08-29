import { Panel } from "@/components/ui/panel";

export default function SettingsPage() {
  return (
    <Panel title="Settings" description="Environment-aware configuration visibility without exposing secrets.">
      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-2xl border border-border p-4">
          <div className="text-xs uppercase tracking-[0.2em] text-muted">API URL</div>
          <div className="mt-2 text-sm">{process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}</div>
        </div>
        <div className="rounded-2xl border border-border p-4">
          <div className="text-xs uppercase tracking-[0.2em] text-muted">Provider Mode</div>
          <div className="mt-2 text-sm">Configured on the backend through environment variables.</div>
        </div>
      </div>
    </Panel>
  );
}

