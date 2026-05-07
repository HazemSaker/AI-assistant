// Configurable backend client. Set VITE_CHAT_API_URL in .env or use the
// in-app Settings dialog to override at runtime (saved in localStorage).

export type ChatAttachment = {
  name: string;
  type: string;        // MIME type
  size: number;        // bytes
  dataUrl: string;     // base64 data URL (data:<mime>;base64,...)
};

export type ChatMessage = {
  role: "user" | "assistant" | "system";
  content: string;
  attachments?: ChatAttachment[];
};

const STORAGE_KEY = "chat_api_url";

export function getApiUrl(): string {
  if (typeof window !== "undefined") {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) return stored;
  }
  return import.meta.env.VITE_CHAT_API_URL || "";
}

export function setApiUrl(url: string) {
  if (typeof window !== "undefined") {
    localStorage.setItem(STORAGE_KEY, url);
  }
}

/**
 * Sends the conversation to your backend.
 *
 * Request body:
 *   {
 *     messages: [
 *       {
 *         role: "user" | "assistant" | "system",
 *         content: string,
 *         attachments?: [{ name, type, size, dataUrl }]
 *       }
 *     ]
 *   }
 *
 * `dataUrl` is a base64 data URL — strip the prefix server-side if you only
 * need the raw bytes: `dataUrl.split(",")[1]`.
 *
 * Response: { reply: string } | { content: string } | { message: string }
 */
export async function sendChat(messages: ChatMessage[]): Promise<string> {
  const url = getApiUrl();
  if (!url) {
    await new Promise((r) => setTimeout(r, 700));
    const last = messages[messages.length - 1];
    const attachInfo = last?.attachments?.length
      ? `\n\nReceived ${last.attachments.length} attachment(s): ${last.attachments
          .map((a) => `\`${a.name}\` (${(a.size / 1024).toFixed(1)} KB)`)
          .join(", ")}`
      : "";
    return `**No backend configured yet.**\n\nOpen the gear icon (top right) and paste your backend URL.${attachInfo}\n\nYour message: \n> ${last?.content ?? ""}`;
  }

  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages }),
  });

  if (!res.ok) {
    throw new Error(`Backend error ${res.status}: ${await res.text()}`);
  }

  const data = await res.json();
  return data.reply ?? data.content ?? data.message ?? JSON.stringify(data);
}
