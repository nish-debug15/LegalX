"use client";

import { useEffect, useState, useRef, useCallback } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  fetchTopicDetail,
  sendChatMessage,
  generateAudio,
  getAudioUrl,
  TopicDetail,
} from "@/lib/api";
import { getTopicMeta } from "@/lib/topics";
import { v4 as uuidv4 } from "uuid";

/* ─── Types ─── */
interface ChatMsg {
  role: "user" | "assistant";
  content: string;
  sources?: string[] | null;
}

type Tab = "summary" | "keyinfo" | "ask" | "audio";

/* ─── Component ─── */
export default function TopicPage() {
  const params = useParams();
  const topicId = params.topicId as string;

  const [topic, setTopic] = useState<TopicDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<Tab>("summary");

  // Chat
  const [messages, setMessages] = useState<ChatMsg[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const [sessionId] = useState(() => uuidv4());
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Audio
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [audioLoading, setAudioLoading] = useState(false);
  const [audioError, setAudioError] = useState<string | null>(null);

  const meta = getTopicMeta(topicId);

  /* Fetch topic detail */
  useEffect(() => {
    fetchTopicDetail(topicId)
      .then((data) => {
        setTopic(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [topicId]);

  /* Auto-scroll chat */
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, chatLoading]);

  /* Send chat message */
  const handleSendMessage = useCallback(async () => {
    const question = chatInput.trim();
    if (!question || chatLoading) return;

    setChatInput("");
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setChatLoading(true);

    try {
      const response = await sendChatMessage(topicId, question, sessionId);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: response.answer,
          sources: response.sources,
        },
      ]);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : "Unknown error";
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `Error: ${errorMessage}` },
      ]);
    } finally {
      setChatLoading(false);
    }
  }, [chatInput, chatLoading, topicId, sessionId]);

  /* Generate audio */
  const handleGenerateAudio = useCallback(async () => {
    setAudioLoading(true);
    setAudioError(null);
    try {
      const response = await generateAudio(topicId);
      setAudioUrl(getAudioUrl(response.audio_url));
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : "Unknown error";
      setAudioError(errorMessage);
    } finally {
      setAudioLoading(false);
    }
  }, [topicId]);

  /* ─── Render Loading / Error ─── */
  if (loading) {
    return (
      <div className="app-container">
        <div className="loading-container">
          <div className="spinner" />
          <span className="loading-text">Loading topic...</span>
        </div>
      </div>
    );
  }

  if (error || !topic) {
    return (
      <div className="app-container">
        <Link href="/" className="back-link">
          ← Back to topics
        </Link>
        <div className="empty-state">
          <div className="empty-state-icon">—</div>
          <h2>Topic not found</h2>
          <p>{error || "This topic does not exist or hasn't been ingested yet."}</p>
        </div>
      </div>
    );
  }

  /* ─── Key Info Section Data ─── */
  const keyInfoSections = [
    {
      key: "key_rights",
      label: "Key Rights",
      icon: "§",
      items: topic.key_info?.key_rights || [],
    },
    {
      key: "important_provisions",
      label: "Important Provisions",
      icon: "¶",
      items: topic.key_info?.important_provisions || [],
    },
    {
      key: "penalties",
      label: "Penalties",
      icon: "!",
      items: topic.key_info?.penalties || [],
    },
    {
      key: "who_can_benefit",
      label: "Who Can Benefit",
      icon: "∷",
      items: topic.key_info?.who_can_benefit || [],
    },
  ];

  return (
    <div className="app-container">
      {/* Back link */}
      <Link href="/" className="back-link">
        ← Back to topics
      </Link>

      {/* Header */}
      <div className="topic-header">
        <div className="topic-header-icon" style={{ background: meta.gradient }}>
          {meta.monogram}
        </div>
        <div>
          <h1>{topic.name}</h1>
          {topic.description && (
            <p className="topic-header-sub">{topic.description}</p>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs" role="tablist">
        {(
          [
            { id: "summary", label: "Summary" },
            { id: "keyinfo", label: "Key Info" },
            { id: "ask", label: "Ask AI" },
            { id: "audio", label: "Audio" },
          ] as { id: Tab; label: string }[]
        ).map((tab) => (
          <button
            key={tab.id}
            role="tab"
            aria-selected={activeTab === tab.id}
            className={`tab ${activeTab === tab.id ? "active" : ""}`}
            onClick={() => setActiveTab(tab.id)}
            id={`tab-${tab.id}`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="tab-content" key={activeTab}>
        {/* ── Summary Tab ── */}
        {activeTab === "summary" && (
          <div>
            {topic.summary ? (
              <div className="summary-content">
                {topic.summary.split("\n").map((paragraph, i) => (
                  <p key={i} style={{ marginBottom: i < topic.summary!.split("\n").length - 1 ? "16px" : 0 }}>
                    {paragraph}
                  </p>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <div className="empty-state-icon">—</div>
                <h2>No summary available</h2>
                <p>Run the ingestion pipeline to generate an AI summary.</p>
              </div>
            )}
          </div>
        )}

        {/* ── Key Info Tab ── */}
        {activeTab === "keyinfo" && (
          <div>
            {topic.key_info ? (
              <div className="key-info-grid">
                {keyInfoSections.map((section) => (
                  <div key={section.key} className="key-info-card">
                    <h3>
                      <span className="ki-icon">{section.icon}</span>
                      {section.label}
                    </h3>
                    {section.items.length > 0 ? (
                      <ul className="key-info-list">
                        {section.items.map((item, i) => (
                          <li key={i}>{item}</li>
                        ))}
                      </ul>
                    ) : (
                      <p style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>
                        No data available
                      </p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <div className="empty-state-icon">—</div>
                <h2>No key information available</h2>
                <p>Run the ingestion pipeline to extract key information.</p>
              </div>
            )}
          </div>
        )}

        {/* ── Chat Tab ── */}
        {activeTab === "ask" && (
          <div className="chat-container">
            <div className="chat-messages">
              {messages.length === 0 && !chatLoading && (
                <div className="chat-empty">
                  <div className="chat-empty-icon">?</div>
                  <p>Ask any question about {topic.name}</p>
                  <p style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
                    Powered by RAG — answers come from the actual legal text
                  </p>
                </div>
              )}

              {messages.map((msg, i) => (
                <div key={i} className={`chat-bubble ${msg.role}`}>
                  {msg.content}
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="sources">
                      Sources: {msg.sources.join(", ")}
                    </div>
                  )}
                </div>
              ))}

              {chatLoading && (
                <div className="typing-indicator">
                  <div className="typing-dot" />
                  <div className="typing-dot" />
                  <div className="typing-dot" />
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            <div className="chat-input-area">
              <input
                id="chat-input"
                type="text"
                className="chat-input"
                placeholder={`Ask about ${topic.name}...`}
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage();
                  }
                }}
                disabled={chatLoading}
              />
              <button
                id="chat-send-btn"
                className="chat-send-btn"
                onClick={handleSendMessage}
                disabled={chatLoading || !chatInput.trim()}
              >
                {chatLoading ? "..." : "Send →"}
              </button>
            </div>
          </div>
        )}

        {/* ── Audio Tab ── */}
        {activeTab === "audio" && (
          <div className="audio-container">
            <div className="audio-icon">♫</div>
            <h2 className="audio-title">Listen to the Summary</h2>
            <p className="audio-desc">
              AI-generated audio narration of the {topic.name} summary
            </p>

            {audioError && <div className="error-banner">{audioError}</div>}

            {audioUrl ? (
              <audio
                controls
                src={audioUrl}
                className="audio-player"
                id="audio-player"
              >
                Your browser does not support audio.
              </audio>
            ) : (
              <button
                id="audio-generate-btn"
                className="audio-generate-btn"
                onClick={handleGenerateAudio}
                disabled={audioLoading || !topic.summary}
              >
                {audioLoading ? (
                  <>
                    <div className="spinner" style={{ width: 18, height: 18, borderWidth: 2 }} />
                    Generating...
                  </>
                ) : (
                  "Generate Audio"
                )}
              </button>
            )}

            {!topic.summary && (
              <p
                style={{
                  marginTop: "16px",
                  fontSize: "0.85rem",
                  color: "var(--text-muted)",
                }}
              >
                No summary available. Run ingestion first.
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
