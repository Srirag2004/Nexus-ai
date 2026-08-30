export type Message = {
  id: string;
  role: string;
  content: string;
  created_at: string;
  sources: Array<Record<string, unknown>>;
};

export type Conversation = {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
};

export type DocumentRecord = {
  id: string;
  filename: string;
  content_type: string;
  status: string;
  created_at: string;
  metadata: Record<string, unknown>;
};

export type MemoryRecord = {
  id: string;
  category: string;
  content: string;
  importance: number;
  created_at: string;
  last_used_at?: string | null;
};

export type RepositoryAnalysis = {
  id: string;
  summary: string;
  architecture: string;
  strengths: string[];
  issues: string[];
  recommendations: string[];
  created_at: string;
};

export type RepositoryRecord = {
  id: string;
  owner: string;
  name: string;
  url: string;
  languages: Record<string, number>;
  created_at: string;
  latest_analysis?: RepositoryAnalysis | null;
};

export type CareerAnalysis = {
  id: string;
  match_score: number;
  matched_skills: string[];
  missing_skills: string[];
  recommendations: string[];
  summary: string;
  skills_considered: number;
  score_label: string;
  score_explanation: string;
  created_at: string;
  heuristic: string;
};

export type AgentRun = {
  id: string;
  agent_name: string;
  status: string;
  input_summary: string;
  output_summary: string;
  duration_ms: number;
  created_at: string;
};

export type EvaluationRun = {
  id: string;
  evaluation_type: string;
  status: string;
  metrics: Record<string, number>;
  created_at: string;
};
