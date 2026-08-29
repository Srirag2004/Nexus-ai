"use client";

import { useEffect, useState } from "react";

import { api } from "@/lib/api";
import { MemoryRecord } from "@/lib/types";
import { Panel } from "@/components/ui/panel";

export default function MemoryPage() {
  const [memories, setMemories] = useState<MemoryRecord[]>([]);

  useEffect(() => {
    api.memories().then(setMemories).catch(() => undefined);
  }, []);

  return (
    <Panel title="Memory" description="Persisted user context that can be retrieved during future responses.">
      <div className="space-y-3">
        {memories.length ? memories.map((memory) => (
          <div key={memory.id} className="rounded-2xl border border-border p-4">
            <div className="text-xs uppercase tracking-[0.2em] text-muted">{memory.category}</div>
            <div className="mt-2">{memory.content}</div>
          </div>
        )) : <div className="text-sm text-muted">No memories stored yet.</div>}
      </div>
    </Panel>
  );
}
