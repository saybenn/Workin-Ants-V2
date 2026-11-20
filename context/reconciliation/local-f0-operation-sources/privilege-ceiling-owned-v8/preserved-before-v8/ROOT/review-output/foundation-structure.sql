-- CreateSchema
CREATE SCHEMA IF NOT EXISTS "app";

-- CreateSchema
CREATE SCHEMA IF NOT EXISTS "platform";

-- CreateEnum
CREATE TYPE "app"."platform_role" AS ENUM ('user', 'admin', 'support');

-- CreateEnum
CREATE TYPE "app"."account_track" AS ENUM ('customer', 'candidate', 'professional');

-- CreateEnum
CREATE TYPE "app"."track_plan_status" AS ENUM ('draft', 'active', 'retired', 'archived');

-- CreateEnum
CREATE TYPE "app"."track_billing_model" AS ENUM ('free', 'subscription', 'commission', 'subscription_plus_commission', 'transaction_perk', 'manual');

-- CreateEnum
CREATE TYPE "app"."track_subscription_status" AS ENUM ('active', 'trialing', 'past_due', 'cancelled', 'expired', 'paused', 'incomplete', 'incomplete_expired');

-- CreateEnum
CREATE TYPE "app"."track_billing_provider" AS ENUM ('none', 'stripe', 'manual', 'comped', 'other');

-- CreateEnum
CREATE TYPE "app"."track_entitlement_value_type" AS ENUM ('boolean', 'integer', 'decimal', 'percent_bps', 'money_cents', 'string', 'json');

-- CreateEnum
CREATE TYPE "app"."track_entitlement_grant_status" AS ENUM ('active', 'expired', 'revoked', 'suspended', 'consumed');

-- CreateEnum
CREATE TYPE "app"."track_usage_event_type" AS ENUM ('job_application_submitted', 'candidate_search_boost_applied', 'application_view_tracked', 'buyer_fee_waived', 'priority_scheduling_used', 'professional_order_completed', 'professional_commission_applied', 'custom_domain_connected', 'live_streaming_used', 'internal_ad_campaign_created', 'other');

-- CreateEnum
CREATE TYPE "app"."track_usage_period" AS ENUM ('once', 'daily', 'monthly', 'yearly', 'lifetime', 'rolling_30_day');

-- CreateEnum
CREATE TYPE "app"."auth_provider_type" AS ENUM ('email_password', 'google', 'apple', 'passkey', 'magic_link', 'sso', 'other');

-- CreateEnum
CREATE TYPE "app"."auth_credential_status" AS ENUM ('active', 'disabled', 'revoked', 'expired', 'compromised');

-- CreateEnum
CREATE TYPE "app"."user_security_tier" AS ENUM ('standard', 'elevated', 'high_risk');

-- CreateEnum
CREATE TYPE "app"."profile_status" AS ENUM ('draft', 'active', 'paused', 'suspended', 'archived');

-- CreateEnum
CREATE TYPE "app"."consent_type" AS ENUM ('terms', 'privacy_policy', 'cookies', 'marketing', 'age_gate', 'calendar_sync', 'sweepstakes_rules', 'gamification_terms', 'reward_redemption_terms', 'healthcare_baa', 'fcra_background_check', 'license_verification', 'dmv_check', 'passkey_login', 'sms_mfa', 'sensitive_financial_access', 'account_recovery_identity_verification', 'phone_number_update', 'digital_goods_terms', 'digital_goods_refund_policy', 'digital_goods_license', 'child_directed_content_declaration', 'course_accessibility_disclosure', 'electronic_records_consent', 'electronic_signature_consent', 'agreement_execution_consent', 'manual_signature_opt_out', 'calendar_free_busy_access', 'calendar_writeback_access', 'calendar_disconnect_notice', 'web_push_notifications', 'pwa_install_guidance', 'subscription_terms', 'recurring_billing_authorization', 'plan_change_terms', 'commission_terms', 'buyer_fee_waiver_terms');

-- CreateEnum
CREATE TYPE "app"."privacy_request_type" AS ENUM ('access', 'export', 'erasure', 'correction', 'restriction');

-- CreateEnum
CREATE TYPE "app"."privacy_request_status" AS ENUM ('submitted', 'verifying_identity', 'verified', 'processing', 'completed', 'partially_completed', 'rejected', 'cancelled');

-- CreateEnum
CREATE TYPE "app"."age_gate_result" AS ENUM ('allowed', 'blocked_underage', 'blocked_region', 'manual_review');

-- CreateEnum
CREATE TYPE "app"."healthcare_access_decision" AS ENUM ('allowed', 'redacted', 'blocked', 'denied');

-- CreateEnum
CREATE TYPE "app"."data_sensitivity" AS ENUM ('normal', 'sensitive', 'healthcare', 'financial', 'identity_document', 'resume', 'legal_contract', 'private_message');

-- CreateEnum
CREATE TYPE "app"."access_audit_action" AS ENUM ('file_read', 'file_download', 'message_read', 'thread_opened', 'video_joined', 'location_revealed', 'privacy_export_generated', 'privacy_erasure_started', 'privacy_erasure_completed', 'healthcare_policy_checked', 'healthcare_payload_redacted', 'healthcare_payload_blocked', 'admin_redacted_view', 'admin_blocked_view', 'processor_balance_read', 'payout_account_read', 'tax_profile_read', 'tax_dashboard_opened', 'payout_request_started', 'sensitive_financial_step_up_verified', 'phone_number_changed', 'account_recovery_completed', 'course_video_started', 'course_video_completed', 'live_video_token_issued', 'digital_download_url_issued', 'digital_download_denied', 'digital_download_started', 'digital_download_completed', 'course_video_playback_granted', 'course_video_playback_denied', 'agreement_viewed', 'agreement_downloaded', 'agreement_signed', 'agreement_hash_verified', 'agreement_tamper_detected', 'agreement_manual_opt_out', 'media_signed_url_issued', 'media_signed_url_denied', 'media_upload_rejected', 'media_malware_detected', 'media_metadata_scrubbed', 'media_quarantined', 'media_promoted_to_ready', 'calendar_connection_started', 'calendar_connection_authorized', 'calendar_connection_revoked', 'calendar_free_busy_synced', 'booking_hold_created', 'booking_confirmed', 'booking_slot_lock_failed', 'booking_orchestration_started', 'booking_orchestration_failed');

-- CreateEnum
CREATE TYPE "app"."review_policy_state" AS ENUM ('draft', 'test_only', 'legal_approved');

-- CreateEnum
CREATE TYPE "app"."consent_disposition_kind" AS ENUM ('declined', 'withdrawn', 'superseded');

-- CreateEnum
CREATE TYPE "platform"."runtime_receipt_state" AS ENUM ('pending', 'committed', 'denied', 'unknown', 'fenced_noncommit');

-- CreateEnum
CREATE TYPE "platform"."runtime_message_kind" AS ENUM ('event', 'command');

-- CreateEnum
CREATE TYPE "platform"."runtime_work_state" AS ENUM ('pending', 'leased', 'completed', 'retry_wait', 'dead_letter', 'unknown');

-- CreateEnum
CREATE TYPE "platform"."runtime_reservation_state" AS ENUM ('active', 'committed', 'released', 'unknown');

-- CreateEnum
CREATE TYPE "app"."privacy_action_kind" AS ENUM ('export', 'erase', 'restrict', 'restore_marker');

-- CreateEnum
CREATE TYPE "app"."privacy_disposition_kind" AS ENUM ('completed', 'retained', 'omitted', 'failed', 'unknown');

