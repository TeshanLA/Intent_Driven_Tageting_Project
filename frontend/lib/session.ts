export function getSessionId() {
  if (typeof window === "undefined") {
    return "server-session";
  }

  const existing = window.sessionStorage.getItem("demo-session-id");
  if (existing) {
    return existing;
  }

  const nextId = `session-${crypto.randomUUID()}`;
  window.sessionStorage.setItem("demo-session-id", nextId);
  return nextId;
}
