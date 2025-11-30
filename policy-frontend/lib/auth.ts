import axios from "axios";
const API_BASE = process.env.NEXT_PUBLIC_API_BASE;

// LOGIN
export const loginUser = async (username: string, password: string) => {
  try {
    const res = await axios.post(`${API_BASE}/auth/login`, null, {
      params: { username, password },
    });

    const token = res.data.token;

    // Save token for axios (client)
    localStorage.setItem("token", token);

    // Save token for Proxy (server)
    document.cookie = `token=${token}; path=/;`;

    return { ok: true };
  } catch (err: any) {
    return {
      ok: false,
      error: err.response?.data?.detail || "Login failed",
    };
  }
};

// GET TOKEN
export const getToken = () => {
  if (typeof window !== "undefined") {
    return localStorage.getItem("token");
  }
  return null;
};

// LOGOUT
export const logout = () => {
  if (typeof window !== "undefined") {
    localStorage.removeItem("token");
    document.cookie = "token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";

    window.location.href = "/login";
  }
};
