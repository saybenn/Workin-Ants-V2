const allowedAppEnvironments = [
  "local",
  "development",
  "staging",
  "production",
] as const;

export type AppEnvironment = (typeof allowedAppEnvironments)[number];

type PublicEnv = {
  appEnv: AppEnvironment;
  appUrl: string;
};

function parseAppEnv(value: string | undefined): AppEnvironment {
  for (const environment of allowedAppEnvironments) {
    if (value === environment) {
      return environment;
    }
  }

  throw new Error(
    "Invalid or missing NEXT_PUBLIC_APP_ENV. Expected local, development, staging, or production.",
  );
}

function parseAppUrl(value: string | undefined): string {
  if (!value) {
    throw new Error("Missing required environment variable NEXT_PUBLIC_APP_URL.");
  }

  try {
    return new URL(value).toString().replace(/\/$/, "");
  } catch {
    throw new Error("Invalid NEXT_PUBLIC_APP_URL. Expected an absolute URL.");
  }
}

export const publicEnv: PublicEnv = {
  appEnv: parseAppEnv(process.env.NEXT_PUBLIC_APP_ENV),
  appUrl: parseAppUrl(process.env.NEXT_PUBLIC_APP_URL),
};

export const isProduction = publicEnv.appEnv === "production";
