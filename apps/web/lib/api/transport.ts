import { returnPlayWebEnv } from "@/lib/env";

export class UnauthorizedApiError extends Error {
  constructor(message = "Your session does not have access to this workflow.") {
    super(message);
    this.name = "UnauthorizedApiError";
  }
}

export async function apiRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${apiBaseUrl()}${path}`, {
    ...init,
    cache: "no-store",
    headers: {
      ...authHeaders(),
      ...(init.headers ?? {}),
    },
  });
  if (response.status === 401 || response.status === 403) {
    throw new UnauthorizedApiError();
  }
  if (!response.ok) {
    throw new Error(`API request failed with ${response.status}: ${path}`);
  }
  return response.json() as Promise<T>;
}

export async function apiArrayBufferRequest(
  path: string,
  errorLabel: string = path,
): Promise<ArrayBuffer> {
  const response = await fetch(`${apiBaseUrl()}${path}`, {
    cache: "no-store",
    headers: authHeaders(),
  });
  if (response.status === 401 || response.status === 403) {
    throw new UnauthorizedApiError();
  }
  if (!response.ok) {
    throw new Error(`API request failed with ${response.status}: ${errorLabel}`);
  }
  return response.arrayBuffer();
}

export function jsonRequest(method: "POST" | "PATCH", payload: unknown): RequestInit {
  return {
    method,
    body: JSON.stringify(payload),
    headers: {
      "content-type": "application/json",
    },
  };
}

export function ensureWritableApiMode() {
  if (!usesApi()) {
    throw new Error("Case creation requires RETURN_PLAY_DATA_MODE=api or api-demo.");
  }
}

export function currentOrganizationId(): string {
  return returnPlayWebEnv().organizationId;
}

export function currentActorId(): string {
  return returnPlayWebEnv().actorId;
}

export function currentActorRole(): string {
  return returnPlayWebEnv().actorRole;
}

export function usesApi(): boolean {
  return dataMode() === "api" || dataMode() === "api-demo";
}

export function dataMode(): string {
  return returnPlayWebEnv().dataMode;
}

function apiBaseUrl(): string {
  return returnPlayWebEnv().apiBaseUrl;
}

function authHeaders(): Record<string, string> {
  const env = returnPlayWebEnv();
  const token = env.apiToken;
  if (token) {
    return { Authorization: `Bearer ${token}` };
  }
  return {
    "x-actor-id": env.actorId,
    "x-actor-role": env.actorRole,
    "x-organization-id": env.organizationId,
  };
}
