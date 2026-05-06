import { Plus, MessageSquare, Trash2, Headphones } from "lucide-react";
import type { Conversation } from "@/lib/use-conversations";
import { Button } from "@/components/ui/button";

type Props = {
  conversations: Conversation[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onNew: () => void;
  onDelete: (id: string) => void;
  open: boolean;
};

export function ChatSidebar({ conversations, activeId, onSelect, onNew, onDelete, open }: Props) {
  return (
    <aside
      className={`${
        open ? "w-72" : "w-0"
      } shrink-0 overflow-hidden transition-all duration-300 ease-in-out border-r border-border`}
      style={{ backgroundColor: "var(--sidebar-bg)" }}
    >
      <div className="flex h-full w-72 flex-col">
        <div className="flex items-center gap-2 px-4 py-4">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <Headphones className="h-4 w-4" />
          </div>
          <div className="flex-1">
            <div className="text-sm font-semibold leading-tight">ManHas</div>
            <div className="text-xs text-muted-foreground">AI Support</div>
          </div>
        </div>

        <div className="px-3 pb-3">
          <Button onClick={onNew} className="w-full justify-start gap-2" variant="outline">
            <Plus className="h-4 w-4" />
            New chat
          </Button>
        </div>

        <div className="flex-1 overflow-y-auto px-2 pb-4">
          {conversations.length === 0 ? (
            <p className="px-3 py-8 text-center text-xs text-muted-foreground">
              No conversations yet
            </p>
          ) : (
            <ul className="space-y-0.5">
              {conversations.map((c) => (
                <li key={c.id}>
                  <button
                    onClick={() => onSelect(c.id)}
                    className={`group flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-sm transition-colors ${
                      c.id === activeId
                        ? "bg-accent text-accent-foreground"
                        : "hover:bg-accent/60 text-foreground/80"
                    }`}
                  >
                    <MessageSquare className="h-4 w-4 shrink-0 opacity-70" />
                    <span className="flex-1 truncate">{c.title}</span>
                    <Trash2
                      className="h-3.5 w-3.5 shrink-0 opacity-0 transition-opacity hover:text-destructive group-hover:opacity-60"
                      onClick={(e) => {
                        e.stopPropagation();
                        onDelete(c.id);
                      }}
                    />
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="border-t border-border px-4 py-3 text-xs text-muted-foreground">
          History saved locally
        </div>
      </div>
    </aside>
  );
}
