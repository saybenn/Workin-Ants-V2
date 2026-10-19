import { publicEnv } from "@/lib/env";

type ServerEnv = {
  public: typeof publicEnv;
  hasSupabaseServiceRoleKey: boolean;
  hasStripeSecretKey: boolean;
  hasTypesenseAdminApiKey: boolean;
  hasBedrockApiKey: boolean;
};

export const serverEnv: ServerEnv = {
  public: publicEnv,
  hasSupabaseServiceRoleKey: Boolean(process.env.SUPABASE_SERVICE_ROLE_KEY),
  hasStripeSecretKey: Boolean(process.env.STRIPE_SECRET_KEY),
  hasTypesenseAdminApiKey: Boolean(process.env.TYPESENSE_ADMIN_API_KEY),
  hasBedrockApiKey: Boolean(process.env.BEDROCK_API_KEY),
};
