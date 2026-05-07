import { useEffect, useRef, useState, useCallback } from "react";

// Web Speech API typings vary by browser. Keep them loose.
type SR = any;

export function useVoiceInput(onResult: (text: string, isFinal: boolean) => void) {
  const [isListening, setIsListening] = useState(false);
  const [supported, setSupported] = useState(false);
  const recRef = useRef<SR | null>(null);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const SR =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    setSupported(!!SR);
  }, []);

  const start = useCallback(() => {
    if (typeof window === "undefined") return;
    const SR =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SR) return;
    const rec: SR = new SR();
    rec.continuous = true;
    rec.interimResults = true;
    rec.lang = "en-US";
    rec.onresult = (e: any) => {
      let interim = "";
      let final = "";
      for (let i = e.resultIndex; i < e.results.length; i++) {
        const r = e.results[i];
        if (r.isFinal) final += r[0].transcript;
        else interim += r[0].transcript;
      }
      if (final) onResult(final, true);
      else if (interim) onResult(interim, false);
    };
    rec.onend = () => setIsListening(false);
    rec.onerror = () => setIsListening(false);
    rec.start();
    recRef.current = rec;
    setIsListening(true);
  }, [onResult]);

  const stop = useCallback(() => {
    recRef.current?.stop();
    setIsListening(false);
  }, []);

  return { isListening, supported, start, stop };
}
