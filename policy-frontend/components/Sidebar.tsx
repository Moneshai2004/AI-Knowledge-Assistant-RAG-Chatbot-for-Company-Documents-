"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { Menu, X, Sun, Moon } from "lucide-react";
import { useTheme } from "@/lib/theme";

const nav = [
  { href: "/", label: "Chat" },
  { href: "/upload", label: "Upload PDF" },
  { href: "/admin", label: "Admin Tools" },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  const { theme, toggle } = useTheme();

  return (
    <>
      {/* Mobile */}
      <button
        onClick={() => setOpen(true)}
        className="fixed left-4 top-4 z-50 rounded-lg 
        bg-slate-200 text-slate-900 
        dark:bg-slate-900 dark:text-slate-200 
        p-2 shadow md:hidden"
      >
        <Menu size={22} />
      </button>

      {open && (
        <div
          className="fixed inset-0 bg-black/40 backdrop-blur-sm z-40 md:hidden"
          onClick={() => setOpen(false)}
        />
      )}

      <aside
        className={`fixed left-0 top-0 z-40 h-full w-64 transform 
        bg-white border-r border-slate-300 
        dark:bg-slate-950 dark:border-slate-800
        transition-transform md:translate-x-0 ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div
          className="flex items-center justify-between 
          border-b border-slate-300 dark:border-slate-800
          px-4 py-4"
        >
          <span
            className="text-lg font-semibold 
            text-slate-900 dark:text-slate-100"
          >
            AI Policy Assistant
          </span>

          <button
            onClick={() => setOpen(false)}
            className="rounded p-1 
            bg-slate-200 text-slate-900
            dark:bg-slate-900 dark:text-slate-300
            md:hidden"
          >
            <X size={20} />
          </button>
        </div>

        <nav className="mt-4 flex flex-col space-y-1 px-4">
          {nav.map((item) => {
            const active = pathname === item.href;

            const activeStyles =
              "bg-slate-300 text-slate-900 dark:bg-slate-800 dark:text-slate-50";

            const inactiveStyles =
              "text-slate-600 hover:bg-slate-200 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-900 dark:hover:text-slate-50";

            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setOpen(false)}
                className={`rounded-lg px-3 py-2 text-sm transition ${
                  active ? activeStyles : inactiveStyles
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="mt-auto px-4 py-4">
          <button
            onClick={toggle}
            className="flex w-full items-center gap-2 rounded-lg 
            bg-slate-200 text-slate-900
            dark:bg-slate-900 dark:text-slate-300
            px-3 py-2 text-sm hover:bg-slate-300 dark:hover:bg-slate-800"
          >
            {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
            {theme === "dark" ? "Light Mode" : "Dark Mode"}
          </button>
        </div>
      </aside>
    </>
  );
}
