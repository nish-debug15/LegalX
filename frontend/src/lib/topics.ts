/**
 * Topic metadata — icon names, colors, and gradient data for each legal topic.
 */

export interface TopicMeta {
  iconName: "shield" | "scale" | "lock" | "file-text" | "receipt";
  monogram: string;
  gradient: string;
  accentColor: string;
}

export const TOPIC_META: Record<string, TopicMeta> = {
  pocso: {
    iconName: "shield",
    monogram: "PC",
    gradient: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    accentColor: "#667eea",
  },
  consumer: {
    iconName: "scale",
    monogram: "CP",
    gradient: "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
    accentColor: "#f093fb",
  },
  cyber: {
    iconName: "lock",
    monogram: "CL",
    gradient: "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
    accentColor: "#00d4ff",
  },
  rti: {
    iconName: "file-text",
    monogram: "RT",
    gradient: "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)",
    accentColor: "#43e97b",
  },
  gst: {
    iconName: "receipt",
    monogram: "GS",
    gradient: "linear-gradient(135deg, #fa709a 0%, #fee140 100%)",
    accentColor: "#fa709a",
  },
};

export function getTopicMeta(topicId: string): TopicMeta {
  return (
    TOPIC_META[topicId] || {
      iconName: "file-text" as const,
      monogram: "LX",
      gradient: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
      accentColor: "#667eea",
    }
  );
}
