import {
  AgentRun,
  CareerAnalysis,
  Conversation,
  DocumentRecord,
  EvaluationRun,
  MemoryRecord,
  RepositoryRecord,
} from "@/lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  health: () => request<{ status: string; database: string }>("/health"),
  conversations: () => request<Conversation[]>("/api/v1/conversations"),
  documents: () => request<DocumentRecord[]>("/api/v1/documents"),
  memories: () => request<MemoryRecord[]>("/api/v1/memories"),
  repositories: () => request<RepositoryRecord[]>("/api/v1/github/repositories"),
  agentRuns: () => request<AgentRun[]>("/api/v1/agents/runs"),
  evaluations: () => request<EvaluationRun[]>("/api/v1/evaluations"),
  chat: (message: string, conversation_id?: string) =>
    request<{
      conversation_id: string;
      provider: string;
      reply: { content: string; role: string; id: string; created_at: string; sources: Array<Record<string, unknown>> };
      citations: Array<Record<string, unknown>>;
    }>("/api/v1/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, conversation_id }),
    }),
  analyzeRepository: (repository_url: string) =>
    request<RepositoryRecord>("/api/v1/github/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ repository_url }),
    }),
  analyzeCareer: (resume_text: string, job_description: string) =>
    request<CareerAnalysis>("/api/v1/career/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ resume_text, job_description }),
    }),
};

