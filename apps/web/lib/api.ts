import {
  AgentRun,
  CareerAnalysis,
  Conversation,
  DocumentRecord,
  EvaluationRun,
  Message,
  MemoryRecord,
  ProjectRecord,
  RepositoryRecord,
} from "@/lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type SignedInUser = { id: string; email: string; display_name: string };

function sessionHeaders(): HeadersInit {
  const token = typeof window === "undefined" ? null : localStorage.getItem("nexus_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      ...sessionHeaders(),
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => null) as { detail?: string } | null;
    throw new Error(payload?.detail ?? `Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  oauthStartUrl: (provider: "google" | "github") => `${API_URL}/api/v1/auth/oauth/${provider}/start`,
  signUp: (email: string, password: string, display_name: string) => request<{ access_token: string; user: SignedInUser }>("/api/v1/auth/signup", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email, password, display_name }) }),
  signIn: (email: string, password: string) => request<{ access_token: string; user: SignedInUser }>("/api/v1/auth/signin", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email, password }) }),
  me: () => request<SignedInUser>("/api/v1/auth/me"),
  health: () => request<{ status: string; database: string }>("/health"),
  conversations: () => request<Conversation[]>("/api/v1/conversations"),
  conversation: (conversationId: string) => request<Conversation & { messages: Message[] }>(`/api/v1/conversations/${conversationId}`),
  deleteConversation: (conversationId: string) => request<void>(`/api/v1/conversations/${conversationId}`, { method: "DELETE" }),
  documents: () => request<DocumentRecord[]>("/api/v1/documents"),
  uploadDocument: async (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return request<DocumentRecord>("/api/v1/documents", { method: "POST", body: form });
  },
  askDocuments: (question: string) =>
    request<{ answer: string; sources: Array<Record<string, unknown>> }>("/api/v1/documents/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    }),
  memories: () => request<MemoryRecord[]>("/api/v1/memories"),
  repositories: () => request<RepositoryRecord[]>("/api/v1/github/repositories"),
  githubConnection: () => request<{ connected: boolean }>("/api/v1/github/connection"),
  availableGitHubRepositories: () => request<Array<{ id: number; name: string; full_name: string; url: string; private: boolean; description: string; updated_at: string }>>("/api/v1/github/available-repositories"),
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
  importGitHubRepository: (repository_url: string) =>
    request<RepositoryRecord>("/api/v1/github/import", {
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
  analyzeCareerUpload: (resume_text: string, job_description: string, resumeFile?: File | null, jobFile?: File | null) => {
    const form = new FormData();
    form.append("resume_text", resume_text);
    form.append("job_description", job_description);
    if (resumeFile) form.append("resume_file", resumeFile);
    if (jobFile) form.append("job_file", jobFile);
    return request<CareerAnalysis>("/api/v1/career/analyze-upload", { method: "POST", body: form });
  },
  projects: () => request<ProjectRecord[]>("/api/v1/projects"),
  createProject: (title: string, goal: string, description: string, repository_id: string | null, document_ids: string[]) =>
    request<ProjectRecord>("/api/v1/projects", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, goal, description, repository_id, document_ids }),
    }),
  generateProjectBrief: (projectId: string) => request<ProjectRecord>(`/api/v1/projects/${projectId}/generate`, { method: "POST" }),
  deleteProject: (projectId: string) => request<void>(`/api/v1/projects/${projectId}`, { method: "DELETE" }),
};
