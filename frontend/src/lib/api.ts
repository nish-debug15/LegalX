/**
 * LegalX API Client — typed fetch wrapper for all backend endpoints.
 *
 * Base URL comes from NEXT_PUBLIC_API_URL env var (defaults to http://localhost:8000).
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/* ─── Types ─── */

export interface TopicListItem {
  id: string;
  name: string;
  description: string | null;
}

export interface TopicDetail {
  id: string;
  name: string;
  description: string | null;
  summary: string | null;
  key_info: {
    key_rights?: string[];
    important_provisions?: string[];
    penalties?: string[];
    who_can_benefit?: string[];
  } | null;
  created_at: string;
  updated_at: string;
}

export interface ChatResponse {
  answer: string;
  sources: string[] | null;
}

export interface ChatMessage {
  id: string;
  session_id: string;
  topic_id: string;
  role: "user" | "assistant";
  content: string;
  sources: string[] | null;
  created_at: string;
}

export interface AudioResponse {
  topic_id: string;
  audio_url: string;
}

export interface IngestResponse {
  status: string;
  topics_processed: string[];
  message: string;
}

/* ─── API Functions ─── */

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API error ${res.status}: ${body}`);
  }

  return res.json();
}

/** GET /api/topics — list all ingested topics */
export async function fetchTopics(): Promise<TopicListItem[]> {
  return apiFetch<TopicListItem[]>("/api/topics/");
}

/** GET /api/topics/:id — get full topic detail with summary + key_info */
export async function fetchTopicDetail(topicId: string): Promise<TopicDetail> {
  return apiFetch<TopicDetail>(`/api/topics/${topicId}`);
}

/** POST /api/chat — send a question for RAG Q&A */
export async function sendChatMessage(
  topicId: string,
  question: string,
  sessionId: string
): Promise<ChatResponse> {
  return apiFetch<ChatResponse>("/api/chat/", {
    method: "POST",
    body: JSON.stringify({
      topic_id: topicId,
      question,
      session_id: sessionId,
    }),
  });
}

/** GET /api/chat/history/:sessionId/:topicId — get chat history */
export async function fetchChatHistory(
  sessionId: string,
  topicId: string
): Promise<ChatMessage[]> {
  return apiFetch<ChatMessage[]>(`/api/chat/history/${sessionId}/${topicId}`);
}

/** POST /api/audio/:topicId — generate audio (if not cached) */
export async function generateAudio(topicId: string): Promise<AudioResponse> {
  return apiFetch<AudioResponse>(`/api/audio/${topicId}`, { method: "POST" });
}

/** GET /api/audio/:topicId — get audio status */
export async function getAudioStatus(topicId: string): Promise<AudioResponse> {
  return apiFetch<AudioResponse>(`/api/audio/${topicId}`);
}

/** POST /api/ingest — trigger full ingestion pipeline */
export async function triggerIngestion(): Promise<IngestResponse> {
  return apiFetch<IngestResponse>("/api/ingest", { method: "POST" });
}

/** Build a full audio URL from the relative path */
export function getAudioUrl(relativePath: string): string {
  return `${API_BASE}${relativePath}`;
}
