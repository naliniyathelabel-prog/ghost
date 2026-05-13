import Constants from "expo-constants";

const BASE = Constants.expoConfig?.extra?.apiUrl ?? "http://localhost:8000";

async function req(path: string, options?: RequestInit) {
  const r = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(options?.headers ?? {}) },
    ...options,
  });
  if (!r.ok) throw new Error(`API ${path} → ${r.status}`);
  return r.json();
}

export const api = {
  health: () => req("/health"),
  getProfile: () => req("/ghost/profile"),
  updateProfile: (data: object) =>
    req("/ghost/profile", { method: "PUT", body: JSON.stringify(data) }),
  toggle: (active: boolean) =>
    req(`/ghost/toggle?active=${active}`, { method: "POST" }),
  getMessages: (contact?: string) =>
    req(`/ghost/messages${contact ? `?contact=${contact}` : ""}`),
  rateMessage: (id: string, rating: 1 | -1) =>
    req(`/ghost/messages/${id}/rate?rating=${rating}`, { method: "POST" }),
};
