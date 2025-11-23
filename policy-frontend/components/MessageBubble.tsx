"use client";

import { TypeAnimation } from "react-type-animation";

export default function MessageBubble({ msg }: any) {
  const isUser = msg.role === "user";

  return (
    <div
      className={`flex w-full gap-3 ${
        isUser ? "justify-end" : "justify-start"
      }`}
    >
      {!isUser && (
        <div
          className="mt-1 flex h-8 w-8 items-center justify-center rounded-full 
          bg-indigo-600 text-white text-xs font-semibold"
        >
          AI
        </div>
      )}

      <div
        className={`max-w-xl whitespace-pre-wrap rounded-2xl px-4 py-3 text-sm shadow-sm 
          ${
            isUser
              ? "bg-indigo-600 text-white rounded-br-sm"
              : `
                  bg-slate-200 text-slate-900 border border-slate-300 rounded-bl-sm
                  dark:bg-slate-900 dark:text-slate-50 dark:border-slate-800
                `
          }`}
      >
        {msg.role === "assistant" ? (
          <TypeAnimation sequence={[msg.text]} wrapper="p" cursor={false} />
        ) : (
          <p>{msg.text}</p>
        )}
      </div>

      {isUser && (
        <div
          className="mt-1 flex h-8 w-8 items-center justify-center rounded-full 
          bg-slate-700 text-white text-xs font-semibold"
        >
          You
        </div>
      )}
    </div>
  );
}
