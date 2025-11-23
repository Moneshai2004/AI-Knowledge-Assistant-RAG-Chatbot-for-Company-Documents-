"use client";

import Sidebar from "@/components/Sidebar";
import MessageBubble from "@/components/MessageBubble";
import { askQuestion } from "@/lib/api";
import { useEffect, useRef, useState } from "react";

export default function ChatPage() {
  const [messages, setMessages] = useState<any[]>([
    {
      role: "system",
      text: "Ask anything about your company policies, HR rules, leave, benefits, etc.",
    },
  ]);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  const sendMessage = async () => {
    if (!input.trim() || isSending) return;

    const userMsg = { role: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsSending(true);

    try {
      const res = await askQuestion(userMsg.text);
      const botMsg = {
        role: "assistant",
        text: res.answer,
        sources: res.sources,
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: "Backend error. Try again." },
      ]);
    } finally {
      setIsSending(false);
    }
  };

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div
      className="flex h-screen 
      bg-white text-slate-900 
      dark:bg-slate-950 dark:text-slate-50"
    >
      <Sidebar />

      <main className="ml-0 flex-1 overflow-hidden md:ml-64">
        <div className="flex h-full flex-col px-4 pb-24 pt-4 md:pt-6">
          <div className="flex-1 space-y-4 overflow-y-auto">
            {messages.map((msg, i) => (
              <MessageBubble key={i} msg={msg} />
            ))}
            <div ref={bottomRef} />
          </div>

          <div
            className="fixed bottom-0 right-0 left-0 md:left-64 
            border-t border-slate-300 bg-slate-100
            dark:border-slate-800 dark:bg-slate-900
            p-4"
          >
            <div className="mx-auto max-w-3xl">
              <textarea
                rows={2}
                className="w-full resize-none rounded-xl
                border border-slate-300 bg-white text-slate-900
                dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100
                p-3 text-sm outline-none placeholder:text-slate-400"
                placeholder="Ask about leave policy, working hours, reimbursement…"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                  }
                }}
              />
              <button
                onClick={sendMessage}
                disabled={!input.trim() || isSending}
                className="mt-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium 
                text-white disabled:bg-slate-400"
              >
                {isSending ? "Sending…" : "Send"}
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
