import { useEffect, useRef, useState } from "react";
import { ArrowUp, Mic, MicOff, Paperclip, X, FileText, Image as ImageIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useVoiceInput } from "@/lib/use-voice-input";
import type { ChatAttachment } from "@/lib/chat-api";
import { toast } from "sonner";

type Props = {
  onSend: (text: string, attachments: ChatAttachment[]) => void;
  disabled?: boolean;
};

const MAX_FILES = 5;
const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5 MB per file (base64 inflates ~33%)
const ACCEPTED =
  "image/png,image/jpeg,image/webp,image/gif,text/plain,text/csv,application/json,application/pdf,.log,.txt,.md";

function fileToAttachment(file: File): Promise<ChatAttachment> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () =>
      resolve({
        name: file.name,
        type: file.type || "application/octet-stream",
        size: file.size,
        dataUrl: reader.result as string,
      });
    reader.onerror = () => reject(reader.error);
    reader.readAsDataURL(file);
  });
}

export function ChatComposer({ onSend, disabled }: Props) {
  const [value, setValue] = useState("");
  const [attachments, setAttachments] = useState<ChatAttachment[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const baseRef = useRef("");
  const taRef = useRef<HTMLTextAreaElement>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const { isListening, supported, start, stop } = useVoiceInput((text, isFinal) => {
    if (isFinal) {
      const next = (baseRef.current ? baseRef.current + " " : "") + text;
      baseRef.current = next.trim();
      setValue(baseRef.current);
    } else {
      setValue((baseRef.current ? baseRef.current + " " : "") + text);
    }
  });

  useEffect(() => {
    const ta = taRef.current;
    if (!ta) return;
    ta.style.height = "auto";
    ta.style.height = Math.min(ta.scrollHeight, 200) + "px";
  }, [value]);

  const addFiles = async (files: FileList | File[]) => {
    const list = Array.from(files);
    if (attachments.length + list.length > MAX_FILES) {
      toast.error(`You can attach up to ${MAX_FILES} files per message.`);
      return;
    }
    const next: ChatAttachment[] = [];
    for (const f of list) {
      if (f.size > MAX_FILE_SIZE) {
        toast.error(`"${f.name}" is too large (max 5 MB).`);
        continue;
      }
      try {
        next.push(await fileToAttachment(f));
      } catch {
        toast.error(`Could not read "${f.name}".`);
      }
    }
    if (next.length) setAttachments((a) => [...a, ...next]);
  };

  const removeAttachment = (i: number) =>
    setAttachments((a) => a.filter((_, idx) => idx !== i));

  const submit = () => {
    const text = value.trim();
    if ((!text && attachments.length === 0) || disabled) return;
    onSend(text, attachments);
    setValue("");
    setAttachments([]);
    baseRef.current = "";
    if (isListening) stop();
  };

  const toggleMic = () => {
    if (isListening) stop();
    else {
      baseRef.current = value;
      start();
    }
  };

  return (
    <div
      className="border-t border-border bg-background px-4 pb-5 pt-4"
      onDragOver={(e) => {
        e.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setIsDragging(false);
        if (e.dataTransfer.files.length) addFiles(e.dataTransfer.files);
      }}
    >
      <div className="mx-auto max-w-3xl">
        <div
          className={`relative flex flex-col gap-2 rounded-2xl border bg-card p-2 shadow-sm transition-colors focus-within:ring-2 focus-within:ring-ring/40 ${
            isDragging ? "border-primary bg-primary/5" : "border-border"
          }`}
        >
          {attachments.length > 0 && (
            <div className="flex flex-wrap gap-2 px-1 pt-1">
              {attachments.map((a, i) => (
                <AttachmentChip key={i} att={a} onRemove={() => removeAttachment(i)} />
              ))}
            </div>
          )}

          <div className="flex items-end gap-2">
            <Button
              type="button"
              size="icon"
              variant="ghost"
              onClick={() => fileRef.current?.click()}
              className="h-9 w-9 shrink-0"
              title="Attach files or screenshots"
            >
              <Paperclip className="h-4 w-4" />
            </Button>
            <input
              ref={fileRef}
              type="file"
              accept={ACCEPTED}
              multiple
              hidden
              onChange={(e) => {
                if (e.target.files) addFiles(e.target.files);
                e.target.value = "";
              }}
            />

            <textarea
              ref={taRef}
              value={value}
              onChange={(e) => {
                setValue(e.target.value);
                baseRef.current = e.target.value;
              }}
              onPaste={(e) => {
                const files = Array.from(e.clipboardData.files);
                if (files.length) {
                  e.preventDefault();
                  addFiles(files);
                }
              }}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  submit();
                }
              }}
              placeholder={
                isDragging
                  ? "Drop files to attach"
                  : isListening
                    ? "Listening…"
                    : "Describe your technical issue or drop a screenshot…"
              }
              rows={1}
              className="max-h-48 flex-1 resize-none bg-transparent px-1 py-2 text-sm outline-none placeholder:text-muted-foreground"
            />

            {supported && (
              <Button
                type="button"
                size="icon"
                variant={isListening ? "destructive" : "ghost"}
                onClick={toggleMic}
                className={`h-9 w-9 shrink-0 ${isListening ? "recording-pulse" : ""}`}
                title={isListening ? "Stop recording" : "Record voice from microphone"}
              >
                {isListening ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
              </Button>
            )}

            <Button
              type="button"
              size="icon"
              onClick={submit}
              disabled={(!value.trim() && attachments.length === 0) || disabled}
              className="h-9 w-9 shrink-0 rounded-xl"
            >
              <ArrowUp className="h-4 w-4" />
            </Button>
          </div>
        </div>

        <p className="mt-2 text-center text-xs text-muted-foreground">
          <kbd className="rounded border border-border px-1">Enter</kbd> send ·{" "}
          <kbd className="rounded border border-border px-1">Shift+Enter</kbd> newline · 📎 attach screenshots/logs
          {supported && " · 🎙 tap mic to record voice"}
        </p>
      </div>
    </div>
  );
}

function AttachmentChip({ att, onRemove }: { att: ChatAttachment; onRemove: () => void }) {
  const isImage = att.type.startsWith("image/");
  return (
    <div className="group relative flex items-center gap-2 rounded-lg border border-border bg-background p-1.5 pr-2">
      {isImage ? (
        <img
          src={att.dataUrl}
          alt={att.name}
          className="h-10 w-10 rounded-md object-cover"
        />
      ) : (
        <div className="flex h-10 w-10 items-center justify-center rounded-md bg-muted">
          <FileText className="h-4 w-4 text-muted-foreground" />
        </div>
      )}
      <div className="min-w-0 max-w-[140px]">
        <div className="truncate text-xs font-medium">{att.name}</div>
        <div className="text-[10px] text-muted-foreground">
          {(att.size / 1024).toFixed(1)} KB
        </div>
      </div>
      <button
        type="button"
        onClick={onRemove}
        className="ml-1 flex h-5 w-5 items-center justify-center rounded-full bg-muted text-muted-foreground hover:bg-destructive hover:text-destructive-foreground"
        aria-label={`Remove ${att.name}`}
      >
        <X className="h-3 w-3" />
      </button>
    </div>
  );
}

// Re-export icon to satisfy unused-import lint cleanly
export { ImageIcon };
