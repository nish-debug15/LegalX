/**
 * Topic metadata — icons, colors, and gradient data for each legal topic.
 */

export interface TopicMeta {
  icon: string;
  gradient: string;
  accentColor: string;
  bgClass: string;
}

export const TOPIC_META: Record<string, TopicMeta> = {
  pocso: {
    icon: "🛡️",
    gradient: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    accentColor: "#764ba2",
    bgClass: "topic-pocso",
  },
  consumer: {
    icon: "⚖️",
    gradient: "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
    accentColor: "#f5576c",
    bgClass: "topic-consumer",
  },
  cyber: {
    icon: "🔒",
    gradient: "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
    accentColor: "#4facfe",
    bgClass: "topic-cyber",
  },
  rti: {
    icon: "📋",
    gradient: "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)",
    accentColor: "#43e97b",
    bgClass: "topic-rti",
  },
  gst: {
    icon: "💰",
    gradient: "linear-gradient(135deg, #fa709a 0%, #fee140 100%)",
    accentColor: "#fa709a",
    bgClass: "topic-gst",
  },
};

export function getTopicMeta(topicId: string): TopicMeta {
  return (
    TOPIC_META[topicId] || {
      icon: "📄",
      gradient: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
      accentColor: "#667eea",
      bgClass: "topic-default",
    }
  );
}
