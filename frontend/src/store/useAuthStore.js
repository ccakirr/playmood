import { create } from "zustand";

const TOKEN_KEY = "playmood_token";
const USER_KEY = "playmood_user";

const BASE_URL = () => import.meta.env.VITE_API_URL || "http://localhost:8000";

export const useAuthStore = create((set, get) => ({
  token: localStorage.getItem(TOKEN_KEY) || null,
  user: JSON.parse(localStorage.getItem(USER_KEY) || "null"),

  // ── Register ──────────────────────────────────────────────────────────────
  register: async (email, password) => {
    const res = await fetch(`${BASE_URL()}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Registration failed.");
    // Auto-login after register
    return get().login(email, password);
  },

  // ── Login ─────────────────────────────────────────────────────────────────
  login: async (email, password) => {
    const form = new URLSearchParams();
    form.append("username", email);
    form.append("password", password);

    const res = await fetch(`${BASE_URL()}/auth/token`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: form.toString(),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Login failed.");

    const token = data.access_token;
    const user = { email };

    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
    set({ token, user });
  },

  // ── Logout ────────────────────────────────────────────────────────────────
  logout: () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    set({ token: null, user: null });
  },

  // ── Save playlist ─────────────────────────────────────────────────────────
  savePlaylist: async (playlistId, playlistName, prompt) => {
    const { token } = get();
    if (!token) throw new Error("Not authenticated.");

    const res = await fetch(`${BASE_URL()}/playlist/save`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        playlist_id: playlistId,
        playlist_name: playlistName,
        prompt,
      }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Save failed.");
    return data;
  },

  // ── Fetch my playlists ────────────────────────────────────────────────────
  fetchMyPlaylists: async () => {
    const { token } = get();
    if (!token) throw new Error("Not authenticated.");

    const res = await fetch(`${BASE_URL()}/playlist/my-playlists`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Fetch failed.");
    return data;
  },

  // ── Delete playlist ───────────────────────────────────────────────────────
  deletePlaylist: async (playlistId) => {
    const { token } = get();
    if (!token) throw new Error("Not authenticated.");
    const res = await fetch(`${BASE_URL()}/playlist/${playlistId}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) {
      const data = await res.json();
      throw new Error(data.detail || "Delete failed.");
    }
  },

  // ── Restore saved playlist into in-memory store for YouTube export ────────
  restoreForYoutube: async (dbId) => {
    const { token } = get();
    if (!token) throw new Error("Not authenticated.");

    const res = await fetch(
      `${BASE_URL()}/playlist/restore-for-youtube/${dbId}`,
      {
        headers: { Authorization: `Bearer ${token}` },
      },
    );
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Restore failed.");
    return data.playlist_id; // temp UUID for /youtube/start
  },
}));
