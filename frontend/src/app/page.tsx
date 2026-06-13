"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchTopics, TopicListItem } from "@/lib/api";
import { getTopicMeta, TopicMeta } from "@/lib/topics";
import { Shield, Scale, Lock, FileText, Receipt, LucideIcon } from "lucide-react";

const ICON_MAP: Record<TopicMeta["iconName"], LucideIcon> = {
  shield: Shield,
  scale: Scale,
  "lock": Lock,
  "file-text": FileText,
  receipt: Receipt,
};

export default function HomePage() {
  const [topics, setTopics] = useState<TopicListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTopics()
      .then((data) => {
        setTopics(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  return (
    <div className="app-container">
      {/* Hero */}
      <section className="hero">
        <h1>Indian Law, Simplified by AI</h1>
        <p>
          Explore key Indian laws with AI-generated summaries, structured insights,
          interactive Q&amp;A, and audio narration — all in plain language.
        </p>
      </section>

      {/* Topics Grid */}
      {loading ? (
        <div className="loading-container">
          <div className="spinner" />
          <span className="loading-text">Loading topics...</span>
        </div>
      ) : error ? (
        <div className="empty-state">
          <div className="empty-state-icon">—</div>
          <h2>Could not load topics</h2>
          <p>
            Make sure the backend is running and ingestion has been completed.
            <br />
            <small style={{ color: "var(--text-muted)" }}>{error}</small>
          </p>
        </div>
      ) : topics.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">—</div>
          <h2>No topics yet</h2>
          <p>
            Run the ingestion pipeline first:
            <br />
            <code style={{ fontSize: "0.85rem", color: "var(--accent-primary)" }}>
              POST /api/ingest
            </code>
          </p>
        </div>
      ) : (
        <div className="topics-grid">
          {topics.map((topic) => {
            const meta = getTopicMeta(topic.id);
            const IconComponent = ICON_MAP[meta.iconName];
            return (
              <Link
                key={topic.id}
                href={`/topic/${topic.id}`}
                className="topic-card"
                id={`topic-card-${topic.id}`}
              >
                <div className="topic-card-content">
                  <div className="topic-card-icon-wrap">
                    <IconComponent size={28} color={meta.accentColor} strokeWidth={1.75} />
                  </div>
                  <h3>{topic.name}</h3>
                  <p>{topic.description || "Explore this topic →"}</p>
                </div>
                <span className="topic-card-arrow">→</span>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
