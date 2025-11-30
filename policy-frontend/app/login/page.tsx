"use client";

import { useState } from "react";
import { loginUser } from "@/lib/auth";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const router = useRouter();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");

  const handleLogin = async () => {
    setErr("");
    const res = await loginUser(username, password);

    if (!res.ok) {
      setErr(res.error || "Invalid credentials");
      return;
    }

    router.push("/admin/dashboard");
  };

  return (
    <div className="flex h-screen items-center justify-center bg-slate-950 text-slate-50">
      <div className="w-full max-w-sm rounded-lg bg-slate-900 p-6 shadow-xl border border-slate-800">
        <h1 className="text-xl font-semibold mb-4">Admin Login</h1>

        {err && <p className="text-red-400 mb-3 text-sm">{err}</p>}

        <input
          type="text"
          placeholder="Username"
          className="w-full rounded bg-slate-800 p-2 mb-3 text-sm outline-none"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />

        <input
          type="password"
          placeholder="Password"
          className="w-full rounded bg-slate-800 p-2 mb-4 text-sm outline-none"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button
          onClick={handleLogin}
          className="w-full rounded bg-blue-600 py-2 font-medium hover:bg-blue-500"
        >
          Login
        </button>
      </div>
    </div>
  );
}
