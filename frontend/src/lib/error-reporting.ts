export interface AppErrorContext {
  boundary?: string;
  route?: string;
  [key: string]: unknown;
}

export function reportAppError(error: unknown, context: AppErrorContext = {}) {
  if (typeof window === "undefined") return;

  const message =
    error instanceof Response
      ? `Response ${error.status}${error.url ? ` at ${error.url}` : ""}`
      : error instanceof Error
        ? error.message
        : String(error);

  const stack = error instanceof Error ? error.stack : undefined;

  // Log to standard console for developer diagnostics
  console.error("[P8 UXBB Error Observatory]", {
    message,
    stack,
    route: window.location.pathname,
    ...context,
  });
}
