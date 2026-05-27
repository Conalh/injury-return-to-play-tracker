export type ReturnPlayDataMode = "demo" | "api" | "api-demo";
export type ReturnPlayRuntimeEnv = "local" | "test" | "staging" | "production";

export type ReturnPlayWebEnv = {
  runtimeEnv: ReturnPlayRuntimeEnv;
  dataMode: ReturnPlayDataMode;
  apiBaseUrl: string;
  apiToken?: string;
  actorId: string;
  actorRole: string;
  organizationId: string;
};

export function returnPlayWebEnv(): ReturnPlayWebEnv {
  const runtimeEnv = parseRuntimeEnv(process.env.RETURN_PLAY_ENV);
  const dataMode = parseDataMode(process.env.RETURN_PLAY_DATA_MODE);
  const configuredApiBaseUrl = process.env.RETURN_PLAY_API_BASE_URL;

  if (runtimeEnv === "production" && dataMode === "demo") {
    throw new Error("RETURN_PLAY_DATA_MODE must be api or api-demo in production.");
  }
  if (runtimeEnv === "production" && !configuredApiBaseUrl) {
    throw new Error("RETURN_PLAY_API_BASE_URL is required in production.");
  }

  return {
    runtimeEnv,
    dataMode,
    apiBaseUrl: configuredApiBaseUrl ?? "http://127.0.0.1:8000",
    apiToken: process.env.RETURN_PLAY_API_TOKEN,
    actorId: process.env.RETURN_PLAY_ACTOR_ID ?? "clinician_demo",
    actorRole: process.env.RETURN_PLAY_ACTOR_ROLE ?? "clinician",
    organizationId: process.env.RETURN_PLAY_ORGANIZATION_ID ?? "org_demo",
  };
}

function parseRuntimeEnv(value: string | undefined): ReturnPlayRuntimeEnv {
  if (!value) {
    return "local";
  }
  if (value === "local" || value === "test" || value === "staging" || value === "production") {
    return value;
  }
  throw new Error("RETURN_PLAY_ENV must be local, test, staging, or production.");
}

function parseDataMode(value: string | undefined): ReturnPlayDataMode {
  if (!value) {
    return "demo";
  }
  if (value === "demo" || value === "api" || value === "api-demo") {
    return value;
  }
  throw new Error("RETURN_PLAY_DATA_MODE must be demo, api, or api-demo.");
}