-- CreateTable
CREATE TABLE "app"."consent_logs" (
    "id" UUID NOT NULL,
    "user_id" UUID NOT NULL,
    "type" "app"."consent_type" NOT NULL,
    "version" TEXT NOT NULL,
    "accepted_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "ip_hash" TEXT,
    "user_agent" TEXT,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "acceptance_key" TEXT NOT NULL,
    "fingerprint" CHAR(64) NOT NULL,
    "action_owner" TEXT NOT NULL,
    "action" TEXT NOT NULL,
    "context_kind" TEXT NOT NULL,
    "context_id" TEXT,
    "context_owner" TEXT NOT NULL,
    "presentation_hash" CHAR(64) NOT NULL,
    "content_revision_id" UUID NOT NULL,
    "presentation_id" UUID NOT NULL,
    "mutation_transaction_id" TEXT NOT NULL DEFAULT pg_current_xact_id()::text,

    CONSTRAINT "consent_logs_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."privacy_requests" (
    "id" UUID NOT NULL,
    "user_id" UUID NOT NULL,
    "type" "app"."privacy_request_type" NOT NULL,
    "status" "app"."privacy_request_status" NOT NULL DEFAULT 'submitted',
    "requested_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "verified_at" TIMESTAMPTZ(6),
    "due_at" TIMESTAMPTZ(6),
    "completed_at" TIMESTAMPTZ(6),
    "rejection_reason" TEXT,
    "admin_note" TEXT,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,
    "revision" BIGINT NOT NULL DEFAULT 0,
    "privacy_generation" BIGINT NOT NULL DEFAULT 0,
    "instruction_generation" BIGINT NOT NULL DEFAULT 0,
    "mutation_transaction_id" TEXT NOT NULL DEFAULT pg_current_xact_id()::text,

    CONSTRAINT "privacy_requests_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."age_gate_attempts" (
    "id" UUID NOT NULL,
    "user_id" UUID,
    "ip_hash" TEXT,
    "device_hash" TEXT,
    "region" TEXT,
    "result" "app"."age_gate_result" NOT NULL,
    "birth_year" INTEGER,
    "age_band" TEXT,
    "blocked_until" TIMESTAMPTZ(6),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "mutation_transaction_id" TEXT NOT NULL DEFAULT pg_current_xact_id()::text,

    CONSTRAINT "age_gate_attempts_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."age_gate_blocks" (
    "id" UUID NOT NULL,
    "ip_hash" TEXT,
    "device_hash" TEXT,
    "reason" TEXT NOT NULL,
    "blocked_until" TIMESTAMPTZ(6) NOT NULL,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "mutation_transaction_id" TEXT NOT NULL DEFAULT pg_current_xact_id()::text,

    CONSTRAINT "age_gate_blocks_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."access_audit_logs" (
    "id" UUID NOT NULL,
    "actor_user_id" UUID,
    "target_type" TEXT NOT NULL,
    "target_id" UUID NOT NULL,
    "action" "app"."access_audit_action" NOT NULL,
    "sensitivity" "app"."data_sensitivity" NOT NULL DEFAULT 'normal',
    "access_decision" "app"."healthcare_access_decision",
    "request_id" TEXT,
    "ip_hash" TEXT,
    "user_agent" TEXT,
    "previous_hash" TEXT,
    "entry_hash" TEXT,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "mutation_transaction_id" TEXT NOT NULL DEFAULT pg_current_xact_id()::text,

    CONSTRAINT "access_audit_logs_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."users" (
    "id" UUID NOT NULL,
    "email" TEXT,
    "handle" TEXT,
    "display_name" TEXT,
    "avatar_url" TEXT,
    "bio" TEXT,
    "city" TEXT,
    "state" TEXT,
    "country" TEXT,
    "is_public" BOOLEAN NOT NULL DEFAULT true,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,
    "privacy_erased_at" TIMESTAMPTZ(6),
    "privacy_erasure_status" TEXT,
    "revision" BIGINT NOT NULL DEFAULT 0,
    "privacy_generation" BIGINT NOT NULL DEFAULT 0,
    "mutation_transaction_id" TEXT NOT NULL DEFAULT pg_current_xact_id()::text,

    CONSTRAINT "users_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."user_roles" (
    "user_id" UUID NOT NULL,
    "role" "app"."platform_role" NOT NULL,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "revision" BIGINT NOT NULL DEFAULT 0,
    "mutation_transaction_id" TEXT NOT NULL DEFAULT pg_current_xact_id()::text,

    CONSTRAINT "user_roles_pkey" PRIMARY KEY ("user_id","role")
);

