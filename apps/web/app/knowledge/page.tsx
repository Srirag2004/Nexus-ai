"use client";

import { useEffect, useState } from "react";

import { api } from "@/lib/api";
import { DocumentRecord } from "@/lib/types";
import { Panel } from "@/components/ui/panel";

export default function KnowledgePage() {
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);

  useEffect(() => {
    api.documents().then(setDocuments).catch(() => undefined);
  }, []);

  return (
    <Panel title="Knowledge" description="Uploaded documents, ingestion status, and retrieval-ready knowledge assets.">
      <div className="space-y-3">
        {documents.length ? documents.map((document) => (
          <div key={document.id} className="rounded-2xl border border-border px-4 py-3">
            <div className="font-medium">{document.filename}</div>
            <div className="text-sm text-muted">
              {document.content_type} / {document.status}
            </div>
          </div>
        )) : <div className="text-sm text-muted">No documents uploaded yet.</div>}
      </div>
    </Panel>
  );
}
