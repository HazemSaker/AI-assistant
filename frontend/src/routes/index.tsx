import { useEffect, useRef, useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { PanelLeft, Settings as SettingsIcon, Sun, Moon, Sparkles, Bug, Key, Wifi } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ChatSidebar } from "@/components/ChatSidebar";
import { ChatMessage, TypingIndicator } from "@/components/ChatMessage";
import { ChatComposer } from "@/components/ChatComposer";
import { SettingsDialog } from "@/components/SettingsDialog";
import { useTheme } from "@/components/ThemeProvider";
import { useConversations } from "@/lib/use-conversations";
import { sendChat, type ChatMessage as Msg } from "@/lib/chat-api";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "ManHas — AI Technical Support" },
      {
        name: "description",
        content: "Intelligent AI assistant for technical support. Chat, diagnose, and resolve issues fast.",
      },
      { property: "og:title", content: "ManHas — AI Technical Support" },
      {
        property: "og:description",
        content: "Intelligent AI assistant for technical support.",
      },
    ],
  }),
  component: ChatPage,
});

const SUGGESTIONS = [
  { icon: Bug, title: "Debug an error", prompt: "I'm seeing this error in production: " },
  { icon: Wifi, title: "Network issue", prompt: "My internet connection keeps dropping when " },
  { icon: Key, title: "Account access", prompt: "I can't log into my account. I've tried " },
  { icon: Sparkles, title: "Set up a new tool", prompt: "Help me get started with " },
];

function ChatPage() {
  const { theme, toggle } = useTheme();
  const {
    conversations,
    activeId,
    active,
    setActiveId,
    newConversation,
    updateConversation,
    deleteConversation,
  } = useConversations();

  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [sending, setSending] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [active?.messages.length, sending]);

  const handleSend = async (text: string, attachments: import("@/lib/chat-api").ChatAttachment[] = []) => {
    let conv = active;
    if (!conv) conv = newConversation();

    const userMsg: Msg = { role: "user", content: text, attachments: attachments.length ? attachments : undefined };
    const nextMessages = [...conv.messages, userMsg];
    const isFirst = conv.messages.length === 0;
    const titleSeed = text || attachments[0]?.name || "New chat";

    updateConversation(conv.id, {
      messages: nextMessages,
      title: isFirst ? titleSeed.slice(0, 40) : conv.title,
    });

    setSending(true);
    try {
      const reply = await sendChat(nextMessages);
      updateConversation(conv.id, {
        messages: [...nextMessages, { role: "assistant", content: reply }],
      });
    } catch (e: any) {
      updateConversation(conv.id, {
        messages: [
          ...nextMessages,
          { role: "assistant", content: `⚠️ **Error contacting backend:** ${e.message}` },
        ],
      });
    } finally {
      setSending(false);
    }
  };

  const showEmpty = !active || active.messages.length === 0;

  return (
    <div className="flex h-screen w-full overflow-hidden bg-background text-foreground">
      <ChatSidebar
        conversations={conversations}
        activeId={activeId}
        onSelect={setActiveId}
        onNew={newConversation}
        onDelete={deleteConversation}
        open={sidebarOpen}
      />

      <div className="flex min-w-0 flex-1 flex-col">
        {/* Header */}
        <header className="flex h-14 items-center justify-between border-b border-border px-4">
          <div className="flex items-center gap-2">
            <Button
              size="icon"
              variant="ghost"
              onClick={() => setSidebarOpen((v) => !v)}
              className="h-9 w-9"
            >
              <PanelLeft className="h-4 w-4" />
            </Button>
            <h1 className="text-sm font-semibold">{active?.title ?? "ManHas"}</h1>
          </div>
          <div className="flex items-center gap-1">
            <Button size="icon" variant="ghost" onClick={toggle} className="h-9 w-9">
              {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </Button>
            <Button
              size="icon"
              variant="ghost"
              onClick={() => setSettingsOpen(true)}
              className="h-9 w-9"
            >
              <SettingsIcon className="h-4 w-4" />
            </Button>
          </div>
        </header>

        {/* Messages */}
        <div ref={scrollRef} className="flex-1 overflow-y-auto">
          {showEmpty ? (
            <EmptyState onPick={(p) => handleSend(p, [])} />
          ) : (
            <div className="mx-auto max-w-3xl py-4">
              {active!.messages.map((m, i) => (
                <ChatMessage key={i} message={m} />
              ))}
              {sending && <TypingIndicator />}
            </div>
          )}
        </div>

        <ChatComposer onSend={handleSend} disabled={sending} />
      </div>

      <SettingsDialog open={settingsOpen} onOpenChange={setSettingsOpen} />
    </div>
  );
}

function EmptyState({ onPick }: { onPick: (prompt: string) => void }) {
  return (
    <div className="mx-auto flex h-full max-w-3xl flex-col items-center justify-center px-4 py-10">
      <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-primary text-primary-foreground shadow-lg">
        <Sparkles className="h-6 w-6" />
      </div>
      <h2 className="text-2xl font-semibold tracking-tight">How can I help you today?</h2>
      <p className="mt-2 text-sm text-muted-foreground">
        Ask me anything technical — errors, setup, troubleshooting, or how-to.
      </p>

      <div className="mt-8 grid w-full grid-cols-1 gap-3 sm:grid-cols-2">
        {SUGGESTIONS.map((s) => {
          const Icon = s.icon;
          return (
            <button
              key={s.title}
              onClick={() => onPick(s.prompt)}
              className="group flex items-start gap-3 rounded-xl border border-border bg-card p-4 text-left transition-all hover:border-primary/40 hover:bg-accent"
            >
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-muted text-foreground/80 group-hover:bg-primary/10 group-hover:text-primary">
                <Icon className="h-4 w-4" />
              </div>
              <div className="min-w-0">
                <div className="text-sm font-medium">{s.title}</div>
                <div className="truncate text-xs text-muted-foreground">{s.prompt}…</div>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