-- CreateTable
CREATE TABLE "app"."professional_profiles" (
    "id" UUID NOT NULL,
    "user_id" UUID NOT NULL,
    "slug" TEXT NOT NULL,
    "headline" TEXT,
    "bio" TEXT,
    "website_url" TEXT,
    "city" TEXT,
    "state" TEXT,
    "country" TEXT,
    "status" "app"."profile_status" NOT NULL DEFAULT 'draft',
    "rating_average" DOUBLE PRECISION,
    "rating_count" INTEGER NOT NULL DEFAULT 0,
    "stripe_account_id" TEXT,
    "stripe_ready" BOOLEAN NOT NULL DEFAULT false,
    "onboarding_complete_at" TIMESTAMPTZ(6),
    "default_currency" TEXT,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,
    "suspended_for_moderation_at" TIMESTAMPTZ(6),
    "trust_score" INTEGER,
    "verified_at" TIMESTAMPTZ(6),
    "verification_expires_at" TIMESTAMPTZ(6),
    "revision" BIGINT NOT NULL DEFAULT 0,
    "privacy_generation" BIGINT NOT NULL DEFAULT 0,
    "mutation_transaction_id" TEXT NOT NULL DEFAULT pg_current_xact_id()::text,

    CONSTRAINT "professional_profiles_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."customer_profiles" (
    "id" UUID NOT NULL,
    "user_id" UUID NOT NULL,
    "status" "app"."profile_status" NOT NULL DEFAULT 'active',
    "display_name" TEXT,
    "avatar_media_id" UUID,
    "city" TEXT,
    "state" TEXT,
    "country" TEXT,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,
    "archived_at" TIMESTAMPTZ(6),
    "revision" BIGINT NOT NULL DEFAULT 0,
    "privacy_generation" BIGINT NOT NULL DEFAULT 0,
    "mutation_transaction_id" TEXT NOT NULL DEFAULT pg_current_xact_id()::text,

    CONSTRAINT "customer_profiles_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."candidate_profiles" (
    "id" UUID NOT NULL,
    "user_id" UUID NOT NULL,
    "headline" TEXT,
    "portfolio_url" TEXT,
    "availability" TEXT,
    "city" TEXT,
    "state" TEXT,
    "country" TEXT,
    "status" "app"."profile_status" NOT NULL DEFAULT 'draft',
    "is_visible" BOOLEAN NOT NULL DEFAULT false,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,
    "trust_score" INTEGER,
    "verified_at" TIMESTAMPTZ(6),
    "verification_expires_at" TIMESTAMPTZ(6),
    "revision" BIGINT NOT NULL DEFAULT 0,
    "privacy_generation" BIGINT NOT NULL DEFAULT 0,
    "discovery_preference_revision" BIGINT NOT NULL DEFAULT 0,
    "discovery_enabled_at" TIMESTAMPTZ(6),
    "mutation_transaction_id" TEXT NOT NULL DEFAULT pg_current_xact_id()::text,

    CONSTRAINT "candidate_profiles_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."audit_events" (
    "id" UUID NOT NULL,
    "actor_user_id" UUID,
    "entity_type" TEXT NOT NULL,
    "entity_id" UUID,
    "action" TEXT NOT NULL,
    "metadata" JSONB,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "mutation_transaction_id" TEXT NOT NULL DEFAULT pg_current_xact_id()::text,

    CONSTRAINT "audit_events_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."user_security_profiles" (
    "id" UUID NOT NULL,
    "user_id" UUID NOT NULL,
    "security_tier" "app"."user_security_tier" NOT NULL DEFAULT 'standard',
    "phone_number_encrypted" TEXT,
    "phone_number_hash" TEXT,
    "phone_verified_at" TIMESTAMPTZ(6),
    "phone_last_changed_at" TIMESTAMPTZ(6),
    "passkeys_enabled" BOOLEAN NOT NULL DEFAULT false,
    "sms_mfa_enabled" BOOLEAN NOT NULL DEFAULT false,
    "backup_password_configured" BOOLEAN NOT NULL DEFAULT false,
    "sensitive_action_mfa_required" BOOLEAN NOT NULL DEFAULT true,
    "last_step_up_at" TIMESTAMPTZ(6),
    "last_sensitive_action_at" TIMESTAMPTZ(6),
    "locked_until" TIMESTAMPTZ(6),
    "lock_reason" TEXT,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,
    "revision" BIGINT NOT NULL DEFAULT 0,
    "security_generation" BIGINT NOT NULL DEFAULT 0,
    "mutation_transaction_id" TEXT NOT NULL DEFAULT pg_current_xact_id()::text,

    CONSTRAINT "user_security_profiles_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."auth_provider_accounts" (
    "id" UUID NOT NULL,
    "user_id" UUID NOT NULL,
    "security_profile_id" UUID,
    "provider_type" "app"."auth_provider_type" NOT NULL,
    "provider_user_id" TEXT,
    "provider_account_id" TEXT,
    "email" TEXT,
    "email_verified_at" TIMESTAMPTZ(6),
    "status" "app"."auth_credential_status" NOT NULL DEFAULT 'active',
    "linked_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "last_used_at" TIMESTAMPTZ(6),
    "revoked_at" TIMESTAMPTZ(6),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,
    "revision" BIGINT NOT NULL DEFAULT 0,
    "mutation_transaction_id" TEXT NOT NULL DEFAULT pg_current_xact_id()::text,

    CONSTRAINT "auth_provider_accounts_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."track_plans" (
    "id" UUID NOT NULL,
    "track" "app"."account_track" NOT NULL,
    "key" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "status" "app"."track_plan_status" NOT NULL DEFAULT 'draft',
    "billing_model" "app"."track_billing_model" NOT NULL,
    "monthly_price_cents" INTEGER,
    "currency" TEXT NOT NULL DEFAULT 'usd',
    "description" TEXT,
    "display_order" INTEGER NOT NULL DEFAULT 0,
    "metadata" JSONB,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,
    "revision" BIGINT NOT NULL DEFAULT 0,
    "version" TEXT NOT NULL,
    "content_hash" CHAR(64) NOT NULL,
    "mutation_transaction_id" TEXT NOT NULL DEFAULT pg_current_xact_id()::text,

    CONSTRAINT "track_plans_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."track_entitlement_definitions" (
    "id" UUID NOT NULL,
    "key" TEXT NOT NULL,
    "label" TEXT NOT NULL,
    "description" TEXT,
    "value_type" "app"."track_entitlement_value_type" NOT NULL,
    "track" "app"."account_track",
    "is_active" BOOLEAN NOT NULL DEFAULT true,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,
    "revision" BIGINT NOT NULL DEFAULT 0,
    "mutation_transaction_id" TEXT NOT NULL DEFAULT pg_current_xact_id()::text,

    CONSTRAINT "track_entitlement_definitions_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."track_plan_entitlements" (
    "id" UUID NOT NULL,
    "plan_id" UUID NOT NULL,
    "entitlement_id" UUID NOT NULL,
    "value_type" "app"."track_entitlement_value_type" NOT NULL,
    "boolean_value" BOOLEAN,
    "int_value" INTEGER,
    "decimal_value" DOUBLE PRECISION,
    "string_value" TEXT,
    "json_value" JSONB,
    "usage_period" "app"."track_usage_period",
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,
    "revision" BIGINT NOT NULL DEFAULT 0,
    "mutation_transaction_id" TEXT NOT NULL DEFAULT pg_current_xact_id()::text,

    CONSTRAINT "track_plan_entitlements_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."track_subscriptions" (
    "id" UUID NOT NULL,
    "user_id" UUID NOT NULL,
    "plan_id" UUID NOT NULL,
    "track" "app"."account_track" NOT NULL,
    "customer_profile_id" UUID,
    "candidate_profile_id" UUID,
    "professional_profile_id" UUID,
    "status" "app"."track_subscription_status" NOT NULL DEFAULT 'active',
    "provider" "app"."track_billing_provider" NOT NULL DEFAULT 'none',
    "provider_customer_id" TEXT,
    "provider_subscription_id" TEXT,
    "provider_price_id" TEXT,
    "current_period_start" TIMESTAMPTZ(6),
    "current_period_end" TIMESTAMPTZ(6),
    "trial_ends_at" TIMESTAMPTZ(6),
    "cancelled_at" TIMESTAMPTZ(6),
    "ended_at" TIMESTAMPTZ(6),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,
    "revision" BIGINT NOT NULL DEFAULT 0,
    "mutation_transaction_id" TEXT NOT NULL DEFAULT pg_current_xact_id()::text,

    CONSTRAINT "track_subscriptions_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."track_entitlement_grants" (
    "id" UUID NOT NULL,
    "user_id" UUID NOT NULL,
    "subscription_id" UUID,
    "entitlement_id" UUID NOT NULL,
    "track" "app"."account_track" NOT NULL,
    "customer_profile_id" UUID,
    "candidate_profile_id" UUID,
    "professional_profile_id" UUID,
    "status" "app"."track_entitlement_grant_status" NOT NULL DEFAULT 'active',
    "value_type" "app"."track_entitlement_value_type" NOT NULL,
    "boolean_value" BOOLEAN,
    "int_value" INTEGER,
    "decimal_value" DOUBLE PRECISION,
    "string_value" TEXT,
    "json_value" JSONB,
    "starts_at" TIMESTAMPTZ(6),
    "expires_at" TIMESTAMPTZ(6),
    "revoked_at" TIMESTAMPTZ(6),
    "revoke_reason" TEXT,
    "source_plan_id" UUID,
    "source_event_id" UUID,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,
    "revision" BIGINT NOT NULL DEFAULT 0,
    "mutation_transaction_id" TEXT NOT NULL DEFAULT pg_current_xact_id()::text,

    CONSTRAINT "track_entitlement_grants_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."track_usage_events" (
    "id" UUID NOT NULL,
    "user_id" UUID NOT NULL,
    "subscription_id" UUID,
    "entitlement_grant_id" UUID,
    "entitlement_id" UUID,
    "track" "app"."account_track" NOT NULL,
    "type" "app"."track_usage_event_type" NOT NULL,
    "customer_profile_id" UUID,
    "candidate_profile_id" UUID,
    "professional_profile_id" UUID,
    "target_type" TEXT,
    "target_id" UUID,
    "quantity" INTEGER NOT NULL DEFAULT 1,
    "occurred_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "metadata" JSONB,
    "semantic_effect_key" TEXT NOT NULL,
    "source_revision" BIGINT NOT NULL,
    "source_owner" TEXT NOT NULL,
    "source_id" TEXT NOT NULL,
    "accepted_at" TIMESTAMPTZ(6) NOT NULL,
    "period_start" TIMESTAMPTZ(6) NOT NULL,
    "period_end" TIMESTAMPTZ(6) NOT NULL,
    "effect_receipt_id" UUID NOT NULL,
    "mutation_transaction_id" TEXT NOT NULL DEFAULT pg_current_xact_id()::text,

    CONSTRAINT "track_usage_events_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."track_usage_counters" (
    "id" UUID NOT NULL,
    "user_id" UUID NOT NULL,
    "subscription_id" UUID,
    "entitlement_grant_id" UUID,
    "entitlement_id" UUID NOT NULL,
    "track" "app"."account_track" NOT NULL,
    "period" "app"."track_usage_period" NOT NULL,
    "customer_profile_id" UUID,
    "candidate_profile_id" UUID,
    "professional_profile_id" UUID,
    "period_start" TIMESTAMPTZ(6) NOT NULL,
    "period_end" TIMESTAMPTZ(6) NOT NULL,
    "used_quantity" INTEGER NOT NULL DEFAULT 0,
    "limit_quantity" INTEGER,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "revision" BIGINT NOT NULL DEFAULT 0,
    "source_revision" BIGINT NOT NULL,
    "mutation_transaction_id" TEXT NOT NULL DEFAULT pg_current_xact_id()::text,

    CONSTRAINT "track_usage_counters_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."track_subscription_events" (
    "id" UUID NOT NULL,
    "subscription_id" UUID,
    "plan_id" UUID,
    "user_id" UUID NOT NULL,
    "name" TEXT NOT NULL,
    "from_status" "app"."track_subscription_status",
    "to_status" "app"."track_subscription_status",
    "provider" "app"."track_billing_provider",
    "provider_event_id" TEXT,
    "metadata" JSONB,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "mutation_transaction_id" TEXT NOT NULL DEFAULT pg_current_xact_id()::text,

    CONSTRAINT "track_subscription_events_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."consent_content_revision" (
    "id" UUID NOT NULL,
    "type" "app"."consent_type" NOT NULL,
    "version" TEXT NOT NULL,
    "locale" TEXT NOT NULL,
    "jurisdiction_scope" TEXT NOT NULL,
    "content_text" TEXT NOT NULL,
    "content_hash" CHAR(64) NOT NULL,
    "review_state" "app"."review_policy_state" NOT NULL DEFAULT 'draft',
    "legal_approval_ref" TEXT,
    "effective_from" TIMESTAMPTZ(6) NOT NULL,
    "effective_until" TIMESTAMPTZ(6),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "mutation_transaction_id" TEXT NOT NULL DEFAULT pg_current_xact_id()::text,

    CONSTRAINT "consent_content_revision_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."consent_presentation" (
    "id" UUID NOT NULL,
    "content_revision_id" UUID NOT NULL,
    "user_id" UUID NOT NULL,
    "action_owner" TEXT NOT NULL,
    "action" TEXT NOT NULL,
    "render_version" TEXT NOT NULL,
    "rendered_text" TEXT NOT NULL,
    "rendered_hash" CHAR(64) NOT NULL,
    "context_owner" TEXT NOT NULL,
    "context_kind" TEXT NOT NULL,
    "context_id" TEXT,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "mutation_transaction_id" TEXT NOT NULL DEFAULT pg_current_xact_id()::text,

    CONSTRAINT "consent_presentation_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."consent_disposition" (
    "id" UUID NOT NULL,
    "proof_id" UUID,
    "user_id" UUID NOT NULL,
    "presentation_id" UUID NOT NULL,
    "kind" "app"."consent_disposition_kind" NOT NULL,
    "semantic_key" TEXT NOT NULL,
    "fingerprint" CHAR(64) NOT NULL,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "mutation_transaction_id" TEXT NOT NULL DEFAULT pg_current_xact_id()::text,

    CONSTRAINT "consent_disposition_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "platform"."database_action_grant" (
    "id" UUID NOT NULL,
    "token_hash" CHAR(64) NOT NULL,
    "issuer_service" TEXT NOT NULL,
    "principal_user_id" UUID,
    "service_principal" TEXT,
    "database_login_role" TEXT NOT NULL,
    "owner_module_id" TEXT NOT NULL,
    "action" TEXT NOT NULL,
    "purpose" TEXT NOT NULL,
    "target_kind" TEXT NOT NULL,
    "target_id" TEXT NOT NULL,
    "allowed_fields" TEXT[],
    "policy_version" TEXT NOT NULL,
    "security_generation" BIGINT NOT NULL,
    "source_generation" BIGINT NOT NULL,
    "backend_pid" INTEGER NOT NULL,
    "transaction_id" TEXT NOT NULL,
    "expires_at" TIMESTAMPTZ(6) NOT NULL,
    "revoked_at" TIMESTAMPTZ(6),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "mutation_transaction_id" TEXT NOT NULL DEFAULT pg_current_xact_id()::text,

    CONSTRAINT "database_action_grant_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "platform"."runtime_command_receipt" (
    "id" UUID NOT NULL,
    "owner_module_id" TEXT NOT NULL,
    "operation" TEXT NOT NULL,
    "subject_scope" TEXT NOT NULL,
    "semantic_key" TEXT NOT NULL,
    "fingerprint" CHAR(64) NOT NULL,
    "state" "platform"."runtime_receipt_state" NOT NULL DEFAULT 'pending',
    "source_revision" BIGINT,
    "result_schema_id" TEXT NOT NULL,
    "result_schema_version" TEXT NOT NULL,
    "result_digest" CHAR(64),
    "result_body" JSONB,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "mutation_transaction_id" TEXT NOT NULL DEFAULT pg_current_xact_id()::text,

    CONSTRAINT "runtime_command_receipt_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "platform"."runtime_outbox_message" (
    "id" UUID NOT NULL,
    "command_receipt_id" UUID NOT NULL,
    "kind" "platform"."runtime_message_kind" NOT NULL,
    "producer_owner" TEXT NOT NULL,
    "aggregate_kind" TEXT NOT NULL,
    "aggregate_id" TEXT NOT NULL,
    "source_revision" BIGINT NOT NULL,
    "source_generation" BIGINT NOT NULL,
    "ordinal" INTEGER NOT NULL,
    "name" TEXT NOT NULL,
    "schema_version" TEXT NOT NULL,
    "payload_schema_id" TEXT NOT NULL,
    "payload_hash" CHAR(64) NOT NULL,
    "payload" JSONB NOT NULL,
    "correlation_id" TEXT NOT NULL,
    "causation_id" TEXT NOT NULL,
    "correction_of_id" UUID,
    "occurred_at" TIMESTAMPTZ(6) NOT NULL,
    "effective_at" TIMESTAMPTZ(6) NOT NULL,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "mutation_transaction_id" TEXT NOT NULL DEFAULT pg_current_xact_id()::text,

    CONSTRAINT "runtime_outbox_message_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "platform"."runtime_effect_receipt" (
    "id" UUID NOT NULL,
    "command_receipt_id" UUID,
    "owner_module_id" TEXT NOT NULL,
    "operation" TEXT NOT NULL,
    "subject_scope" TEXT NOT NULL,
    "semantic_effect_key" TEXT NOT NULL,
    "fingerprint" CHAR(64) NOT NULL,
    "state" "platform"."runtime_receipt_state" NOT NULL DEFAULT 'pending',
    "source_revision" BIGINT,
    "fence" BIGINT NOT NULL DEFAULT 0,
    "result_schema_id" TEXT NOT NULL,
    "result_hash" CHAR(64),
    "committed_at" TIMESTAMPTZ(6),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "mutation_transaction_id" TEXT NOT NULL DEFAULT pg_current_xact_id()::text,

    CONSTRAINT "runtime_effect_receipt_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "platform"."runtime_work_item" (
    "id" UUID NOT NULL,
    "outbox_message_id" UUID NOT NULL,
    "handler_name" TEXT NOT NULL,
    "semantic_work_key" TEXT NOT NULL,
    "state" "platform"."runtime_work_state" NOT NULL DEFAULT 'pending',
    "fence" BIGINT NOT NULL DEFAULT 0,
    "lease_token_hash" CHAR(64),
    "lease_expires_at" TIMESTAMPTZ(6),
    "attempt_count" INTEGER NOT NULL DEFAULT 0,
    "next_attempt_at" TIMESTAMPTZ(6),
    "effect_receipt_id" UUID,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "mutation_transaction_id" TEXT NOT NULL DEFAULT pg_current_xact_id()::text,

    CONSTRAINT "runtime_work_item_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "platform"."runtime_attempt" (
    "id" UUID NOT NULL,
    "work_item_id" UUID NOT NULL,
    "attempt_number" INTEGER NOT NULL,
    "fence" BIGINT NOT NULL,
    "worker_id" TEXT NOT NULL,
    "result" "platform"."runtime_receipt_state" NOT NULL,
    "reason_code" TEXT NOT NULL,
    "started_at" TIMESTAMPTZ(6) NOT NULL,
    "finished_at" TIMESTAMPTZ(6) NOT NULL,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "mutation_transaction_id" TEXT NOT NULL DEFAULT pg_current_xact_id()::text,

    CONSTRAINT "runtime_attempt_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "platform"."runtime_inbox_receipt" (
    "id" UUID NOT NULL,
    "outbox_message_id" UUID NOT NULL,
    "consumer_owner" TEXT NOT NULL,
    "handler_name" TEXT NOT NULL,
    "payload_hash" CHAR(64) NOT NULL,
    "effect_receipt_id" UUID NOT NULL,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "mutation_transaction_id" TEXT NOT NULL DEFAULT pg_current_xact_id()::text,

    CONSTRAINT "runtime_inbox_receipt_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "platform"."runtime_reservation" (
    "id" UUID NOT NULL,
    "command_receipt_id" UUID NOT NULL,
    "owner_module_id" TEXT NOT NULL,
    "resource_kind" TEXT NOT NULL,
    "resource_key" TEXT NOT NULL,
    "semantic_key" TEXT NOT NULL,
    "quantity" INTEGER NOT NULL,
    "state" "platform"."runtime_reservation_state" NOT NULL DEFAULT 'active',
    "fence" BIGINT NOT NULL DEFAULT 0,
    "effect_receipt_id" UUID,
    "expires_at" TIMESTAMPTZ(6),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "mutation_transaction_id" TEXT NOT NULL DEFAULT pg_current_xact_id()::text,

    CONSTRAINT "runtime_reservation_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "platform"."owner_mutation_evidence" (
    "id" UUID NOT NULL,
    "command_receipt_id" UUID NOT NULL,
    "owner_module_id" TEXT NOT NULL,
    "aggregate_kind" TEXT NOT NULL,
    "aggregate_id" TEXT NOT NULL,
    "previous_revision" BIGINT,
    "committed_revision" BIGINT NOT NULL,
    "action" TEXT NOT NULL,
    "decision_ref" TEXT NOT NULL,
    "evidence_schema_id" TEXT NOT NULL,
    "evidence_schema_version" TEXT NOT NULL,
    "evidence_digest" CHAR(64) NOT NULL,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "evidence_body" JSONB NOT NULL,
    "mutation_transaction_id" TEXT NOT NULL DEFAULT pg_current_xact_id()::text,

    CONSTRAINT "owner_mutation_evidence_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."customer_profile_lifecycle_event" (
    "id" UUID NOT NULL,
    "customer_profile_id" UUID NOT NULL,
    "command_receipt_id" UUID NOT NULL,
    "source_revision" BIGINT NOT NULL,
    "from_status" "app"."profile_status",
    "to_status" "app"."profile_status" NOT NULL,
    "name" TEXT NOT NULL,
    "actor_user_id" UUID NOT NULL,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "mutation_transaction_id" TEXT NOT NULL DEFAULT pg_current_xact_id()::text,

    CONSTRAINT "customer_profile_lifecycle_event_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."track_base_selection" (
    "id" UUID NOT NULL,
    "user_id" UUID NOT NULL,
    "track" "app"."account_track" NOT NULL,
    "customer_profile_id" UUID,
    "candidate_profile_id" UUID,
    "professional_profile_id" UUID,
    "subscription_id" UUID NOT NULL,
    "revision" BIGINT NOT NULL DEFAULT 0,
    "source_generation" BIGINT NOT NULL DEFAULT 0,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "mutation_transaction_id" TEXT NOT NULL DEFAULT pg_current_xact_id()::text,

    CONSTRAINT "track_base_selection_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."track_enrollment_receipt" (
    "id" UUID NOT NULL,
    "user_id" UUID NOT NULL,
    "track" "app"."account_track" NOT NULL,
    "profile_id" UUID NOT NULL,
    "source_owner" TEXT NOT NULL,
    "source_creation_revision" BIGINT NOT NULL,
    "selection_id" UUID NOT NULL,
    "selection_revision" BIGINT NOT NULL,
    "semantic_key" TEXT NOT NULL,
    "fingerprint" CHAR(64) NOT NULL,
    "result_code" TEXT NOT NULL,
    "effect_receipt_id" UUID NOT NULL,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "mutation_transaction_id" TEXT NOT NULL DEFAULT pg_current_xact_id()::text,

    CONSTRAINT "track_enrollment_receipt_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."track_usage_reservation" (
    "id" UUID NOT NULL,
    "user_id" UUID NOT NULL,
    "entitlement_id" UUID NOT NULL,
    "period_start" TIMESTAMPTZ(6) NOT NULL,
    "period_end" TIMESTAMPTZ(6) NOT NULL,
    "quantity" INTEGER NOT NULL,
    "semantic_key" TEXT NOT NULL,
    "reservation_id" UUID NOT NULL,
    "accepted_source_owner" TEXT NOT NULL,
    "accepted_source_id" TEXT,
    "accepted_at" TIMESTAMPTZ(6),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "revision" BIGINT NOT NULL DEFAULT 0,
    "mutation_transaction_id" TEXT NOT NULL DEFAULT pg_current_xact_id()::text,

    CONSTRAINT "track_usage_reservation_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."privacy_target_instruction" (
    "id" UUID NOT NULL,
    "privacy_request_id" UUID NOT NULL,
    "owner_module_id" TEXT NOT NULL,
    "target_kind" TEXT NOT NULL,
    "source_id" TEXT NOT NULL,
    "source_revision" TEXT NOT NULL,
    "action" "app"."privacy_action_kind" NOT NULL,
    "generation" BIGINT NOT NULL,
    "field_map_version" TEXT NOT NULL,
    "executor_version" TEXT NOT NULL,
    "descriptor_hash" CHAR(64) NOT NULL,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "mutation_transaction_id" TEXT NOT NULL DEFAULT pg_current_xact_id()::text,

    CONSTRAINT "privacy_target_instruction_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."privacy_owner_receipt" (
    "id" UUID NOT NULL,
    "instruction_id" UUID NOT NULL,
    "generation" BIGINT NOT NULL,
    "disposition" "app"."privacy_disposition_kind" NOT NULL,
    "execution_receipt_ref" TEXT NOT NULL,
    "legal_basis_ref" TEXT,
    "artifact_digest" CHAR(64),
    "artifact_version" TEXT,
    "result_schema_version" TEXT NOT NULL,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "mutation_transaction_id" TEXT NOT NULL DEFAULT pg_current_xact_id()::text,

    CONSTRAINT "privacy_owner_receipt_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."privacy_restore_marker" (
    "id" UUID NOT NULL,
    "owner_module_id" TEXT NOT NULL,
    "target_kind" TEXT NOT NULL,
    "source_id" TEXT NOT NULL,
    "generation" BIGINT NOT NULL,
    "action" "app"."privacy_action_kind" NOT NULL,
    "source_receipt_id" UUID NOT NULL,
    "restore_point_ref" TEXT,
    "applied_at" TIMESTAMPTZ(6),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "revision" BIGINT NOT NULL DEFAULT 0,
    "mutation_transaction_id" TEXT NOT NULL DEFAULT pg_current_xact_id()::text,

    CONSTRAINT "privacy_restore_marker_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "consent_logs_user_id_type_accepted_at_idx" ON "app"."consent_logs"("user_id", "type", "accepted_at");

-- CreateIndex
CREATE INDEX "consent_logs_type_version_idx" ON "app"."consent_logs"("type", "version");

-- CreateIndex
CREATE UNIQUE INDEX "consent_logs_user_id_acceptance_key_key" ON "app"."consent_logs"("user_id", "acceptance_key");

-- CreateIndex
CREATE INDEX "privacy_requests_user_id_status_idx" ON "app"."privacy_requests"("user_id", "status");

-- CreateIndex
CREATE INDEX "privacy_requests_type_status_idx" ON "app"."privacy_requests"("type", "status");

-- CreateIndex
CREATE INDEX "privacy_requests_due_at_idx" ON "app"."privacy_requests"("due_at");

-- CreateIndex
CREATE INDEX "age_gate_attempts_user_id_created_at_idx" ON "app"."age_gate_attempts"("user_id", "created_at");

-- CreateIndex
CREATE INDEX "age_gate_attempts_ip_hash_created_at_idx" ON "app"."age_gate_attempts"("ip_hash", "created_at");

-- CreateIndex
CREATE INDEX "age_gate_attempts_device_hash_created_at_idx" ON "app"."age_gate_attempts"("device_hash", "created_at");

-- CreateIndex
CREATE INDEX "age_gate_attempts_result_created_at_idx" ON "app"."age_gate_attempts"("result", "created_at");

-- CreateIndex
CREATE INDEX "age_gate_attempts_blocked_until_idx" ON "app"."age_gate_attempts"("blocked_until");

-- CreateIndex
CREATE INDEX "age_gate_blocks_ip_hash_blocked_until_idx" ON "app"."age_gate_blocks"("ip_hash", "blocked_until");

-- CreateIndex
CREATE INDEX "age_gate_blocks_device_hash_blocked_until_idx" ON "app"."age_gate_blocks"("device_hash", "blocked_until");

-- CreateIndex
CREATE INDEX "access_audit_logs_actor_user_id_created_at_idx" ON "app"."access_audit_logs"("actor_user_id", "created_at");

-- CreateIndex
CREATE INDEX "access_audit_logs_target_type_target_id_idx" ON "app"."access_audit_logs"("target_type", "target_id");

-- CreateIndex
CREATE INDEX "access_audit_logs_sensitivity_created_at_idx" ON "app"."access_audit_logs"("sensitivity", "created_at");

-- CreateIndex
CREATE INDEX "access_audit_logs_action_created_at_idx" ON "app"."access_audit_logs"("action", "created_at");

-- CreateIndex
CREATE INDEX "access_audit_logs_request_id_idx" ON "app"."access_audit_logs"("request_id");

-- CreateIndex
CREATE UNIQUE INDEX "users_email_key" ON "app"."users"("email");

-- CreateIndex
CREATE UNIQUE INDEX "users_handle_key" ON "app"."users"("handle");

-- CreateIndex
CREATE INDEX "users_is_public_idx" ON "app"."users"("is_public");

-- CreateIndex
CREATE INDEX "users_city_state_country_idx" ON "app"."users"("city", "state", "country");

-- CreateIndex
CREATE INDEX "user_roles_role_idx" ON "app"."user_roles"("role");

-- CreateIndex
CREATE UNIQUE INDEX "professional_profiles_user_id_key" ON "app"."professional_profiles"("user_id");

-- CreateIndex
CREATE UNIQUE INDEX "professional_profiles_slug_key" ON "app"."professional_profiles"("slug");

-- CreateIndex
CREATE INDEX "professional_profiles_status_idx" ON "app"."professional_profiles"("status");

-- CreateIndex
CREATE INDEX "professional_profiles_city_state_country_idx" ON "app"."professional_profiles"("city", "state", "country");

-- CreateIndex
CREATE INDEX "professional_profiles_stripe_account_id_idx" ON "app"."professional_profiles"("stripe_account_id");

-- CreateIndex
CREATE UNIQUE INDEX "customer_profiles_user_id_key" ON "app"."customer_profiles"("user_id");

-- CreateIndex
CREATE INDEX "customer_profiles_status_idx" ON "app"."customer_profiles"("status");

-- CreateIndex
CREATE INDEX "customer_profiles_city_state_country_idx" ON "app"."customer_profiles"("city", "state", "country");

-- CreateIndex
CREATE UNIQUE INDEX "candidate_profiles_user_id_key" ON "app"."candidate_profiles"("user_id");

-- CreateIndex
CREATE INDEX "candidate_profiles_status_is_visible_idx" ON "app"."candidate_profiles"("status", "is_visible");

-- CreateIndex
CREATE INDEX "candidate_profiles_country_state_city_idx" ON "app"."candidate_profiles"("country", "state", "city");

-- CreateIndex
CREATE INDEX "audit_events_actor_user_id_idx" ON "app"."audit_events"("actor_user_id");

-- CreateIndex
CREATE INDEX "audit_events_entity_type_entity_id_idx" ON "app"."audit_events"("entity_type", "entity_id");

-- CreateIndex
CREATE INDEX "audit_events_action_created_at_idx" ON "app"."audit_events"("action", "created_at");

-- CreateIndex
CREATE UNIQUE INDEX "user_security_profiles_user_id_key" ON "app"."user_security_profiles"("user_id");

-- CreateIndex
CREATE INDEX "user_security_profiles_security_tier_idx" ON "app"."user_security_profiles"("security_tier");

-- CreateIndex
CREATE INDEX "user_security_profiles_phone_number_hash_idx" ON "app"."user_security_profiles"("phone_number_hash");

-- CreateIndex
CREATE INDEX "user_security_profiles_locked_until_idx" ON "app"."user_security_profiles"("locked_until");

-- CreateIndex
CREATE INDEX "auth_provider_accounts_user_id_provider_type_idx" ON "app"."auth_provider_accounts"("user_id", "provider_type");

-- CreateIndex
CREATE INDEX "auth_provider_accounts_provider_type_provider_user_id_idx" ON "app"."auth_provider_accounts"("provider_type", "provider_user_id");

-- CreateIndex
CREATE INDEX "auth_provider_accounts_provider_type_provider_account_id_idx" ON "app"."auth_provider_accounts"("provider_type", "provider_account_id");

-- CreateIndex
CREATE INDEX "auth_provider_accounts_status_idx" ON "app"."auth_provider_accounts"("status");

-- CreateIndex
CREATE INDEX "track_plans_track_status_idx" ON "app"."track_plans"("track", "status");

-- CreateIndex
CREATE UNIQUE INDEX "track_plans_track_key_version_key" ON "app"."track_plans"("track", "key", "version");

-- CreateIndex
CREATE UNIQUE INDEX "track_entitlement_definitions_key_key" ON "app"."track_entitlement_definitions"("key");

-- CreateIndex
CREATE INDEX "track_entitlement_definitions_track_is_active_idx" ON "app"."track_entitlement_definitions"("track", "is_active");

-- CreateIndex
CREATE INDEX "track_plan_entitlements_entitlement_id_idx" ON "app"."track_plan_entitlements"("entitlement_id");

-- CreateIndex
CREATE UNIQUE INDEX "track_plan_entitlements_plan_id_entitlement_id_key" ON "app"."track_plan_entitlements"("plan_id", "entitlement_id");

-- CreateIndex
CREATE INDEX "track_subscriptions_user_id_track_status_idx" ON "app"."track_subscriptions"("user_id", "track", "status");

-- CreateIndex
CREATE INDEX "track_subscriptions_plan_id_idx" ON "app"."track_subscriptions"("plan_id");

-- CreateIndex
CREATE INDEX "track_subscriptions_customer_profile_id_idx" ON "app"."track_subscriptions"("customer_profile_id");

-- CreateIndex
CREATE INDEX "track_subscriptions_candidate_profile_id_idx" ON "app"."track_subscriptions"("candidate_profile_id");

-- CreateIndex
CREATE INDEX "track_subscriptions_professional_profile_id_idx" ON "app"."track_subscriptions"("professional_profile_id");

-- CreateIndex
CREATE INDEX "track_subscriptions_provider_provider_subscription_id_idx" ON "app"."track_subscriptions"("provider", "provider_subscription_id");

-- CreateIndex
CREATE INDEX "track_subscriptions_current_period_end_idx" ON "app"."track_subscriptions"("current_period_end");

-- CreateIndex
CREATE INDEX "track_entitlement_grants_user_id_track_status_idx" ON "app"."track_entitlement_grants"("user_id", "track", "status");

-- CreateIndex
CREATE INDEX "track_entitlement_grants_subscription_id_idx" ON "app"."track_entitlement_grants"("subscription_id");

-- CreateIndex
CREATE INDEX "track_entitlement_grants_entitlement_id_status_idx" ON "app"."track_entitlement_grants"("entitlement_id", "status");

-- CreateIndex
CREATE INDEX "track_entitlement_grants_customer_profile_id_status_idx" ON "app"."track_entitlement_grants"("customer_profile_id", "status");

-- CreateIndex
CREATE INDEX "track_entitlement_grants_candidate_profile_id_status_idx" ON "app"."track_entitlement_grants"("candidate_profile_id", "status");

-- CreateIndex
CREATE INDEX "track_entitlement_grants_professional_profile_id_status_idx" ON "app"."track_entitlement_grants"("professional_profile_id", "status");

-- CreateIndex
CREATE INDEX "track_entitlement_grants_expires_at_idx" ON "app"."track_entitlement_grants"("expires_at");

-- CreateIndex
CREATE UNIQUE INDEX "track_usage_events_semantic_effect_key_key" ON "app"."track_usage_events"("semantic_effect_key");

-- CreateIndex
CREATE INDEX "track_usage_events_user_id_type_occurred_at_idx" ON "app"."track_usage_events"("user_id", "type", "occurred_at");

-- CreateIndex
CREATE INDEX "track_usage_events_candidate_profile_id_type_occurred_at_idx" ON "app"."track_usage_events"("candidate_profile_id", "type", "occurred_at");

-- CreateIndex
CREATE INDEX "track_usage_events_customer_profile_id_type_occurred_at_idx" ON "app"."track_usage_events"("customer_profile_id", "type", "occurred_at");

-- CreateIndex
CREATE INDEX "track_usage_events_professional_profile_id_type_occurred_at_idx" ON "app"."track_usage_events"("professional_profile_id", "type", "occurred_at");

-- CreateIndex
CREATE INDEX "track_usage_events_target_type_target_id_idx" ON "app"."track_usage_events"("target_type", "target_id");

-- CreateIndex
CREATE INDEX "track_usage_counters_candidate_profile_id_period_start_peri_idx" ON "app"."track_usage_counters"("candidate_profile_id", "period_start", "period_end");

-- CreateIndex
CREATE INDEX "track_usage_counters_customer_profile_id_period_start_perio_idx" ON "app"."track_usage_counters"("customer_profile_id", "period_start", "period_end");

-- CreateIndex
CREATE INDEX "track_usage_counters_professional_profile_id_period_start_p_idx" ON "app"."track_usage_counters"("professional_profile_id", "period_start", "period_end");

-- CreateIndex
CREATE UNIQUE INDEX "track_usage_counters_entitlement_id_track_user_id_period_st_key" ON "app"."track_usage_counters"("entitlement_id", "track", "user_id", "period_start", "period_end");

-- CreateIndex
CREATE INDEX "track_subscription_events_subscription_id_created_at_idx" ON "app"."track_subscription_events"("subscription_id", "created_at");

-- CreateIndex
CREATE INDEX "track_subscription_events_plan_id_idx" ON "app"."track_subscription_events"("plan_id");

-- CreateIndex
CREATE INDEX "track_subscription_events_user_id_created_at_idx" ON "app"."track_subscription_events"("user_id", "created_at");

-- CreateIndex
CREATE INDEX "track_subscription_events_provider_provider_event_id_idx" ON "app"."track_subscription_events"("provider", "provider_event_id");

-- CreateIndex
CREATE UNIQUE INDEX "consent_content_revision_type_version_locale_jurisdiction_s_key" ON "app"."consent_content_revision"("type", "version", "locale", "jurisdiction_scope");

-- CreateIndex
CREATE UNIQUE INDEX "consent_presentation_id_content_revision_id_user_id_key" ON "app"."consent_presentation"("id", "content_revision_id", "user_id");

-- CreateIndex
CREATE UNIQUE INDEX "consent_disposition_user_id_semantic_key_key" ON "app"."consent_disposition"("user_id", "semantic_key");

-- CreateIndex
CREATE UNIQUE INDEX "database_action_grant_token_hash_key" ON "platform"."database_action_grant"("token_hash");

-- CreateIndex
CREATE INDEX "database_action_grant_expires_at_idx" ON "platform"."database_action_grant"("expires_at");

-- CreateIndex
CREATE UNIQUE INDEX "runtime_command_receipt_owner_module_id_operation_subject_s_key" ON "platform"."runtime_command_receipt"("owner_module_id", "operation", "subject_scope", "semantic_key");

-- CreateIndex
CREATE UNIQUE INDEX "runtime_outbox_message_producer_owner_aggregate_kind_aggreg_key" ON "platform"."runtime_outbox_message"("producer_owner", "aggregate_kind", "aggregate_id", "source_revision", "ordinal");

-- CreateIndex
CREATE UNIQUE INDEX "runtime_effect_receipt_owner_module_id_operation_subject_sc_key" ON "platform"."runtime_effect_receipt"("owner_module_id", "operation", "subject_scope", "semantic_effect_key");

-- CreateIndex
CREATE UNIQUE INDEX "runtime_work_item_semantic_work_key_key" ON "platform"."runtime_work_item"("semantic_work_key");

-- CreateIndex
CREATE INDEX "runtime_work_item_state_next_attempt_at_idx" ON "platform"."runtime_work_item"("state", "next_attempt_at");

-- CreateIndex
CREATE UNIQUE INDEX "runtime_work_item_outbox_message_id_handler_name_key" ON "platform"."runtime_work_item"("outbox_message_id", "handler_name");

-- CreateIndex
CREATE UNIQUE INDEX "runtime_attempt_work_item_id_attempt_number_key" ON "platform"."runtime_attempt"("work_item_id", "attempt_number");

-- CreateIndex
CREATE UNIQUE INDEX "runtime_inbox_receipt_consumer_owner_handler_name_outbox_me_key" ON "platform"."runtime_inbox_receipt"("consumer_owner", "handler_name", "outbox_message_id");

-- CreateIndex
CREATE UNIQUE INDEX "runtime_reservation_owner_module_id_resource_kind_resource__key" ON "platform"."runtime_reservation"("owner_module_id", "resource_kind", "resource_key", "semantic_key");

-- CreateIndex
CREATE UNIQUE INDEX "owner_mutation_evidence_owner_module_id_aggregate_kind_aggr_key" ON "platform"."owner_mutation_evidence"("owner_module_id", "aggregate_kind", "aggregate_id", "committed_revision");

-- CreateIndex
CREATE UNIQUE INDEX "customer_profile_lifecycle_event_customer_profile_id_source_key" ON "app"."customer_profile_lifecycle_event"("customer_profile_id", "source_revision");

-- CreateIndex
CREATE UNIQUE INDEX "track_base_selection_user_id_track_key" ON "app"."track_base_selection"("user_id", "track");

-- CreateIndex
CREATE UNIQUE INDEX "track_enrollment_receipt_source_owner_profile_id_semantic_k_key" ON "app"."track_enrollment_receipt"("source_owner", "profile_id", "semantic_key");

-- CreateIndex
CREATE UNIQUE INDEX "track_usage_reservation_reservation_id_key" ON "app"."track_usage_reservation"("reservation_id");

-- CreateIndex
CREATE UNIQUE INDEX "track_usage_reservation_user_id_entitlement_id_period_start_key" ON "app"."track_usage_reservation"("user_id", "entitlement_id", "period_start", "period_end", "semantic_key");

-- CreateIndex
CREATE UNIQUE INDEX "privacy_target_instruction_privacy_request_id_owner_module__key" ON "app"."privacy_target_instruction"("privacy_request_id", "owner_module_id", "target_kind", "source_id", "action", "generation");

-- CreateIndex
CREATE UNIQUE INDEX "privacy_owner_receipt_instruction_id_generation_key" ON "app"."privacy_owner_receipt"("instruction_id", "generation");

-- CreateIndex
CREATE UNIQUE INDEX "privacy_restore_marker_owner_module_id_target_kind_source_i_key" ON "app"."privacy_restore_marker"("owner_module_id", "target_kind", "source_id", "generation");

-- AddForeignKey
ALTER TABLE "app"."consent_logs" ADD CONSTRAINT "consent_logs_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "app"."users"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."consent_logs" ADD CONSTRAINT "consent_logs_content_revision_id_fkey" FOREIGN KEY ("content_revision_id") REFERENCES "app"."consent_content_revision"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."consent_logs" ADD CONSTRAINT "consent_logs_presentation_id_content_revision_id_user_id_fkey" FOREIGN KEY ("presentation_id", "content_revision_id", "user_id") REFERENCES "app"."consent_presentation"("id", "content_revision_id", "user_id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."privacy_requests" ADD CONSTRAINT "privacy_requests_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "app"."users"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."age_gate_attempts" ADD CONSTRAINT "age_gate_attempts_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "app"."users"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."access_audit_logs" ADD CONSTRAINT "access_audit_logs_actor_user_id_fkey" FOREIGN KEY ("actor_user_id") REFERENCES "app"."users"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."user_roles" ADD CONSTRAINT "user_roles_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "app"."users"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."professional_profiles" ADD CONSTRAINT "professional_profiles_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "app"."users"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."customer_profiles" ADD CONSTRAINT "customer_profiles_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "app"."users"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."candidate_profiles" ADD CONSTRAINT "candidate_profiles_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "app"."users"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."user_security_profiles" ADD CONSTRAINT "user_security_profiles_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "app"."users"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."auth_provider_accounts" ADD CONSTRAINT "auth_provider_accounts_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "app"."users"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."auth_provider_accounts" ADD CONSTRAINT "auth_provider_accounts_security_profile_id_fkey" FOREIGN KEY ("security_profile_id") REFERENCES "app"."user_security_profiles"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."track_plan_entitlements" ADD CONSTRAINT "track_plan_entitlements_plan_id_fkey" FOREIGN KEY ("plan_id") REFERENCES "app"."track_plans"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."track_plan_entitlements" ADD CONSTRAINT "track_plan_entitlements_entitlement_id_fkey" FOREIGN KEY ("entitlement_id") REFERENCES "app"."track_entitlement_definitions"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."track_subscriptions" ADD CONSTRAINT "track_subscriptions_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "app"."users"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."track_subscriptions" ADD CONSTRAINT "track_subscriptions_plan_id_fkey" FOREIGN KEY ("plan_id") REFERENCES "app"."track_plans"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."track_subscriptions" ADD CONSTRAINT "track_subscriptions_customer_profile_id_fkey" FOREIGN KEY ("customer_profile_id") REFERENCES "app"."customer_profiles"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."track_subscriptions" ADD CONSTRAINT "track_subscriptions_candidate_profile_id_fkey" FOREIGN KEY ("candidate_profile_id") REFERENCES "app"."candidate_profiles"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."track_subscriptions" ADD CONSTRAINT "track_subscriptions_professional_profile_id_fkey" FOREIGN KEY ("professional_profile_id") REFERENCES "app"."professional_profiles"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."track_entitlement_grants" ADD CONSTRAINT "track_entitlement_grants_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "app"."users"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."track_entitlement_grants" ADD CONSTRAINT "track_entitlement_grants_subscription_id_fkey" FOREIGN KEY ("subscription_id") REFERENCES "app"."track_subscriptions"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."track_entitlement_grants" ADD CONSTRAINT "track_entitlement_grants_entitlement_id_fkey" FOREIGN KEY ("entitlement_id") REFERENCES "app"."track_entitlement_definitions"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."track_entitlement_grants" ADD CONSTRAINT "track_entitlement_grants_customer_profile_id_fkey" FOREIGN KEY ("customer_profile_id") REFERENCES "app"."customer_profiles"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."track_entitlement_grants" ADD CONSTRAINT "track_entitlement_grants_candidate_profile_id_fkey" FOREIGN KEY ("candidate_profile_id") REFERENCES "app"."candidate_profiles"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."track_entitlement_grants" ADD CONSTRAINT "track_entitlement_grants_professional_profile_id_fkey" FOREIGN KEY ("professional_profile_id") REFERENCES "app"."professional_profiles"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."track_usage_events" ADD CONSTRAINT "track_usage_events_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "app"."users"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."track_usage_events" ADD CONSTRAINT "track_usage_events_subscription_id_fkey" FOREIGN KEY ("subscription_id") REFERENCES "app"."track_subscriptions"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."track_usage_events" ADD CONSTRAINT "track_usage_events_entitlement_grant_id_fkey" FOREIGN KEY ("entitlement_grant_id") REFERENCES "app"."track_entitlement_grants"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."track_usage_events" ADD CONSTRAINT "track_usage_events_entitlement_id_fkey" FOREIGN KEY ("entitlement_id") REFERENCES "app"."track_entitlement_definitions"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."track_usage_events" ADD CONSTRAINT "track_usage_events_customer_profile_id_fkey" FOREIGN KEY ("customer_profile_id") REFERENCES "app"."customer_profiles"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."track_usage_events" ADD CONSTRAINT "track_usage_events_candidate_profile_id_fkey" FOREIGN KEY ("candidate_profile_id") REFERENCES "app"."candidate_profiles"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."track_usage_events" ADD CONSTRAINT "track_usage_events_professional_profile_id_fkey" FOREIGN KEY ("professional_profile_id") REFERENCES "app"."professional_profiles"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."track_usage_events" ADD CONSTRAINT "track_usage_events_effect_receipt_id_fkey" FOREIGN KEY ("effect_receipt_id") REFERENCES "platform"."runtime_effect_receipt"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."track_usage_counters" ADD CONSTRAINT "track_usage_counters_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "app"."users"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."track_usage_counters" ADD CONSTRAINT "track_usage_counters_subscription_id_fkey" FOREIGN KEY ("subscription_id") REFERENCES "app"."track_subscriptions"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."track_usage_counters" ADD CONSTRAINT "track_usage_counters_entitlement_grant_id_fkey" FOREIGN KEY ("entitlement_grant_id") REFERENCES "app"."track_entitlement_grants"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."track_usage_counters" ADD CONSTRAINT "track_usage_counters_entitlement_id_fkey" FOREIGN KEY ("entitlement_id") REFERENCES "app"."track_entitlement_definitions"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."track_usage_counters" ADD CONSTRAINT "track_usage_counters_customer_profile_id_fkey" FOREIGN KEY ("customer_profile_id") REFERENCES "app"."customer_profiles"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."track_usage_counters" ADD CONSTRAINT "track_usage_counters_candidate_profile_id_fkey" FOREIGN KEY ("candidate_profile_id") REFERENCES "app"."candidate_profiles"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."track_usage_counters" ADD CONSTRAINT "track_usage_counters_professional_profile_id_fkey" FOREIGN KEY ("professional_profile_id") REFERENCES "app"."professional_profiles"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."track_subscription_events" ADD CONSTRAINT "track_subscription_events_subscription_id_fkey" FOREIGN KEY ("subscription_id") REFERENCES "app"."track_subscriptions"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."track_subscription_events" ADD CONSTRAINT "track_subscription_events_plan_id_fkey" FOREIGN KEY ("plan_id") REFERENCES "app"."track_plans"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."track_subscription_events" ADD CONSTRAINT "track_subscription_events_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "app"."users"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."consent_presentation" ADD CONSTRAINT "consent_presentation_content_revision_id_fkey" FOREIGN KEY ("content_revision_id") REFERENCES "app"."consent_content_revision"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."consent_presentation" ADD CONSTRAINT "consent_presentation_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "app"."users"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."consent_disposition" ADD CONSTRAINT "consent_disposition_proof_id_fkey" FOREIGN KEY ("proof_id") REFERENCES "app"."consent_logs"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."consent_disposition" ADD CONSTRAINT "consent_disposition_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "app"."users"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."consent_disposition" ADD CONSTRAINT "consent_disposition_presentation_id_fkey" FOREIGN KEY ("presentation_id") REFERENCES "app"."consent_presentation"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "platform"."runtime_outbox_message" ADD CONSTRAINT "runtime_outbox_message_command_receipt_id_fkey" FOREIGN KEY ("command_receipt_id") REFERENCES "platform"."runtime_command_receipt"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "platform"."runtime_effect_receipt" ADD CONSTRAINT "runtime_effect_receipt_command_receipt_id_fkey" FOREIGN KEY ("command_receipt_id") REFERENCES "platform"."runtime_command_receipt"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "platform"."runtime_work_item" ADD CONSTRAINT "runtime_work_item_outbox_message_id_fkey" FOREIGN KEY ("outbox_message_id") REFERENCES "platform"."runtime_outbox_message"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "platform"."runtime_work_item" ADD CONSTRAINT "runtime_work_item_effect_receipt_id_fkey" FOREIGN KEY ("effect_receipt_id") REFERENCES "platform"."runtime_effect_receipt"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "platform"."runtime_attempt" ADD CONSTRAINT "runtime_attempt_work_item_id_fkey" FOREIGN KEY ("work_item_id") REFERENCES "platform"."runtime_work_item"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "platform"."runtime_inbox_receipt" ADD CONSTRAINT "runtime_inbox_receipt_outbox_message_id_fkey" FOREIGN KEY ("outbox_message_id") REFERENCES "platform"."runtime_outbox_message"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "platform"."runtime_inbox_receipt" ADD CONSTRAINT "runtime_inbox_receipt_effect_receipt_id_fkey" FOREIGN KEY ("effect_receipt_id") REFERENCES "platform"."runtime_effect_receipt"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "platform"."runtime_reservation" ADD CONSTRAINT "runtime_reservation_command_receipt_id_fkey" FOREIGN KEY ("command_receipt_id") REFERENCES "platform"."runtime_command_receipt"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "platform"."runtime_reservation" ADD CONSTRAINT "runtime_reservation_effect_receipt_id_fkey" FOREIGN KEY ("effect_receipt_id") REFERENCES "platform"."runtime_effect_receipt"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "platform"."owner_mutation_evidence" ADD CONSTRAINT "owner_mutation_evidence_command_receipt_id_fkey" FOREIGN KEY ("command_receipt_id") REFERENCES "platform"."runtime_command_receipt"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."customer_profile_lifecycle_event" ADD CONSTRAINT "customer_profile_lifecycle_event_customer_profile_id_fkey" FOREIGN KEY ("customer_profile_id") REFERENCES "app"."customer_profiles"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."customer_profile_lifecycle_event" ADD CONSTRAINT "customer_profile_lifecycle_event_command_receipt_id_fkey" FOREIGN KEY ("command_receipt_id") REFERENCES "platform"."runtime_command_receipt"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."customer_profile_lifecycle_event" ADD CONSTRAINT "customer_profile_lifecycle_event_actor_user_id_fkey" FOREIGN KEY ("actor_user_id") REFERENCES "app"."users"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."track_base_selection" ADD CONSTRAINT "track_base_selection_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "app"."users"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."track_base_selection" ADD CONSTRAINT "track_base_selection_subscription_id_fkey" FOREIGN KEY ("subscription_id") REFERENCES "app"."track_subscriptions"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."track_base_selection" ADD CONSTRAINT "track_base_selection_customer_profile_id_fkey" FOREIGN KEY ("customer_profile_id") REFERENCES "app"."customer_profiles"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."track_base_selection" ADD CONSTRAINT "track_base_selection_candidate_profile_id_fkey" FOREIGN KEY ("candidate_profile_id") REFERENCES "app"."candidate_profiles"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."track_base_selection" ADD CONSTRAINT "track_base_selection_professional_profile_id_fkey" FOREIGN KEY ("professional_profile_id") REFERENCES "app"."professional_profiles"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."track_enrollment_receipt" ADD CONSTRAINT "track_enrollment_receipt_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "app"."users"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."track_enrollment_receipt" ADD CONSTRAINT "track_enrollment_receipt_selection_id_fkey" FOREIGN KEY ("selection_id") REFERENCES "app"."track_base_selection"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."track_enrollment_receipt" ADD CONSTRAINT "track_enrollment_receipt_effect_receipt_id_fkey" FOREIGN KEY ("effect_receipt_id") REFERENCES "platform"."runtime_effect_receipt"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."track_usage_reservation" ADD CONSTRAINT "track_usage_reservation_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "app"."users"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."track_usage_reservation" ADD CONSTRAINT "track_usage_reservation_entitlement_id_fkey" FOREIGN KEY ("entitlement_id") REFERENCES "app"."track_entitlement_definitions"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."track_usage_reservation" ADD CONSTRAINT "track_usage_reservation_reservation_id_fkey" FOREIGN KEY ("reservation_id") REFERENCES "platform"."runtime_reservation"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."privacy_target_instruction" ADD CONSTRAINT "privacy_target_instruction_privacy_request_id_fkey" FOREIGN KEY ("privacy_request_id") REFERENCES "app"."privacy_requests"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."privacy_owner_receipt" ADD CONSTRAINT "privacy_owner_receipt_instruction_id_fkey" FOREIGN KEY ("instruction_id") REFERENCES "app"."privacy_target_instruction"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;

-- AddForeignKey
ALTER TABLE "app"."privacy_restore_marker" ADD CONSTRAINT "privacy_restore_marker_source_receipt_id_fkey" FOREIGN KEY ("source_receipt_id") REFERENCES "app"."privacy_owner_receipt"("id") ON DELETE RESTRICT ON UPDATE RESTRICT;
