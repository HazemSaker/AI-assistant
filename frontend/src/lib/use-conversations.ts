import { useEffect, useState, useCallback } from "react";
import type { ChatMessage } from "./chat-api";

export type Conversation = {
  id: string;
  title: string;
  messages: ChatMessage[];
  createdAt: number;
};

const KEY = "chat_conversations";

function load(): Conversation[] {
  if (typeof window === "undefined") return [];
  try {
    return JSON.parse(localStorage.getItem(KEY) || "[]");
  } catch {
    return [];
  }
}

function save(items: Conversation[]) {
  if (typeof window === "undefined") return;
  localStorage.setItem(KEY, JSON.stringify(items));
}

export function useConversations() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);

  useEffect(() => {
    const loaded = load();
    setConversations(loaded);
    if (loaded[0]) setActiveId(loaded[0].id);
  }, []);

  const persist = useCallback((items: Conversation[]) => {
    setConversations(items);
    save(items);
  }, []);

  const newConversation = useCallback(() => {
    const c: Conversation = {
      id: crypto.randomUUID(),
      title: "New chat",
      messages: [],
      createdAt: Date.now(),
    };
    const next = [c, ...conversations];
    persist(next);
    setActiveId(c.id);
    return c;
  }, [conversations, persist]);

  const updateConversation = useCallback(
    (id: string, patch: Partial<Conversation>) => {
      const next = conversations.map((c) => (c.id === id ? { ...c, ...patch } : c));
      persist(next);
    },
    [conversations, persist]
  );

  const deleteConversation = useCallback(
    (id: string) => {
      const next = conversations.filter((c) => c.id !== id);
      persist(next);
      if (activeId === id) setActiveId(next[0]?.id ?? null);
    },
    [conversations, persist, activeId]
  );

  const active = conversations.find((c) => c.id === activeId) ?? null;

  return {
    conversations,
    activeId,
    active,
    setActiveId,
    newConversation,
    updateConversation,
    deleteConversation,
  };
}
