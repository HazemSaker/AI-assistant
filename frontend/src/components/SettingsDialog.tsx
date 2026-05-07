import { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { getApiUrl, setApiUrl } from "@/lib/chat-api";

export function SettingsDialog({
  open,
  onOpenChange,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
}) {
  const [url, setUrl] = useState("");

  useEffect(() => {
    if (open) setUrl(getApiUrl());
  }, [open]);

  const save = () => {
    setApiUrl(url.trim());
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Backend settings</DialogTitle>
          <DialogDescription>
            Paste the URL of your AI tech-support backend. The UI will POST{" "}
            <code className="text-xs">{`{ messages: [...] }`}</code> and expects{" "}
            <code className="text-xs">{`{ reply: string }`}</code> in response.
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-2 py-2">
          <Label htmlFor="api-url">API endpoint</Label>
          <Input
            id="api-url"
            placeholder="https://your-server.com/api/chat"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
          />
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={save}>Save</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
