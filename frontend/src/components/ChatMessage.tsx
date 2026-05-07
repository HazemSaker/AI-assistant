import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { FileText } from "lucide-react";
import type { ChatMessage as Msg, ChatAttachment } from "@/lib/chat-api";

export function ChatMessage({ message }: { message: Msg }) {
  const isUser = message.role === "user";

  if (isUser) {
    return (
      <div className="flex w-full justify-end px-4 py-3">
        <div className="flex max-w-[75%] flex-col items-end gap-2">
          {message.attachments && message.attachments.length > 0 && (
            <div className="flex flex-wrap justify-end gap-2">
              {message.attachments.map((a, i) => (
                <AttachmentPreview key={i} att={a} />
              ))}
            </div>
          )}
          {message.content && (
            <div className="rounded-2xl bg-user-bubble px-4 py-2.5 text-sm text-foreground">
              <div className="prose-chat whitespace-pre-wrap">{message.content}</div>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="flex w-full px-4 py-3">
      <div className="min-w-0 max-w-full flex-1">
        {message.attachments && message.attachments.length > 0 && (
          <div className="mb-2 flex flex-wrap gap-2">
            {message.attachments.map((a, i) => (
              <AttachmentPreview key={i} att={a} />
            ))}
          </div>
        )}
        {message.content && (
          <div className="prose-chat text-foreground">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
}

function AttachmentPreview({ att }: { att: ChatAttachment }) {
  if (att.type.startsWith("image/")) {
    return (
      <a
        href={att.dataUrl}
        target="_blank"
        rel="noreferrer"
        className="block overflow-hidden rounded-lg border border-border"
      >
        <img src={att.dataUrl} alt={att.name} className="max-h-64 max-w-xs object-cover" />
      </a>
    );
  }
  return (
    <a
      href={att.dataUrl}
      download={att.name}
      className="flex items-center gap-2 rounded-lg border border-border bg-card px-3 py-2 text-xs hover:bg-accent"
    >
      <FileText className="h-4 w-4 text-muted-foreground" />
      <div>
        <div className="font-medium">{att.name}</div>
        <div className="text-[10px] text-muted-foreground">
          {(att.size / 1024).toFixed(1)} KB
        </div>
      </div>
    </a>
  );
}

export function TypingIndicator() {
  return (
    <div className="flex w-full px-4 py-3">
      <div className="flex items-center gap-1.5 pt-1">
        <span className="typing-dot h-2 w-2 rounded-full bg-muted-foreground" />
        <span className="typing-dot h-2 w-2 rounded-full bg-muted-foreground" />
        <span className="typing-dot h-2 w-2 rounded-full bg-muted-foreground" />
      </div>
    </div>
  );
}
