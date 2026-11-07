-- P0-C-03 REVIEW DRAFT ONLY. NOT EXECUTION-APPROVED. Posture D.
-- Future order: separate bootstrap, then one application migration transaction.
-- No migration directory/config/ledger is activated by these review artifacts.
BEGIN;
SET LOCAL ROLE wa_schema_owner;
SET LOCAL search_path = pg_catalog;

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

REVOKE ALL ON TYPE "app"."platform_role" FROM PUBLIC;
GRANT USAGE ON TYPE "app"."platform_role" TO wa_app_runtime,wa_worker,wa_context_issuer,wa_private_helper_owner;
REVOKE ALL ON TYPE "app"."account_track" FROM PUBLIC;
GRANT USAGE ON TYPE "app"."account_track" TO wa_app_runtime,wa_worker,wa_context_issuer,wa_private_helper_owner;
REVOKE ALL ON TYPE "app"."track_plan_status" FROM PUBLIC;
GRANT USAGE ON TYPE "app"."track_plan_status" TO wa_app_runtime,wa_worker,wa_context_issuer,wa_private_helper_owner;
REVOKE ALL ON TYPE "app"."track_billing_model" FROM PUBLIC;
GRANT USAGE ON TYPE "app"."track_billing_model" TO wa_app_runtime,wa_worker,wa_context_issuer,wa_private_helper_owner;
REVOKE ALL ON TYPE "app"."track_subscription_status" FROM PUBLIC;
GRANT USAGE ON TYPE "app"."track_subscription_status" TO wa_app_runtime,wa_worker,wa_context_issuer,wa_private_helper_owner;
REVOKE ALL ON TYPE "app"."track_billing_provider" FROM PUBLIC;
GRANT USAGE ON TYPE "app"."track_billing_provider" TO wa_app_runtime,wa_worker,wa_context_issuer,wa_private_helper_owner;
REVOKE ALL ON TYPE "app"."track_entitlement_value_type" FROM PUBLIC;
GRANT USAGE ON TYPE "app"."track_entitlement_value_type" TO wa_app_runtime,wa_worker,wa_context_issuer,wa_private_helper_owner;
REVOKE ALL ON TYPE "app"."track_entitlement_grant_status" FROM PUBLIC;
GRANT USAGE ON TYPE "app"."track_entitlement_grant_status" TO wa_app_runtime,wa_worker,wa_context_issuer,wa_private_helper_owner;
REVOKE ALL ON TYPE "app"."track_usage_event_type" FROM PUBLIC;
GRANT USAGE ON TYPE "app"."track_usage_event_type" TO wa_app_runtime,wa_worker,wa_context_issuer,wa_private_helper_owner;
REVOKE ALL ON TYPE "app"."track_usage_period" FROM PUBLIC;
GRANT USAGE ON TYPE "app"."track_usage_period" TO wa_app_runtime,wa_worker,wa_context_issuer,wa_private_helper_owner;
REVOKE ALL ON TYPE "app"."auth_provider_type" FROM PUBLIC;
GRANT USAGE ON TYPE "app"."auth_provider_type" TO wa_app_runtime,wa_worker,wa_context_issuer,wa_private_helper_owner;
REVOKE ALL ON TYPE "app"."auth_credential_status" FROM PUBLIC;
GRANT USAGE ON TYPE "app"."auth_credential_status" TO wa_app_runtime,wa_worker,wa_context_issuer,wa_private_helper_owner;
REVOKE ALL ON TYPE "app"."user_security_tier" FROM PUBLIC;
GRANT USAGE ON TYPE "app"."user_security_tier" TO wa_app_runtime,wa_worker,wa_context_issuer,wa_private_helper_owner;
REVOKE ALL ON TYPE "app"."profile_status" FROM PUBLIC;
GRANT USAGE ON TYPE "app"."profile_status" TO wa_app_runtime,wa_worker,wa_context_issuer,wa_private_helper_owner;
REVOKE ALL ON TYPE "app"."consent_type" FROM PUBLIC;
GRANT USAGE ON TYPE "app"."consent_type" TO wa_app_runtime,wa_worker,wa_context_issuer,wa_private_helper_owner;
REVOKE ALL ON TYPE "app"."privacy_request_type" FROM PUBLIC;
GRANT USAGE ON TYPE "app"."privacy_request_type" TO wa_app_runtime,wa_worker,wa_context_issuer,wa_private_helper_owner;
REVOKE ALL ON TYPE "app"."privacy_request_status" FROM PUBLIC;
GRANT USAGE ON TYPE "app"."privacy_request_status" TO wa_app_runtime,wa_worker,wa_context_issuer,wa_private_helper_owner;
REVOKE ALL ON TYPE "app"."age_gate_result" FROM PUBLIC;
GRANT USAGE ON TYPE "app"."age_gate_result" TO wa_app_runtime,wa_worker,wa_context_issuer,wa_private_helper_owner;
REVOKE ALL ON TYPE "app"."healthcare_access_decision" FROM PUBLIC;
GRANT USAGE ON TYPE "app"."healthcare_access_decision" TO wa_app_runtime,wa_worker,wa_context_issuer,wa_private_helper_owner;
REVOKE ALL ON TYPE "app"."data_sensitivity" FROM PUBLIC;
GRANT USAGE ON TYPE "app"."data_sensitivity" TO wa_app_runtime,wa_worker,wa_context_issuer,wa_private_helper_owner;
REVOKE ALL ON TYPE "app"."access_audit_action" FROM PUBLIC;
GRANT USAGE ON TYPE "app"."access_audit_action" TO wa_app_runtime,wa_worker,wa_context_issuer,wa_private_helper_owner;
REVOKE ALL ON TYPE "app"."review_policy_state" FROM PUBLIC;
GRANT USAGE ON TYPE "app"."review_policy_state" TO wa_app_runtime,wa_worker,wa_context_issuer,wa_private_helper_owner;
REVOKE ALL ON TYPE "app"."consent_disposition_kind" FROM PUBLIC;
GRANT USAGE ON TYPE "app"."consent_disposition_kind" TO wa_app_runtime,wa_worker,wa_context_issuer,wa_private_helper_owner;
REVOKE ALL ON TYPE "platform"."runtime_receipt_state" FROM PUBLIC;
GRANT USAGE ON TYPE "platform"."runtime_receipt_state" TO wa_app_runtime,wa_worker,wa_context_issuer,wa_private_helper_owner;
REVOKE ALL ON TYPE "platform"."runtime_message_kind" FROM PUBLIC;
GRANT USAGE ON TYPE "platform"."runtime_message_kind" TO wa_app_runtime,wa_worker,wa_context_issuer,wa_private_helper_owner;
REVOKE ALL ON TYPE "platform"."runtime_work_state" FROM PUBLIC;
GRANT USAGE ON TYPE "platform"."runtime_work_state" TO wa_app_runtime,wa_worker,wa_context_issuer,wa_private_helper_owner;
REVOKE ALL ON TYPE "platform"."runtime_reservation_state" FROM PUBLIC;
GRANT USAGE ON TYPE "platform"."runtime_reservation_state" TO wa_app_runtime,wa_worker,wa_context_issuer,wa_private_helper_owner;
REVOKE ALL ON TYPE "app"."privacy_action_kind" FROM PUBLIC;
GRANT USAGE ON TYPE "app"."privacy_action_kind" TO wa_app_runtime,wa_worker,wa_context_issuer,wa_private_helper_owner;
REVOKE ALL ON TYPE "app"."privacy_disposition_kind" FROM PUBLIC;
GRANT USAGE ON TYPE "app"."privacy_disposition_kind" TO wa_app_runtime,wa_worker,wa_context_issuer,wa_private_helper_owner;

-- P0-C-03A/DRAFT-01. Private Identity source, not a permission-policy catalog.
-- Identity's separately credentialed transition port verifies its canonical
-- authorization receipt before this transaction. Issuer/app/worker cannot write it.
CREATE TABLE platform_private.identity_service_receipt (
 id uuid PRIMARY KEY,
 service_principal text NOT NULL,
 previous_generation bigint,
 previous_receipt_id uuid REFERENCES platform_private.identity_service_receipt(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
 security_generation bigint NOT NULL CHECK (security_generation>=0),
 transition text NOT NULL CHECK (transition IN ('bootstrap','rotate','revoke','recover')),
 revoked_at timestamptz,
 identity_authorization_ref text NOT NULL CHECK (length(identity_authorization_ref)>0),
 mutation_transaction_id text NOT NULL DEFAULT pg_current_xact_id()::text,
 UNIQUE(service_principal,security_generation,id),
 CHECK ((previous_generation IS NULL AND previous_receipt_id IS NULL AND security_generation=0 AND transition='bootstrap')
     OR (previous_generation IS NOT NULL AND previous_receipt_id IS NOT NULL AND security_generation=previous_generation+1 AND transition<>'bootstrap')),
 CHECK ((transition='revoke')=(revoked_at IS NOT NULL))
);
CREATE TABLE platform_private.identity_service_authorization (
 service_principal text PRIMARY KEY CHECK (length(service_principal)>0),
 security_generation bigint NOT NULL CHECK (security_generation>=0),
 revoked_at timestamptz,
 identity_receipt_id uuid NOT NULL UNIQUE,
 mutation_transaction_id text NOT NULL DEFAULT pg_current_xact_id()::text,
 FOREIGN KEY(service_principal,security_generation,identity_receipt_id)
  REFERENCES platform_private.identity_service_receipt(service_principal,security_generation,id) ON DELETE RESTRICT ON UPDATE RESTRICT
);
ALTER TABLE platform_private.identity_service_receipt ENABLE ROW LEVEL SECURITY;
ALTER TABLE platform_private.identity_service_receipt FORCE ROW LEVEL SECURITY;
ALTER TABLE platform_private.identity_service_authorization ENABLE ROW LEVEL SECURITY;
ALTER TABLE platform_private.identity_service_authorization FORCE ROW LEVEL SECURITY;
GRANT SELECT,INSERT ON platform_private.identity_service_receipt TO wa_identity_service_authority;
GRANT SELECT,INSERT,UPDATE ON platform_private.identity_service_authorization TO wa_identity_service_authority;
GRANT SELECT(service_principal,security_generation,revoked_at) ON platform_private.identity_service_authorization TO wa_private_helper_owner;
CREATE POLICY identity_receipt_owner ON platform_private.identity_service_receipt TO wa_identity_service_authority USING (true) WITH CHECK (true);
CREATE POLICY identity_service_owner ON platform_private.identity_service_authorization TO wa_identity_service_authority USING (true) WITH CHECK (true);
CREATE POLICY identity_service_leaf ON platform_private.identity_service_authorization FOR SELECT TO wa_private_helper_owner USING (true);

CREATE FUNCTION platform_private.identity_service_guard() RETURNS trigger
LANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog AS $wa$
DECLARE r platform_private.identity_service_receipt; old_authority platform_private.identity_service_authorization;
BEGIN
 IF session_user::text<>'wa_identity_service_authority' OR TG_OP='DELETE' THEN
  RAISE EXCEPTION 'Identity service authority required' USING ERRCODE='42501'; END IF;
 PERFORM pg_advisory_xact_lock(hashtextextended('service:'||NEW.service_principal,0));
 IF TG_TABLE_NAME='identity_service_receipt' THEN
  IF TG_OP<>'INSERT' THEN RAISE EXCEPTION 'immutable Identity receipt'; END IF;
  SELECT * INTO old_authority FROM platform_private.identity_service_authorization WHERE service_principal=NEW.service_principal;
  IF FOUND THEN
   IF NEW.previous_generation IS DISTINCT FROM old_authority.security_generation
    OR NEW.previous_receipt_id IS DISTINCT FROM old_authority.identity_receipt_id
    OR NEW.security_generation<>old_authority.security_generation+1
    OR (old_authority.revoked_at IS NOT NULL AND NEW.transition<>'recover')
    OR (old_authority.revoked_at IS NULL AND NEW.transition NOT IN ('rotate','revoke'))
   THEN RAISE EXCEPTION 'stale or unsupported Identity transition'; END IF;
  ELSIF NEW.transition<>'bootstrap' OR NEW.previous_generation IS NOT NULL OR NEW.security_generation<>0 THEN
   RAISE EXCEPTION 'service bootstrap must have no predecessor';
  END IF;
  IF NEW.transition='revoke' THEN NEW.revoked_at:=clock_timestamp(); ELSE NEW.revoked_at:=NULL; END IF;
 ELSE
  IF TG_OP='UPDATE' AND (NEW.service_principal<>OLD.service_principal OR NEW.security_generation<>OLD.security_generation+1) THEN
   RAISE EXCEPTION 'service generation must advance once'; END IF;
  SELECT * INTO STRICT r FROM platform_private.identity_service_receipt WHERE id=NEW.identity_receipt_id;
  IF r.service_principal<>NEW.service_principal OR r.security_generation<>NEW.security_generation
   OR r.revoked_at IS DISTINCT FROM NEW.revoked_at OR r.mutation_transaction_id<>pg_current_xact_id()::text
   OR r.previous_generation IS DISTINCT FROM (CASE WHEN TG_OP='UPDATE' THEN OLD.security_generation ELSE NULL::bigint END)
   OR r.previous_receipt_id IS DISTINCT FROM (CASE WHEN TG_OP='UPDATE' THEN OLD.identity_receipt_id ELSE NULL::uuid END)
  THEN RAISE EXCEPTION 'exact current Identity receipt required'; END IF;
 END IF;
 NEW.mutation_transaction_id:=pg_current_xact_id()::text;
 RETURN NEW;
END $wa$;
CREATE TRIGGER identity_service_write BEFORE INSERT OR UPDATE OR DELETE ON platform_private.identity_service_authorization FOR EACH ROW EXECUTE FUNCTION platform_private.identity_service_guard();
CREATE TRIGGER identity_receipt_write BEFORE INSERT OR UPDATE OR DELETE ON platform_private.identity_service_receipt FOR EACH ROW EXECUTE FUNCTION platform_private.identity_service_guard();
CREATE FUNCTION platform_private.identity_receipt_commit() RETURNS trigger
LANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog AS $wa$
BEGIN
 IF NOT EXISTS(SELECT 1 FROM platform_private.identity_service_authorization a WHERE a.service_principal=NEW.service_principal
  AND a.security_generation=NEW.security_generation AND a.identity_receipt_id=NEW.id
  AND a.mutation_transaction_id=NEW.mutation_transaction_id) THEN RAISE EXCEPTION 'orphan Identity authorization receipt'; END IF;
 RETURN NULL;
END $wa$;
CREATE CONSTRAINT TRIGGER identity_receipt_atomic AFTER INSERT ON platform_private.identity_service_receipt DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.identity_receipt_commit();

CREATE FUNCTION platform_private.json_datetime(v text) RETURNS boolean
LANGUAGE plpgsql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
BEGIN
 IF v IS NULL OR v !~ '^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$' THEN RETURN false; END IF;
 PERFORM v::timestamptz; RETURN true;
 EXCEPTION WHEN invalid_datetime_format OR datetime_field_overflow THEN RETURN false;
END;
$wa$;

CREATE FUNCTION platform_private.json_evidence_consentlog(v jsonb) RETURNS boolean
LANGUAGE sql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
SELECT COALESCE((jsonb_typeof(v) = 'object' AND v ?& ARRAY['schema','owner','model','primaryKey','committed','decisionRef']::text[] AND (v - ARRAY['schema','owner','model','primaryKey','prior','committed','decisionRef']::text[]) = '{}'::jsonb AND (NOT (v ? 'schema') OR ((v->'schema') = '"database-owner-evidence.v1"'::jsonb)) AND (NOT (v ? 'owner') OR ((v->'owner') = '"consent_disclosure"'::jsonb)) AND (NOT (v ? 'model') OR ((v->'model') = '"ConsentLog"'::jsonb)) AND (NOT (v ? 'primaryKey') OR (jsonb_typeof((v->'primaryKey')) = 'object' AND (v->'primaryKey') ?& ARRAY['id']::text[] AND ((v->'primaryKey') - ARRAY['id']::text[]) = '{}'::jsonb AND (NOT ((v->'primaryKey') ? 'id') OR (jsonb_typeof(((v->'primaryKey')->'id')) = 'string' AND (((v->'primaryKey')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')))) AND (NOT (v ? 'prior') OR ((v->'prior') = 'null'::jsonb OR (jsonb_typeof((v->'prior')) = 'object' AND (v->'prior') ?& ARRAY['id','userId','type','acceptedAt','ipHash','presentationHash']::text[] AND ((v->'prior') - ARRAY['id','userId','type','acceptedAt','ipHash','presentationHash']::text[]) = '{}'::jsonb AND (NOT ((v->'prior') ? 'id') OR (jsonb_typeof(((v->'prior')->'id')) = 'string' AND (((v->'prior')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'userId') OR (jsonb_typeof(((v->'prior')->'userId')) = 'string' AND (((v->'prior')->'userId') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'type') OR (((v->'prior')->'type') = '"terms"'::jsonb OR ((v->'prior')->'type') = '"privacy_policy"'::jsonb OR ((v->'prior')->'type') = '"cookies"'::jsonb OR ((v->'prior')->'type') = '"marketing"'::jsonb OR ((v->'prior')->'type') = '"age_gate"'::jsonb OR ((v->'prior')->'type') = '"calendar_sync"'::jsonb OR ((v->'prior')->'type') = '"sweepstakes_rules"'::jsonb OR ((v->'prior')->'type') = '"gamification_terms"'::jsonb OR ((v->'prior')->'type') = '"reward_redemption_terms"'::jsonb OR ((v->'prior')->'type') = '"healthcare_baa"'::jsonb OR ((v->'prior')->'type') = '"fcra_background_check"'::jsonb OR ((v->'prior')->'type') = '"license_verification"'::jsonb OR ((v->'prior')->'type') = '"dmv_check"'::jsonb OR ((v->'prior')->'type') = '"passkey_login"'::jsonb OR ((v->'prior')->'type') = '"sms_mfa"'::jsonb OR ((v->'prior')->'type') = '"sensitive_financial_access"'::jsonb OR ((v->'prior')->'type') = '"account_recovery_identity_verification"'::jsonb OR ((v->'prior')->'type') = '"phone_number_update"'::jsonb OR ((v->'prior')->'type') = '"digital_goods_terms"'::jsonb OR ((v->'prior')->'type') = '"digital_goods_refund_policy"'::jsonb OR ((v->'prior')->'type') = '"digital_goods_license"'::jsonb OR ((v->'prior')->'type') = '"child_directed_content_declaration"'::jsonb OR ((v->'prior')->'type') = '"course_accessibility_disclosure"'::jsonb OR ((v->'prior')->'type') = '"electronic_records_consent"'::jsonb OR ((v->'prior')->'type') = '"electronic_signature_consent"'::jsonb OR ((v->'prior')->'type') = '"agreement_execution_consent"'::jsonb OR ((v->'prior')->'type') = '"manual_signature_opt_out"'::jsonb OR ((v->'prior')->'type') = '"calendar_free_busy_access"'::jsonb OR ((v->'prior')->'type') = '"calendar_writeback_access"'::jsonb OR ((v->'prior')->'type') = '"calendar_disconnect_notice"'::jsonb OR ((v->'prior')->'type') = '"web_push_notifications"'::jsonb OR ((v->'prior')->'type') = '"pwa_install_guidance"'::jsonb OR ((v->'prior')->'type') = '"subscription_terms"'::jsonb OR ((v->'prior')->'type') = '"recurring_billing_authorization"'::jsonb OR ((v->'prior')->'type') = '"plan_change_terms"'::jsonb OR ((v->'prior')->'type') = '"commission_terms"'::jsonb OR ((v->'prior')->'type') = '"buyer_fee_waiver_terms"'::jsonb)) AND (NOT ((v->'prior') ? 'acceptedAt') OR (jsonb_typeof(((v->'prior')->'acceptedAt')) = 'string' AND platform_private.json_datetime((((v->'prior')->'acceptedAt') #>> '{}')))) AND (NOT ((v->'prior') ? 'ipHash') OR ((jsonb_typeof(((v->'prior')->'ipHash')) = 'string') OR (jsonb_typeof(((v->'prior')->'ipHash')) = 'null'))) AND (NOT ((v->'prior') ? 'presentationHash') OR (jsonb_typeof(((v->'prior')->'presentationHash')) = 'string'))))) AND (NOT (v ? 'committed') OR (jsonb_typeof((v->'committed')) = 'object' AND (v->'committed') ?& ARRAY['id','userId','type','acceptedAt','ipHash','presentationHash']::text[] AND ((v->'committed') - ARRAY['id','userId','type','acceptedAt','ipHash','presentationHash']::text[]) = '{}'::jsonb AND (NOT ((v->'committed') ? 'id') OR (jsonb_typeof(((v->'committed')->'id')) = 'string' AND (((v->'committed')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'userId') OR (jsonb_typeof(((v->'committed')->'userId')) = 'string' AND (((v->'committed')->'userId') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'type') OR (((v->'committed')->'type') = '"terms"'::jsonb OR ((v->'committed')->'type') = '"privacy_policy"'::jsonb OR ((v->'committed')->'type') = '"cookies"'::jsonb OR ((v->'committed')->'type') = '"marketing"'::jsonb OR ((v->'committed')->'type') = '"age_gate"'::jsonb OR ((v->'committed')->'type') = '"calendar_sync"'::jsonb OR ((v->'committed')->'type') = '"sweepstakes_rules"'::jsonb OR ((v->'committed')->'type') = '"gamification_terms"'::jsonb OR ((v->'committed')->'type') = '"reward_redemption_terms"'::jsonb OR ((v->'committed')->'type') = '"healthcare_baa"'::jsonb OR ((v->'committed')->'type') = '"fcra_background_check"'::jsonb OR ((v->'committed')->'type') = '"license_verification"'::jsonb OR ((v->'committed')->'type') = '"dmv_check"'::jsonb OR ((v->'committed')->'type') = '"passkey_login"'::jsonb OR ((v->'committed')->'type') = '"sms_mfa"'::jsonb OR ((v->'committed')->'type') = '"sensitive_financial_access"'::jsonb OR ((v->'committed')->'type') = '"account_recovery_identity_verification"'::jsonb OR ((v->'committed')->'type') = '"phone_number_update"'::jsonb OR ((v->'committed')->'type') = '"digital_goods_terms"'::jsonb OR ((v->'committed')->'type') = '"digital_goods_refund_policy"'::jsonb OR ((v->'committed')->'type') = '"digital_goods_license"'::jsonb OR ((v->'committed')->'type') = '"child_directed_content_declaration"'::jsonb OR ((v->'committed')->'type') = '"course_accessibility_disclosure"'::jsonb OR ((v->'committed')->'type') = '"electronic_records_consent"'::jsonb OR ((v->'committed')->'type') = '"electronic_signature_consent"'::jsonb OR ((v->'committed')->'type') = '"agreement_execution_consent"'::jsonb OR ((v->'committed')->'type') = '"manual_signature_opt_out"'::jsonb OR ((v->'committed')->'type') = '"calendar_free_busy_access"'::jsonb OR ((v->'committed')->'type') = '"calendar_writeback_access"'::jsonb OR ((v->'committed')->'type') = '"calendar_disconnect_notice"'::jsonb OR ((v->'committed')->'type') = '"web_push_notifications"'::jsonb OR ((v->'committed')->'type') = '"pwa_install_guidance"'::jsonb OR ((v->'committed')->'type') = '"subscription_terms"'::jsonb OR ((v->'committed')->'type') = '"recurring_billing_authorization"'::jsonb OR ((v->'committed')->'type') = '"plan_change_terms"'::jsonb OR ((v->'committed')->'type') = '"commission_terms"'::jsonb OR ((v->'committed')->'type') = '"buyer_fee_waiver_terms"'::jsonb)) AND (NOT ((v->'committed') ? 'acceptedAt') OR (jsonb_typeof(((v->'committed')->'acceptedAt')) = 'string' AND platform_private.json_datetime((((v->'committed')->'acceptedAt') #>> '{}')))) AND (NOT ((v->'committed') ? 'ipHash') OR ((jsonb_typeof(((v->'committed')->'ipHash')) = 'string') OR (jsonb_typeof(((v->'committed')->'ipHash')) = 'null'))) AND (NOT ((v->'committed') ? 'presentationHash') OR (jsonb_typeof(((v->'committed')->'presentationHash')) = 'string')))) AND (NOT (v ? 'decisionRef') OR (jsonb_typeof((v->'decisionRef')) = 'string' AND length(((v->'decisionRef') #>> '{}')) >= 1))),false);
$wa$;

CREATE FUNCTION platform_private.json_evidence_privacyrequest(v jsonb) RETURNS boolean
LANGUAGE sql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
SELECT COALESCE((jsonb_typeof(v) = 'object' AND v ?& ARRAY['schema','owner','model','primaryKey','committed','decisionRef']::text[] AND (v - ARRAY['schema','owner','model','primaryKey','prior','committed','decisionRef']::text[]) = '{}'::jsonb AND (NOT (v ? 'schema') OR ((v->'schema') = '"database-owner-evidence.v1"'::jsonb)) AND (NOT (v ? 'owner') OR ((v->'owner') = '"privacy_data_erasure"'::jsonb)) AND (NOT (v ? 'model') OR ((v->'model') = '"PrivacyRequest"'::jsonb)) AND (NOT (v ? 'primaryKey') OR (jsonb_typeof((v->'primaryKey')) = 'object' AND (v->'primaryKey') ?& ARRAY['id']::text[] AND ((v->'primaryKey') - ARRAY['id']::text[]) = '{}'::jsonb AND (NOT ((v->'primaryKey') ? 'id') OR (jsonb_typeof(((v->'primaryKey')->'id')) = 'string' AND (((v->'primaryKey')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')))) AND (NOT (v ? 'prior') OR ((v->'prior') = 'null'::jsonb OR (jsonb_typeof((v->'prior')) = 'object' AND (v->'prior') ?& ARRAY['id','userId','type','status','revision','privacyGeneration','instructionGeneration']::text[] AND ((v->'prior') - ARRAY['id','userId','type','status','revision','privacyGeneration','instructionGeneration']::text[]) = '{}'::jsonb AND (NOT ((v->'prior') ? 'id') OR (jsonb_typeof(((v->'prior')->'id')) = 'string' AND (((v->'prior')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'userId') OR (jsonb_typeof(((v->'prior')->'userId')) = 'string' AND (((v->'prior')->'userId') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'type') OR (((v->'prior')->'type') = '"access"'::jsonb OR ((v->'prior')->'type') = '"export"'::jsonb OR ((v->'prior')->'type') = '"erasure"'::jsonb OR ((v->'prior')->'type') = '"correction"'::jsonb OR ((v->'prior')->'type') = '"restriction"'::jsonb)) AND (NOT ((v->'prior') ? 'status') OR (((v->'prior')->'status') = '"submitted"'::jsonb OR ((v->'prior')->'status') = '"verifying_identity"'::jsonb OR ((v->'prior')->'status') = '"verified"'::jsonb OR ((v->'prior')->'status') = '"processing"'::jsonb OR ((v->'prior')->'status') = '"completed"'::jsonb OR ((v->'prior')->'status') = '"partially_completed"'::jsonb OR ((v->'prior')->'status') = '"rejected"'::jsonb OR ((v->'prior')->'status') = '"cancelled"'::jsonb)) AND (NOT ((v->'prior') ? 'revision') OR (jsonb_typeof(((v->'prior')->'revision')) = 'string' AND (((v->'prior')->'revision') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'prior') ? 'privacyGeneration') OR (jsonb_typeof(((v->'prior')->'privacyGeneration')) = 'string' AND (((v->'prior')->'privacyGeneration') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'prior') ? 'instructionGeneration') OR (jsonb_typeof(((v->'prior')->'instructionGeneration')) = 'string' AND (((v->'prior')->'instructionGeneration') #>> '{}') ~ '^-?[0-9]+$'))))) AND (NOT (v ? 'committed') OR (jsonb_typeof((v->'committed')) = 'object' AND (v->'committed') ?& ARRAY['id','userId','type','status','revision','privacyGeneration','instructionGeneration']::text[] AND ((v->'committed') - ARRAY['id','userId','type','status','revision','privacyGeneration','instructionGeneration']::text[]) = '{}'::jsonb AND (NOT ((v->'committed') ? 'id') OR (jsonb_typeof(((v->'committed')->'id')) = 'string' AND (((v->'committed')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'userId') OR (jsonb_typeof(((v->'committed')->'userId')) = 'string' AND (((v->'committed')->'userId') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'type') OR (((v->'committed')->'type') = '"access"'::jsonb OR ((v->'committed')->'type') = '"export"'::jsonb OR ((v->'committed')->'type') = '"erasure"'::jsonb OR ((v->'committed')->'type') = '"correction"'::jsonb OR ((v->'committed')->'type') = '"restriction"'::jsonb)) AND (NOT ((v->'committed') ? 'status') OR (((v->'committed')->'status') = '"submitted"'::jsonb OR ((v->'committed')->'status') = '"verifying_identity"'::jsonb OR ((v->'committed')->'status') = '"verified"'::jsonb OR ((v->'committed')->'status') = '"processing"'::jsonb OR ((v->'committed')->'status') = '"completed"'::jsonb OR ((v->'committed')->'status') = '"partially_completed"'::jsonb OR ((v->'committed')->'status') = '"rejected"'::jsonb OR ((v->'committed')->'status') = '"cancelled"'::jsonb)) AND (NOT ((v->'committed') ? 'revision') OR (jsonb_typeof(((v->'committed')->'revision')) = 'string' AND (((v->'committed')->'revision') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'committed') ? 'privacyGeneration') OR (jsonb_typeof(((v->'committed')->'privacyGeneration')) = 'string' AND (((v->'committed')->'privacyGeneration') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'committed') ? 'instructionGeneration') OR (jsonb_typeof(((v->'committed')->'instructionGeneration')) = 'string' AND (((v->'committed')->'instructionGeneration') #>> '{}') ~ '^-?[0-9]+$')))) AND (NOT (v ? 'decisionRef') OR (jsonb_typeof((v->'decisionRef')) = 'string' AND length(((v->'decisionRef') #>> '{}')) >= 1))),false);
$wa$;

CREATE FUNCTION platform_private.json_evidence_agegateattempt(v jsonb) RETURNS boolean
LANGUAGE sql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
SELECT COALESCE((jsonb_typeof(v) = 'object' AND v ?& ARRAY['schema','owner','model','primaryKey','committed','decisionRef']::text[] AND (v - ARRAY['schema','owner','model','primaryKey','prior','committed','decisionRef']::text[]) = '{}'::jsonb AND (NOT (v ? 'schema') OR ((v->'schema') = '"database-owner-evidence.v1"'::jsonb)) AND (NOT (v ? 'owner') OR ((v->'owner') = '"identity_access"'::jsonb)) AND (NOT (v ? 'model') OR ((v->'model') = '"AgeGateAttempt"'::jsonb)) AND (NOT (v ? 'primaryKey') OR (jsonb_typeof((v->'primaryKey')) = 'object' AND (v->'primaryKey') ?& ARRAY['id']::text[] AND ((v->'primaryKey') - ARRAY['id']::text[]) = '{}'::jsonb AND (NOT ((v->'primaryKey') ? 'id') OR (jsonb_typeof(((v->'primaryKey')->'id')) = 'string' AND (((v->'primaryKey')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')))) AND (NOT (v ? 'prior') OR ((v->'prior') = 'null'::jsonb OR (jsonb_typeof((v->'prior')) = 'object' AND (v->'prior') ?& ARRAY['id','userId','ipHash','deviceHash','result']::text[] AND ((v->'prior') - ARRAY['id','userId','ipHash','deviceHash','result']::text[]) = '{}'::jsonb AND (NOT ((v->'prior') ? 'id') OR (jsonb_typeof(((v->'prior')->'id')) = 'string' AND (((v->'prior')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'userId') OR ((jsonb_typeof(((v->'prior')->'userId')) = 'string' AND (((v->'prior')->'userId') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$') OR (jsonb_typeof(((v->'prior')->'userId')) = 'null'))) AND (NOT ((v->'prior') ? 'ipHash') OR ((jsonb_typeof(((v->'prior')->'ipHash')) = 'string') OR (jsonb_typeof(((v->'prior')->'ipHash')) = 'null'))) AND (NOT ((v->'prior') ? 'deviceHash') OR ((jsonb_typeof(((v->'prior')->'deviceHash')) = 'string') OR (jsonb_typeof(((v->'prior')->'deviceHash')) = 'null'))) AND (NOT ((v->'prior') ? 'result') OR (((v->'prior')->'result') = '"allowed"'::jsonb OR ((v->'prior')->'result') = '"blocked_underage"'::jsonb OR ((v->'prior')->'result') = '"blocked_region"'::jsonb OR ((v->'prior')->'result') = '"manual_review"'::jsonb))))) AND (NOT (v ? 'committed') OR (jsonb_typeof((v->'committed')) = 'object' AND (v->'committed') ?& ARRAY['id','userId','ipHash','deviceHash','result']::text[] AND ((v->'committed') - ARRAY['id','userId','ipHash','deviceHash','result']::text[]) = '{}'::jsonb AND (NOT ((v->'committed') ? 'id') OR (jsonb_typeof(((v->'committed')->'id')) = 'string' AND (((v->'committed')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'userId') OR ((jsonb_typeof(((v->'committed')->'userId')) = 'string' AND (((v->'committed')->'userId') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$') OR (jsonb_typeof(((v->'committed')->'userId')) = 'null'))) AND (NOT ((v->'committed') ? 'ipHash') OR ((jsonb_typeof(((v->'committed')->'ipHash')) = 'string') OR (jsonb_typeof(((v->'committed')->'ipHash')) = 'null'))) AND (NOT ((v->'committed') ? 'deviceHash') OR ((jsonb_typeof(((v->'committed')->'deviceHash')) = 'string') OR (jsonb_typeof(((v->'committed')->'deviceHash')) = 'null'))) AND (NOT ((v->'committed') ? 'result') OR (((v->'committed')->'result') = '"allowed"'::jsonb OR ((v->'committed')->'result') = '"blocked_underage"'::jsonb OR ((v->'committed')->'result') = '"blocked_region"'::jsonb OR ((v->'committed')->'result') = '"manual_review"'::jsonb)))) AND (NOT (v ? 'decisionRef') OR (jsonb_typeof((v->'decisionRef')) = 'string' AND length(((v->'decisionRef') #>> '{}')) >= 1))),false);
$wa$;

CREATE FUNCTION platform_private.json_evidence_agegateblock(v jsonb) RETURNS boolean
LANGUAGE sql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
SELECT COALESCE((jsonb_typeof(v) = 'object' AND v ?& ARRAY['schema','owner','model','primaryKey','committed','decisionRef']::text[] AND (v - ARRAY['schema','owner','model','primaryKey','prior','committed','decisionRef']::text[]) = '{}'::jsonb AND (NOT (v ? 'schema') OR ((v->'schema') = '"database-owner-evidence.v1"'::jsonb)) AND (NOT (v ? 'owner') OR ((v->'owner') = '"identity_access"'::jsonb)) AND (NOT (v ? 'model') OR ((v->'model') = '"AgeGateBlock"'::jsonb)) AND (NOT (v ? 'primaryKey') OR (jsonb_typeof((v->'primaryKey')) = 'object' AND (v->'primaryKey') ?& ARRAY['id']::text[] AND ((v->'primaryKey') - ARRAY['id']::text[]) = '{}'::jsonb AND (NOT ((v->'primaryKey') ? 'id') OR (jsonb_typeof(((v->'primaryKey')->'id')) = 'string' AND (((v->'primaryKey')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')))) AND (NOT (v ? 'prior') OR ((v->'prior') = 'null'::jsonb OR (jsonb_typeof((v->'prior')) = 'object' AND (v->'prior') ?& ARRAY['id','ipHash','deviceHash']::text[] AND ((v->'prior') - ARRAY['id','ipHash','deviceHash']::text[]) = '{}'::jsonb AND (NOT ((v->'prior') ? 'id') OR (jsonb_typeof(((v->'prior')->'id')) = 'string' AND (((v->'prior')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'ipHash') OR ((jsonb_typeof(((v->'prior')->'ipHash')) = 'string') OR (jsonb_typeof(((v->'prior')->'ipHash')) = 'null'))) AND (NOT ((v->'prior') ? 'deviceHash') OR ((jsonb_typeof(((v->'prior')->'deviceHash')) = 'string') OR (jsonb_typeof(((v->'prior')->'deviceHash')) = 'null')))))) AND (NOT (v ? 'committed') OR (jsonb_typeof((v->'committed')) = 'object' AND (v->'committed') ?& ARRAY['id','ipHash','deviceHash']::text[] AND ((v->'committed') - ARRAY['id','ipHash','deviceHash']::text[]) = '{}'::jsonb AND (NOT ((v->'committed') ? 'id') OR (jsonb_typeof(((v->'committed')->'id')) = 'string' AND (((v->'committed')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'ipHash') OR ((jsonb_typeof(((v->'committed')->'ipHash')) = 'string') OR (jsonb_typeof(((v->'committed')->'ipHash')) = 'null'))) AND (NOT ((v->'committed') ? 'deviceHash') OR ((jsonb_typeof(((v->'committed')->'deviceHash')) = 'string') OR (jsonb_typeof(((v->'committed')->'deviceHash')) = 'null'))))) AND (NOT (v ? 'decisionRef') OR (jsonb_typeof((v->'decisionRef')) = 'string' AND length(((v->'decisionRef') #>> '{}')) >= 1))),false);
$wa$;

CREATE FUNCTION platform_private.json_evidence_accessauditlog(v jsonb) RETURNS boolean
LANGUAGE sql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
SELECT COALESCE((jsonb_typeof(v) = 'object' AND v ?& ARRAY['schema','owner','model','primaryKey','committed','decisionRef']::text[] AND (v - ARRAY['schema','owner','model','primaryKey','prior','committed','decisionRef']::text[]) = '{}'::jsonb AND (NOT (v ? 'schema') OR ((v->'schema') = '"database-owner-evidence.v1"'::jsonb)) AND (NOT (v ? 'owner') OR ((v->'owner') = '"audit_event_ledger"'::jsonb)) AND (NOT (v ? 'model') OR ((v->'model') = '"AccessAuditLog"'::jsonb)) AND (NOT (v ? 'primaryKey') OR (jsonb_typeof((v->'primaryKey')) = 'object' AND (v->'primaryKey') ?& ARRAY['id']::text[] AND ((v->'primaryKey') - ARRAY['id']::text[]) = '{}'::jsonb AND (NOT ((v->'primaryKey') ? 'id') OR (jsonb_typeof(((v->'primaryKey')->'id')) = 'string' AND (((v->'primaryKey')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')))) AND (NOT (v ? 'prior') OR ((v->'prior') = 'null'::jsonb OR (jsonb_typeof((v->'prior')) = 'object' AND (v->'prior') ?& ARRAY['id','action','sensitivity','accessDecision','ipHash','previousHash','entryHash']::text[] AND ((v->'prior') - ARRAY['id','action','sensitivity','accessDecision','ipHash','previousHash','entryHash']::text[]) = '{}'::jsonb AND (NOT ((v->'prior') ? 'id') OR (jsonb_typeof(((v->'prior')->'id')) = 'string' AND (((v->'prior')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'action') OR (((v->'prior')->'action') = '"file_read"'::jsonb OR ((v->'prior')->'action') = '"file_download"'::jsonb OR ((v->'prior')->'action') = '"message_read"'::jsonb OR ((v->'prior')->'action') = '"thread_opened"'::jsonb OR ((v->'prior')->'action') = '"video_joined"'::jsonb OR ((v->'prior')->'action') = '"location_revealed"'::jsonb OR ((v->'prior')->'action') = '"privacy_export_generated"'::jsonb OR ((v->'prior')->'action') = '"privacy_erasure_started"'::jsonb OR ((v->'prior')->'action') = '"privacy_erasure_completed"'::jsonb OR ((v->'prior')->'action') = '"healthcare_policy_checked"'::jsonb OR ((v->'prior')->'action') = '"healthcare_payload_redacted"'::jsonb OR ((v->'prior')->'action') = '"healthcare_payload_blocked"'::jsonb OR ((v->'prior')->'action') = '"admin_redacted_view"'::jsonb OR ((v->'prior')->'action') = '"admin_blocked_view"'::jsonb OR ((v->'prior')->'action') = '"processor_balance_read"'::jsonb OR ((v->'prior')->'action') = '"payout_account_read"'::jsonb OR ((v->'prior')->'action') = '"tax_profile_read"'::jsonb OR ((v->'prior')->'action') = '"tax_dashboard_opened"'::jsonb OR ((v->'prior')->'action') = '"payout_request_started"'::jsonb OR ((v->'prior')->'action') = '"sensitive_financial_step_up_verified"'::jsonb OR ((v->'prior')->'action') = '"phone_number_changed"'::jsonb OR ((v->'prior')->'action') = '"account_recovery_completed"'::jsonb OR ((v->'prior')->'action') = '"course_video_started"'::jsonb OR ((v->'prior')->'action') = '"course_video_completed"'::jsonb OR ((v->'prior')->'action') = '"live_video_token_issued"'::jsonb OR ((v->'prior')->'action') = '"digital_download_url_issued"'::jsonb OR ((v->'prior')->'action') = '"digital_download_denied"'::jsonb OR ((v->'prior')->'action') = '"digital_download_started"'::jsonb OR ((v->'prior')->'action') = '"digital_download_completed"'::jsonb OR ((v->'prior')->'action') = '"course_video_playback_granted"'::jsonb OR ((v->'prior')->'action') = '"course_video_playback_denied"'::jsonb OR ((v->'prior')->'action') = '"agreement_viewed"'::jsonb OR ((v->'prior')->'action') = '"agreement_downloaded"'::jsonb OR ((v->'prior')->'action') = '"agreement_signed"'::jsonb OR ((v->'prior')->'action') = '"agreement_hash_verified"'::jsonb OR ((v->'prior')->'action') = '"agreement_tamper_detected"'::jsonb OR ((v->'prior')->'action') = '"agreement_manual_opt_out"'::jsonb OR ((v->'prior')->'action') = '"media_signed_url_issued"'::jsonb OR ((v->'prior')->'action') = '"media_signed_url_denied"'::jsonb OR ((v->'prior')->'action') = '"media_upload_rejected"'::jsonb OR ((v->'prior')->'action') = '"media_malware_detected"'::jsonb OR ((v->'prior')->'action') = '"media_metadata_scrubbed"'::jsonb OR ((v->'prior')->'action') = '"media_quarantined"'::jsonb OR ((v->'prior')->'action') = '"media_promoted_to_ready"'::jsonb OR ((v->'prior')->'action') = '"calendar_connection_started"'::jsonb OR ((v->'prior')->'action') = '"calendar_connection_authorized"'::jsonb OR ((v->'prior')->'action') = '"calendar_connection_revoked"'::jsonb OR ((v->'prior')->'action') = '"calendar_free_busy_synced"'::jsonb OR ((v->'prior')->'action') = '"booking_hold_created"'::jsonb OR ((v->'prior')->'action') = '"booking_confirmed"'::jsonb OR ((v->'prior')->'action') = '"booking_slot_lock_failed"'::jsonb OR ((v->'prior')->'action') = '"booking_orchestration_started"'::jsonb OR ((v->'prior')->'action') = '"booking_orchestration_failed"'::jsonb)) AND (NOT ((v->'prior') ? 'sensitivity') OR (((v->'prior')->'sensitivity') = '"normal"'::jsonb OR ((v->'prior')->'sensitivity') = '"sensitive"'::jsonb OR ((v->'prior')->'sensitivity') = '"healthcare"'::jsonb OR ((v->'prior')->'sensitivity') = '"financial"'::jsonb OR ((v->'prior')->'sensitivity') = '"identity_document"'::jsonb OR ((v->'prior')->'sensitivity') = '"resume"'::jsonb OR ((v->'prior')->'sensitivity') = '"legal_contract"'::jsonb OR ((v->'prior')->'sensitivity') = '"private_message"'::jsonb)) AND (NOT ((v->'prior') ? 'accessDecision') OR ((((v->'prior')->'accessDecision') = '"allowed"'::jsonb OR ((v->'prior')->'accessDecision') = '"redacted"'::jsonb OR ((v->'prior')->'accessDecision') = '"blocked"'::jsonb OR ((v->'prior')->'accessDecision') = '"denied"'::jsonb) OR (jsonb_typeof(((v->'prior')->'accessDecision')) = 'null'))) AND (NOT ((v->'prior') ? 'ipHash') OR ((jsonb_typeof(((v->'prior')->'ipHash')) = 'string') OR (jsonb_typeof(((v->'prior')->'ipHash')) = 'null'))) AND (NOT ((v->'prior') ? 'previousHash') OR ((jsonb_typeof(((v->'prior')->'previousHash')) = 'string') OR (jsonb_typeof(((v->'prior')->'previousHash')) = 'null'))) AND (NOT ((v->'prior') ? 'entryHash') OR ((jsonb_typeof(((v->'prior')->'entryHash')) = 'string') OR (jsonb_typeof(((v->'prior')->'entryHash')) = 'null')))))) AND (NOT (v ? 'committed') OR (jsonb_typeof((v->'committed')) = 'object' AND (v->'committed') ?& ARRAY['id','action','sensitivity','accessDecision','ipHash','previousHash','entryHash']::text[] AND ((v->'committed') - ARRAY['id','action','sensitivity','accessDecision','ipHash','previousHash','entryHash']::text[]) = '{}'::jsonb AND (NOT ((v->'committed') ? 'id') OR (jsonb_typeof(((v->'committed')->'id')) = 'string' AND (((v->'committed')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'action') OR (((v->'committed')->'action') = '"file_read"'::jsonb OR ((v->'committed')->'action') = '"file_download"'::jsonb OR ((v->'committed')->'action') = '"message_read"'::jsonb OR ((v->'committed')->'action') = '"thread_opened"'::jsonb OR ((v->'committed')->'action') = '"video_joined"'::jsonb OR ((v->'committed')->'action') = '"location_revealed"'::jsonb OR ((v->'committed')->'action') = '"privacy_export_generated"'::jsonb OR ((v->'committed')->'action') = '"privacy_erasure_started"'::jsonb OR ((v->'committed')->'action') = '"privacy_erasure_completed"'::jsonb OR ((v->'committed')->'action') = '"healthcare_policy_checked"'::jsonb OR ((v->'committed')->'action') = '"healthcare_payload_redacted"'::jsonb OR ((v->'committed')->'action') = '"healthcare_payload_blocked"'::jsonb OR ((v->'committed')->'action') = '"admin_redacted_view"'::jsonb OR ((v->'committed')->'action') = '"admin_blocked_view"'::jsonb OR ((v->'committed')->'action') = '"processor_balance_read"'::jsonb OR ((v->'committed')->'action') = '"payout_account_read"'::jsonb OR ((v->'committed')->'action') = '"tax_profile_read"'::jsonb OR ((v->'committed')->'action') = '"tax_dashboard_opened"'::jsonb OR ((v->'committed')->'action') = '"payout_request_started"'::jsonb OR ((v->'committed')->'action') = '"sensitive_financial_step_up_verified"'::jsonb OR ((v->'committed')->'action') = '"phone_number_changed"'::jsonb OR ((v->'committed')->'action') = '"account_recovery_completed"'::jsonb OR ((v->'committed')->'action') = '"course_video_started"'::jsonb OR ((v->'committed')->'action') = '"course_video_completed"'::jsonb OR ((v->'committed')->'action') = '"live_video_token_issued"'::jsonb OR ((v->'committed')->'action') = '"digital_download_url_issued"'::jsonb OR ((v->'committed')->'action') = '"digital_download_denied"'::jsonb OR ((v->'committed')->'action') = '"digital_download_started"'::jsonb OR ((v->'committed')->'action') = '"digital_download_completed"'::jsonb OR ((v->'committed')->'action') = '"course_video_playback_granted"'::jsonb OR ((v->'committed')->'action') = '"course_video_playback_denied"'::jsonb OR ((v->'committed')->'action') = '"agreement_viewed"'::jsonb OR ((v->'committed')->'action') = '"agreement_downloaded"'::jsonb OR ((v->'committed')->'action') = '"agreement_signed"'::jsonb OR ((v->'committed')->'action') = '"agreement_hash_verified"'::jsonb OR ((v->'committed')->'action') = '"agreement_tamper_detected"'::jsonb OR ((v->'committed')->'action') = '"agreement_manual_opt_out"'::jsonb OR ((v->'committed')->'action') = '"media_signed_url_issued"'::jsonb OR ((v->'committed')->'action') = '"media_signed_url_denied"'::jsonb OR ((v->'committed')->'action') = '"media_upload_rejected"'::jsonb OR ((v->'committed')->'action') = '"media_malware_detected"'::jsonb OR ((v->'committed')->'action') = '"media_metadata_scrubbed"'::jsonb OR ((v->'committed')->'action') = '"media_quarantined"'::jsonb OR ((v->'committed')->'action') = '"media_promoted_to_ready"'::jsonb OR ((v->'committed')->'action') = '"calendar_connection_started"'::jsonb OR ((v->'committed')->'action') = '"calendar_connection_authorized"'::jsonb OR ((v->'committed')->'action') = '"calendar_connection_revoked"'::jsonb OR ((v->'committed')->'action') = '"calendar_free_busy_synced"'::jsonb OR ((v->'committed')->'action') = '"booking_hold_created"'::jsonb OR ((v->'committed')->'action') = '"booking_confirmed"'::jsonb OR ((v->'committed')->'action') = '"booking_slot_lock_failed"'::jsonb OR ((v->'committed')->'action') = '"booking_orchestration_started"'::jsonb OR ((v->'committed')->'action') = '"booking_orchestration_failed"'::jsonb)) AND (NOT ((v->'committed') ? 'sensitivity') OR (((v->'committed')->'sensitivity') = '"normal"'::jsonb OR ((v->'committed')->'sensitivity') = '"sensitive"'::jsonb OR ((v->'committed')->'sensitivity') = '"healthcare"'::jsonb OR ((v->'committed')->'sensitivity') = '"financial"'::jsonb OR ((v->'committed')->'sensitivity') = '"identity_document"'::jsonb OR ((v->'committed')->'sensitivity') = '"resume"'::jsonb OR ((v->'committed')->'sensitivity') = '"legal_contract"'::jsonb OR ((v->'committed')->'sensitivity') = '"private_message"'::jsonb)) AND (NOT ((v->'committed') ? 'accessDecision') OR ((((v->'committed')->'accessDecision') = '"allowed"'::jsonb OR ((v->'committed')->'accessDecision') = '"redacted"'::jsonb OR ((v->'committed')->'accessDecision') = '"blocked"'::jsonb OR ((v->'committed')->'accessDecision') = '"denied"'::jsonb) OR (jsonb_typeof(((v->'committed')->'accessDecision')) = 'null'))) AND (NOT ((v->'committed') ? 'ipHash') OR ((jsonb_typeof(((v->'committed')->'ipHash')) = 'string') OR (jsonb_typeof(((v->'committed')->'ipHash')) = 'null'))) AND (NOT ((v->'committed') ? 'previousHash') OR ((jsonb_typeof(((v->'committed')->'previousHash')) = 'string') OR (jsonb_typeof(((v->'committed')->'previousHash')) = 'null'))) AND (NOT ((v->'committed') ? 'entryHash') OR ((jsonb_typeof(((v->'committed')->'entryHash')) = 'string') OR (jsonb_typeof(((v->'committed')->'entryHash')) = 'null'))))) AND (NOT (v ? 'decisionRef') OR (jsonb_typeof((v->'decisionRef')) = 'string' AND length(((v->'decisionRef') #>> '{}')) >= 1))),false);
$wa$;

CREATE FUNCTION platform_private.json_evidence_user(v jsonb) RETURNS boolean
LANGUAGE sql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
SELECT COALESCE((jsonb_typeof(v) = 'object' AND v ?& ARRAY['schema','owner','model','primaryKey','committed','decisionRef']::text[] AND (v - ARRAY['schema','owner','model','primaryKey','prior','committed','decisionRef']::text[]) = '{}'::jsonb AND (NOT (v ? 'schema') OR ((v->'schema') = '"database-owner-evidence.v1"'::jsonb)) AND (NOT (v ? 'owner') OR ((v->'owner') = '"identity_access"'::jsonb)) AND (NOT (v ? 'model') OR ((v->'model') = '"User"'::jsonb)) AND (NOT (v ? 'primaryKey') OR (jsonb_typeof((v->'primaryKey')) = 'object' AND (v->'primaryKey') ?& ARRAY['id']::text[] AND ((v->'primaryKey') - ARRAY['id']::text[]) = '{}'::jsonb AND (NOT ((v->'primaryKey') ? 'id') OR (jsonb_typeof(((v->'primaryKey')->'id')) = 'string' AND (((v->'primaryKey')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')))) AND (NOT (v ? 'prior') OR ((v->'prior') = 'null'::jsonb OR (jsonb_typeof((v->'prior')) = 'object' AND (v->'prior') ?& ARRAY['id','revision','privacyGeneration']::text[] AND ((v->'prior') - ARRAY['id','revision','privacyGeneration']::text[]) = '{}'::jsonb AND (NOT ((v->'prior') ? 'id') OR (jsonb_typeof(((v->'prior')->'id')) = 'string' AND (((v->'prior')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'revision') OR (jsonb_typeof(((v->'prior')->'revision')) = 'string' AND (((v->'prior')->'revision') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'prior') ? 'privacyGeneration') OR (jsonb_typeof(((v->'prior')->'privacyGeneration')) = 'string' AND (((v->'prior')->'privacyGeneration') #>> '{}') ~ '^-?[0-9]+$'))))) AND (NOT (v ? 'committed') OR (jsonb_typeof((v->'committed')) = 'object' AND (v->'committed') ?& ARRAY['id','revision','privacyGeneration']::text[] AND ((v->'committed') - ARRAY['id','revision','privacyGeneration']::text[]) = '{}'::jsonb AND (NOT ((v->'committed') ? 'id') OR (jsonb_typeof(((v->'committed')->'id')) = 'string' AND (((v->'committed')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'revision') OR (jsonb_typeof(((v->'committed')->'revision')) = 'string' AND (((v->'committed')->'revision') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'committed') ? 'privacyGeneration') OR (jsonb_typeof(((v->'committed')->'privacyGeneration')) = 'string' AND (((v->'committed')->'privacyGeneration') #>> '{}') ~ '^-?[0-9]+$')))) AND (NOT (v ? 'decisionRef') OR (jsonb_typeof((v->'decisionRef')) = 'string' AND length(((v->'decisionRef') #>> '{}')) >= 1))),false);
$wa$;

CREATE FUNCTION platform_private.json_evidence_userrole(v jsonb) RETURNS boolean
LANGUAGE sql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
SELECT COALESCE((jsonb_typeof(v) = 'object' AND v ?& ARRAY['schema','owner','model','primaryKey','committed','decisionRef']::text[] AND (v - ARRAY['schema','owner','model','primaryKey','prior','committed','decisionRef']::text[]) = '{}'::jsonb AND (NOT (v ? 'schema') OR ((v->'schema') = '"database-owner-evidence.v1"'::jsonb)) AND (NOT (v ? 'owner') OR ((v->'owner') = '"identity_access"'::jsonb)) AND (NOT (v ? 'model') OR ((v->'model') = '"UserRole"'::jsonb)) AND (NOT (v ? 'primaryKey') OR (jsonb_typeof((v->'primaryKey')) = 'object' AND (v->'primaryKey') ?& ARRAY['userId','role']::text[] AND ((v->'primaryKey') - ARRAY['userId','role']::text[]) = '{}'::jsonb AND (NOT ((v->'primaryKey') ? 'userId') OR (jsonb_typeof(((v->'primaryKey')->'userId')) = 'string' AND (((v->'primaryKey')->'userId') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'primaryKey') ? 'role') OR (((v->'primaryKey')->'role') = '"user"'::jsonb OR ((v->'primaryKey')->'role') = '"admin"'::jsonb OR ((v->'primaryKey')->'role') = '"support"'::jsonb)))) AND (NOT (v ? 'prior') OR ((v->'prior') = 'null'::jsonb OR (jsonb_typeof((v->'prior')) = 'object' AND (v->'prior') ?& ARRAY['userId','role','revision']::text[] AND ((v->'prior') - ARRAY['userId','role','revision']::text[]) = '{}'::jsonb AND (NOT ((v->'prior') ? 'userId') OR (jsonb_typeof(((v->'prior')->'userId')) = 'string' AND (((v->'prior')->'userId') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'role') OR (((v->'prior')->'role') = '"user"'::jsonb OR ((v->'prior')->'role') = '"admin"'::jsonb OR ((v->'prior')->'role') = '"support"'::jsonb)) AND (NOT ((v->'prior') ? 'revision') OR (jsonb_typeof(((v->'prior')->'revision')) = 'string' AND (((v->'prior')->'revision') #>> '{}') ~ '^-?[0-9]+$'))))) AND (NOT (v ? 'committed') OR (jsonb_typeof((v->'committed')) = 'object' AND (v->'committed') ?& ARRAY['userId','role','revision']::text[] AND ((v->'committed') - ARRAY['userId','role','revision']::text[]) = '{}'::jsonb AND (NOT ((v->'committed') ? 'userId') OR (jsonb_typeof(((v->'committed')->'userId')) = 'string' AND (((v->'committed')->'userId') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'role') OR (((v->'committed')->'role') = '"user"'::jsonb OR ((v->'committed')->'role') = '"admin"'::jsonb OR ((v->'committed')->'role') = '"support"'::jsonb)) AND (NOT ((v->'committed') ? 'revision') OR (jsonb_typeof(((v->'committed')->'revision')) = 'string' AND (((v->'committed')->'revision') #>> '{}') ~ '^-?[0-9]+$')))) AND (NOT (v ? 'decisionRef') OR (jsonb_typeof((v->'decisionRef')) = 'string' AND length(((v->'decisionRef') #>> '{}')) >= 1))),false);
$wa$;

CREATE FUNCTION platform_private.json_evidence_professionalprofile(v jsonb) RETURNS boolean
LANGUAGE sql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
SELECT COALESCE((jsonb_typeof(v) = 'object' AND v ?& ARRAY['schema','owner','model','primaryKey','committed','decisionRef']::text[] AND (v - ARRAY['schema','owner','model','primaryKey','prior','committed','decisionRef']::text[]) = '{}'::jsonb AND (NOT (v ? 'schema') OR ((v->'schema') = '"database-owner-evidence.v1"'::jsonb)) AND (NOT (v ? 'owner') OR ((v->'owner') = '"professional_eligibility"'::jsonb)) AND (NOT (v ? 'model') OR ((v->'model') = '"ProfessionalProfile"'::jsonb)) AND (NOT (v ? 'primaryKey') OR (jsonb_typeof((v->'primaryKey')) = 'object' AND (v->'primaryKey') ?& ARRAY['id']::text[] AND ((v->'primaryKey') - ARRAY['id']::text[]) = '{}'::jsonb AND (NOT ((v->'primaryKey') ? 'id') OR (jsonb_typeof(((v->'primaryKey')->'id')) = 'string' AND (((v->'primaryKey')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')))) AND (NOT (v ? 'prior') OR ((v->'prior') = 'null'::jsonb OR (jsonb_typeof((v->'prior')) = 'object' AND (v->'prior') ?& ARRAY['id','userId','status','ratingCount','revision','privacyGeneration']::text[] AND ((v->'prior') - ARRAY['id','userId','status','ratingCount','revision','privacyGeneration']::text[]) = '{}'::jsonb AND (NOT ((v->'prior') ? 'id') OR (jsonb_typeof(((v->'prior')->'id')) = 'string' AND (((v->'prior')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'userId') OR (jsonb_typeof(((v->'prior')->'userId')) = 'string' AND (((v->'prior')->'userId') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'status') OR (((v->'prior')->'status') = '"draft"'::jsonb OR ((v->'prior')->'status') = '"active"'::jsonb OR ((v->'prior')->'status') = '"paused"'::jsonb OR ((v->'prior')->'status') = '"suspended"'::jsonb OR ((v->'prior')->'status') = '"archived"'::jsonb)) AND (NOT ((v->'prior') ? 'ratingCount') OR (jsonb_typeof(((v->'prior')->'ratingCount')) = 'number' AND (((v->'prior')->'ratingCount') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'prior') ? 'revision') OR (jsonb_typeof(((v->'prior')->'revision')) = 'string' AND (((v->'prior')->'revision') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'prior') ? 'privacyGeneration') OR (jsonb_typeof(((v->'prior')->'privacyGeneration')) = 'string' AND (((v->'prior')->'privacyGeneration') #>> '{}') ~ '^-?[0-9]+$'))))) AND (NOT (v ? 'committed') OR (jsonb_typeof((v->'committed')) = 'object' AND (v->'committed') ?& ARRAY['id','userId','status','ratingCount','revision','privacyGeneration']::text[] AND ((v->'committed') - ARRAY['id','userId','status','ratingCount','revision','privacyGeneration']::text[]) = '{}'::jsonb AND (NOT ((v->'committed') ? 'id') OR (jsonb_typeof(((v->'committed')->'id')) = 'string' AND (((v->'committed')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'userId') OR (jsonb_typeof(((v->'committed')->'userId')) = 'string' AND (((v->'committed')->'userId') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'status') OR (((v->'committed')->'status') = '"draft"'::jsonb OR ((v->'committed')->'status') = '"active"'::jsonb OR ((v->'committed')->'status') = '"paused"'::jsonb OR ((v->'committed')->'status') = '"suspended"'::jsonb OR ((v->'committed')->'status') = '"archived"'::jsonb)) AND (NOT ((v->'committed') ? 'ratingCount') OR (jsonb_typeof(((v->'committed')->'ratingCount')) = 'number' AND (((v->'committed')->'ratingCount') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'committed') ? 'revision') OR (jsonb_typeof(((v->'committed')->'revision')) = 'string' AND (((v->'committed')->'revision') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'committed') ? 'privacyGeneration') OR (jsonb_typeof(((v->'committed')->'privacyGeneration')) = 'string' AND (((v->'committed')->'privacyGeneration') #>> '{}') ~ '^-?[0-9]+$')))) AND (NOT (v ? 'decisionRef') OR (jsonb_typeof((v->'decisionRef')) = 'string' AND length(((v->'decisionRef') #>> '{}')) >= 1))),false);
$wa$;

CREATE FUNCTION platform_private.json_evidence_customerprofile(v jsonb) RETURNS boolean
LANGUAGE sql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
SELECT COALESCE((jsonb_typeof(v) = 'object' AND v ?& ARRAY['schema','owner','model','primaryKey','committed','decisionRef']::text[] AND (v - ARRAY['schema','owner','model','primaryKey','prior','committed','decisionRef']::text[]) = '{}'::jsonb AND (NOT (v ? 'schema') OR ((v->'schema') = '"database-owner-evidence.v1"'::jsonb)) AND (NOT (v ? 'owner') OR ((v->'owner') = '"customer_buyer_profile"'::jsonb)) AND (NOT (v ? 'model') OR ((v->'model') = '"CustomerProfile"'::jsonb)) AND (NOT (v ? 'primaryKey') OR (jsonb_typeof((v->'primaryKey')) = 'object' AND (v->'primaryKey') ?& ARRAY['id']::text[] AND ((v->'primaryKey') - ARRAY['id']::text[]) = '{}'::jsonb AND (NOT ((v->'primaryKey') ? 'id') OR (jsonb_typeof(((v->'primaryKey')->'id')) = 'string' AND (((v->'primaryKey')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')))) AND (NOT (v ? 'prior') OR ((v->'prior') = 'null'::jsonb OR (jsonb_typeof((v->'prior')) = 'object' AND (v->'prior') ?& ARRAY['id','userId','status','revision','privacyGeneration']::text[] AND ((v->'prior') - ARRAY['id','userId','status','revision','privacyGeneration']::text[]) = '{}'::jsonb AND (NOT ((v->'prior') ? 'id') OR (jsonb_typeof(((v->'prior')->'id')) = 'string' AND (((v->'prior')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'userId') OR (jsonb_typeof(((v->'prior')->'userId')) = 'string' AND (((v->'prior')->'userId') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'status') OR (((v->'prior')->'status') = '"draft"'::jsonb OR ((v->'prior')->'status') = '"active"'::jsonb OR ((v->'prior')->'status') = '"paused"'::jsonb OR ((v->'prior')->'status') = '"suspended"'::jsonb OR ((v->'prior')->'status') = '"archived"'::jsonb)) AND (NOT ((v->'prior') ? 'revision') OR (jsonb_typeof(((v->'prior')->'revision')) = 'string' AND (((v->'prior')->'revision') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'prior') ? 'privacyGeneration') OR (jsonb_typeof(((v->'prior')->'privacyGeneration')) = 'string' AND (((v->'prior')->'privacyGeneration') #>> '{}') ~ '^-?[0-9]+$'))))) AND (NOT (v ? 'committed') OR (jsonb_typeof((v->'committed')) = 'object' AND (v->'committed') ?& ARRAY['id','userId','status','revision','privacyGeneration']::text[] AND ((v->'committed') - ARRAY['id','userId','status','revision','privacyGeneration']::text[]) = '{}'::jsonb AND (NOT ((v->'committed') ? 'id') OR (jsonb_typeof(((v->'committed')->'id')) = 'string' AND (((v->'committed')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'userId') OR (jsonb_typeof(((v->'committed')->'userId')) = 'string' AND (((v->'committed')->'userId') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'status') OR (((v->'committed')->'status') = '"draft"'::jsonb OR ((v->'committed')->'status') = '"active"'::jsonb OR ((v->'committed')->'status') = '"paused"'::jsonb OR ((v->'committed')->'status') = '"suspended"'::jsonb OR ((v->'committed')->'status') = '"archived"'::jsonb)) AND (NOT ((v->'committed') ? 'revision') OR (jsonb_typeof(((v->'committed')->'revision')) = 'string' AND (((v->'committed')->'revision') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'committed') ? 'privacyGeneration') OR (jsonb_typeof(((v->'committed')->'privacyGeneration')) = 'string' AND (((v->'committed')->'privacyGeneration') #>> '{}') ~ '^-?[0-9]+$')))) AND (NOT (v ? 'decisionRef') OR (jsonb_typeof((v->'decisionRef')) = 'string' AND length(((v->'decisionRef') #>> '{}')) >= 1))),false);
$wa$;

CREATE FUNCTION platform_private.json_evidence_candidateprofile(v jsonb) RETURNS boolean
LANGUAGE sql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
SELECT COALESCE((jsonb_typeof(v) = 'object' AND v ?& ARRAY['schema','owner','model','primaryKey','committed','decisionRef']::text[] AND (v - ARRAY['schema','owner','model','primaryKey','prior','committed','decisionRef']::text[]) = '{}'::jsonb AND (NOT (v ? 'schema') OR ((v->'schema') = '"database-owner-evidence.v1"'::jsonb)) AND (NOT (v ? 'owner') OR ((v->'owner') = '"candidate_application_resume_privacy"'::jsonb)) AND (NOT (v ? 'model') OR ((v->'model') = '"CandidateProfile"'::jsonb)) AND (NOT (v ? 'primaryKey') OR (jsonb_typeof((v->'primaryKey')) = 'object' AND (v->'primaryKey') ?& ARRAY['id']::text[] AND ((v->'primaryKey') - ARRAY['id']::text[]) = '{}'::jsonb AND (NOT ((v->'primaryKey') ? 'id') OR (jsonb_typeof(((v->'primaryKey')->'id')) = 'string' AND (((v->'primaryKey')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')))) AND (NOT (v ? 'prior') OR ((v->'prior') = 'null'::jsonb OR (jsonb_typeof((v->'prior')) = 'object' AND (v->'prior') ?& ARRAY['id','userId','status','revision','privacyGeneration','discoveryPreferenceRevision']::text[] AND ((v->'prior') - ARRAY['id','userId','status','revision','privacyGeneration','discoveryPreferenceRevision']::text[]) = '{}'::jsonb AND (NOT ((v->'prior') ? 'id') OR (jsonb_typeof(((v->'prior')->'id')) = 'string' AND (((v->'prior')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'userId') OR (jsonb_typeof(((v->'prior')->'userId')) = 'string' AND (((v->'prior')->'userId') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'status') OR (((v->'prior')->'status') = '"draft"'::jsonb OR ((v->'prior')->'status') = '"active"'::jsonb OR ((v->'prior')->'status') = '"paused"'::jsonb OR ((v->'prior')->'status') = '"suspended"'::jsonb OR ((v->'prior')->'status') = '"archived"'::jsonb)) AND (NOT ((v->'prior') ? 'revision') OR (jsonb_typeof(((v->'prior')->'revision')) = 'string' AND (((v->'prior')->'revision') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'prior') ? 'privacyGeneration') OR (jsonb_typeof(((v->'prior')->'privacyGeneration')) = 'string' AND (((v->'prior')->'privacyGeneration') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'prior') ? 'discoveryPreferenceRevision') OR (jsonb_typeof(((v->'prior')->'discoveryPreferenceRevision')) = 'string' AND (((v->'prior')->'discoveryPreferenceRevision') #>> '{}') ~ '^-?[0-9]+$'))))) AND (NOT (v ? 'committed') OR (jsonb_typeof((v->'committed')) = 'object' AND (v->'committed') ?& ARRAY['id','userId','status','revision','privacyGeneration','discoveryPreferenceRevision']::text[] AND ((v->'committed') - ARRAY['id','userId','status','revision','privacyGeneration','discoveryPreferenceRevision']::text[]) = '{}'::jsonb AND (NOT ((v->'committed') ? 'id') OR (jsonb_typeof(((v->'committed')->'id')) = 'string' AND (((v->'committed')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'userId') OR (jsonb_typeof(((v->'committed')->'userId')) = 'string' AND (((v->'committed')->'userId') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'status') OR (((v->'committed')->'status') = '"draft"'::jsonb OR ((v->'committed')->'status') = '"active"'::jsonb OR ((v->'committed')->'status') = '"paused"'::jsonb OR ((v->'committed')->'status') = '"suspended"'::jsonb OR ((v->'committed')->'status') = '"archived"'::jsonb)) AND (NOT ((v->'committed') ? 'revision') OR (jsonb_typeof(((v->'committed')->'revision')) = 'string' AND (((v->'committed')->'revision') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'committed') ? 'privacyGeneration') OR (jsonb_typeof(((v->'committed')->'privacyGeneration')) = 'string' AND (((v->'committed')->'privacyGeneration') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'committed') ? 'discoveryPreferenceRevision') OR (jsonb_typeof(((v->'committed')->'discoveryPreferenceRevision')) = 'string' AND (((v->'committed')->'discoveryPreferenceRevision') #>> '{}') ~ '^-?[0-9]+$')))) AND (NOT (v ? 'decisionRef') OR (jsonb_typeof((v->'decisionRef')) = 'string' AND length(((v->'decisionRef') #>> '{}')) >= 1))),false);
$wa$;

CREATE FUNCTION platform_private.json_evidence_auditevent(v jsonb) RETURNS boolean
LANGUAGE sql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
SELECT COALESCE((jsonb_typeof(v) = 'object' AND v ?& ARRAY['schema','owner','model','primaryKey','committed','decisionRef']::text[] AND (v - ARRAY['schema','owner','model','primaryKey','prior','committed','decisionRef']::text[]) = '{}'::jsonb AND (NOT (v ? 'schema') OR ((v->'schema') = '"database-owner-evidence.v1"'::jsonb)) AND (NOT (v ? 'owner') OR ((v->'owner') = '"audit_event_ledger"'::jsonb)) AND (NOT (v ? 'model') OR ((v->'model') = '"AuditEvent"'::jsonb)) AND (NOT (v ? 'primaryKey') OR (jsonb_typeof((v->'primaryKey')) = 'object' AND (v->'primaryKey') ?& ARRAY['id']::text[] AND ((v->'primaryKey') - ARRAY['id']::text[]) = '{}'::jsonb AND (NOT ((v->'primaryKey') ? 'id') OR (jsonb_typeof(((v->'primaryKey')->'id')) = 'string' AND (((v->'primaryKey')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')))) AND (NOT (v ? 'prior') OR ((v->'prior') = 'null'::jsonb OR (jsonb_typeof((v->'prior')) = 'object' AND (v->'prior') ?& ARRAY['id']::text[] AND ((v->'prior') - ARRAY['id']::text[]) = '{}'::jsonb AND (NOT ((v->'prior') ? 'id') OR (jsonb_typeof(((v->'prior')->'id')) = 'string' AND (((v->'prior')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'))))) AND (NOT (v ? 'committed') OR (jsonb_typeof((v->'committed')) = 'object' AND (v->'committed') ?& ARRAY['id']::text[] AND ((v->'committed') - ARRAY['id']::text[]) = '{}'::jsonb AND (NOT ((v->'committed') ? 'id') OR (jsonb_typeof(((v->'committed')->'id')) = 'string' AND (((v->'committed')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')))) AND (NOT (v ? 'decisionRef') OR (jsonb_typeof((v->'decisionRef')) = 'string' AND length(((v->'decisionRef') #>> '{}')) >= 1))),false);
$wa$;

CREATE FUNCTION platform_private.json_evidence_usersecurityprofile(v jsonb) RETURNS boolean
LANGUAGE sql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
SELECT COALESCE((jsonb_typeof(v) = 'object' AND v ?& ARRAY['schema','owner','model','primaryKey','committed','decisionRef']::text[] AND (v - ARRAY['schema','owner','model','primaryKey','prior','committed','decisionRef']::text[]) = '{}'::jsonb AND (NOT (v ? 'schema') OR ((v->'schema') = '"database-owner-evidence.v1"'::jsonb)) AND (NOT (v ? 'owner') OR ((v->'owner') = '"identity_access"'::jsonb)) AND (NOT (v ? 'model') OR ((v->'model') = '"UserSecurityProfile"'::jsonb)) AND (NOT (v ? 'primaryKey') OR (jsonb_typeof((v->'primaryKey')) = 'object' AND (v->'primaryKey') ?& ARRAY['id']::text[] AND ((v->'primaryKey') - ARRAY['id']::text[]) = '{}'::jsonb AND (NOT ((v->'primaryKey') ? 'id') OR (jsonb_typeof(((v->'primaryKey')->'id')) = 'string' AND (((v->'primaryKey')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')))) AND (NOT (v ? 'prior') OR ((v->'prior') = 'null'::jsonb OR (jsonb_typeof((v->'prior')) = 'object' AND (v->'prior') ?& ARRAY['id','userId','securityTier','phoneNumberHash','revision','securityGeneration']::text[] AND ((v->'prior') - ARRAY['id','userId','securityTier','phoneNumberHash','revision','securityGeneration']::text[]) = '{}'::jsonb AND (NOT ((v->'prior') ? 'id') OR (jsonb_typeof(((v->'prior')->'id')) = 'string' AND (((v->'prior')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'userId') OR (jsonb_typeof(((v->'prior')->'userId')) = 'string' AND (((v->'prior')->'userId') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'securityTier') OR (((v->'prior')->'securityTier') = '"standard"'::jsonb OR ((v->'prior')->'securityTier') = '"elevated"'::jsonb OR ((v->'prior')->'securityTier') = '"high_risk"'::jsonb)) AND (NOT ((v->'prior') ? 'phoneNumberHash') OR ((jsonb_typeof(((v->'prior')->'phoneNumberHash')) = 'string') OR (jsonb_typeof(((v->'prior')->'phoneNumberHash')) = 'null'))) AND (NOT ((v->'prior') ? 'revision') OR (jsonb_typeof(((v->'prior')->'revision')) = 'string' AND (((v->'prior')->'revision') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'prior') ? 'securityGeneration') OR (jsonb_typeof(((v->'prior')->'securityGeneration')) = 'string' AND (((v->'prior')->'securityGeneration') #>> '{}') ~ '^-?[0-9]+$'))))) AND (NOT (v ? 'committed') OR (jsonb_typeof((v->'committed')) = 'object' AND (v->'committed') ?& ARRAY['id','userId','securityTier','phoneNumberHash','revision','securityGeneration']::text[] AND ((v->'committed') - ARRAY['id','userId','securityTier','phoneNumberHash','revision','securityGeneration']::text[]) = '{}'::jsonb AND (NOT ((v->'committed') ? 'id') OR (jsonb_typeof(((v->'committed')->'id')) = 'string' AND (((v->'committed')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'userId') OR (jsonb_typeof(((v->'committed')->'userId')) = 'string' AND (((v->'committed')->'userId') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'securityTier') OR (((v->'committed')->'securityTier') = '"standard"'::jsonb OR ((v->'committed')->'securityTier') = '"elevated"'::jsonb OR ((v->'committed')->'securityTier') = '"high_risk"'::jsonb)) AND (NOT ((v->'committed') ? 'phoneNumberHash') OR ((jsonb_typeof(((v->'committed')->'phoneNumberHash')) = 'string') OR (jsonb_typeof(((v->'committed')->'phoneNumberHash')) = 'null'))) AND (NOT ((v->'committed') ? 'revision') OR (jsonb_typeof(((v->'committed')->'revision')) = 'string' AND (((v->'committed')->'revision') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'committed') ? 'securityGeneration') OR (jsonb_typeof(((v->'committed')->'securityGeneration')) = 'string' AND (((v->'committed')->'securityGeneration') #>> '{}') ~ '^-?[0-9]+$')))) AND (NOT (v ? 'decisionRef') OR (jsonb_typeof((v->'decisionRef')) = 'string' AND length(((v->'decisionRef') #>> '{}')) >= 1))),false);
$wa$;

CREATE FUNCTION platform_private.json_evidence_authprovideraccount(v jsonb) RETURNS boolean
LANGUAGE sql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
SELECT COALESCE((jsonb_typeof(v) = 'object' AND v ?& ARRAY['schema','owner','model','primaryKey','committed','decisionRef']::text[] AND (v - ARRAY['schema','owner','model','primaryKey','prior','committed','decisionRef']::text[]) = '{}'::jsonb AND (NOT (v ? 'schema') OR ((v->'schema') = '"database-owner-evidence.v1"'::jsonb)) AND (NOT (v ? 'owner') OR ((v->'owner') = '"identity_access"'::jsonb)) AND (NOT (v ? 'model') OR ((v->'model') = '"AuthProviderAccount"'::jsonb)) AND (NOT (v ? 'primaryKey') OR (jsonb_typeof((v->'primaryKey')) = 'object' AND (v->'primaryKey') ?& ARRAY['id']::text[] AND ((v->'primaryKey') - ARRAY['id']::text[]) = '{}'::jsonb AND (NOT ((v->'primaryKey') ? 'id') OR (jsonb_typeof(((v->'primaryKey')->'id')) = 'string' AND (((v->'primaryKey')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')))) AND (NOT (v ? 'prior') OR ((v->'prior') = 'null'::jsonb OR (jsonb_typeof((v->'prior')) = 'object' AND (v->'prior') ?& ARRAY['id','userId','providerType','status','revision']::text[] AND ((v->'prior') - ARRAY['id','userId','providerType','status','revision']::text[]) = '{}'::jsonb AND (NOT ((v->'prior') ? 'id') OR (jsonb_typeof(((v->'prior')->'id')) = 'string' AND (((v->'prior')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'userId') OR (jsonb_typeof(((v->'prior')->'userId')) = 'string' AND (((v->'prior')->'userId') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'providerType') OR (((v->'prior')->'providerType') = '"email_password"'::jsonb OR ((v->'prior')->'providerType') = '"google"'::jsonb OR ((v->'prior')->'providerType') = '"apple"'::jsonb OR ((v->'prior')->'providerType') = '"passkey"'::jsonb OR ((v->'prior')->'providerType') = '"magic_link"'::jsonb OR ((v->'prior')->'providerType') = '"sso"'::jsonb OR ((v->'prior')->'providerType') = '"other"'::jsonb)) AND (NOT ((v->'prior') ? 'status') OR (((v->'prior')->'status') = '"active"'::jsonb OR ((v->'prior')->'status') = '"disabled"'::jsonb OR ((v->'prior')->'status') = '"revoked"'::jsonb OR ((v->'prior')->'status') = '"expired"'::jsonb OR ((v->'prior')->'status') = '"compromised"'::jsonb)) AND (NOT ((v->'prior') ? 'revision') OR (jsonb_typeof(((v->'prior')->'revision')) = 'string' AND (((v->'prior')->'revision') #>> '{}') ~ '^-?[0-9]+$'))))) AND (NOT (v ? 'committed') OR (jsonb_typeof((v->'committed')) = 'object' AND (v->'committed') ?& ARRAY['id','userId','providerType','status','revision']::text[] AND ((v->'committed') - ARRAY['id','userId','providerType','status','revision']::text[]) = '{}'::jsonb AND (NOT ((v->'committed') ? 'id') OR (jsonb_typeof(((v->'committed')->'id')) = 'string' AND (((v->'committed')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'userId') OR (jsonb_typeof(((v->'committed')->'userId')) = 'string' AND (((v->'committed')->'userId') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'providerType') OR (((v->'committed')->'providerType') = '"email_password"'::jsonb OR ((v->'committed')->'providerType') = '"google"'::jsonb OR ((v->'committed')->'providerType') = '"apple"'::jsonb OR ((v->'committed')->'providerType') = '"passkey"'::jsonb OR ((v->'committed')->'providerType') = '"magic_link"'::jsonb OR ((v->'committed')->'providerType') = '"sso"'::jsonb OR ((v->'committed')->'providerType') = '"other"'::jsonb)) AND (NOT ((v->'committed') ? 'status') OR (((v->'committed')->'status') = '"active"'::jsonb OR ((v->'committed')->'status') = '"disabled"'::jsonb OR ((v->'committed')->'status') = '"revoked"'::jsonb OR ((v->'committed')->'status') = '"expired"'::jsonb OR ((v->'committed')->'status') = '"compromised"'::jsonb)) AND (NOT ((v->'committed') ? 'revision') OR (jsonb_typeof(((v->'committed')->'revision')) = 'string' AND (((v->'committed')->'revision') #>> '{}') ~ '^-?[0-9]+$')))) AND (NOT (v ? 'decisionRef') OR (jsonb_typeof((v->'decisionRef')) = 'string' AND length(((v->'decisionRef') #>> '{}')) >= 1))),false);
$wa$;

CREATE FUNCTION platform_private.json_evidence_trackplan(v jsonb) RETURNS boolean
LANGUAGE sql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
SELECT COALESCE((jsonb_typeof(v) = 'object' AND v ?& ARRAY['schema','owner','model','primaryKey','committed','decisionRef']::text[] AND (v - ARRAY['schema','owner','model','primaryKey','prior','committed','decisionRef']::text[]) = '{}'::jsonb AND (NOT (v ? 'schema') OR ((v->'schema') = '"database-owner-evidence.v1"'::jsonb)) AND (NOT (v ? 'owner') OR ((v->'owner') = '"track_subscription_entitlement"'::jsonb)) AND (NOT (v ? 'model') OR ((v->'model') = '"TrackPlan"'::jsonb)) AND (NOT (v ? 'primaryKey') OR (jsonb_typeof((v->'primaryKey')) = 'object' AND (v->'primaryKey') ?& ARRAY['id']::text[] AND ((v->'primaryKey') - ARRAY['id']::text[]) = '{}'::jsonb AND (NOT ((v->'primaryKey') ? 'id') OR (jsonb_typeof(((v->'primaryKey')->'id')) = 'string' AND (((v->'primaryKey')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')))) AND (NOT (v ? 'prior') OR ((v->'prior') = 'null'::jsonb OR (jsonb_typeof((v->'prior')) = 'object' AND (v->'prior') ?& ARRAY['id','track','status','billingModel','monthlyPriceCents','currency','revision','contentHash']::text[] AND ((v->'prior') - ARRAY['id','track','status','billingModel','monthlyPriceCents','currency','revision','contentHash']::text[]) = '{}'::jsonb AND (NOT ((v->'prior') ? 'id') OR (jsonb_typeof(((v->'prior')->'id')) = 'string' AND (((v->'prior')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'track') OR (((v->'prior')->'track') = '"customer"'::jsonb OR ((v->'prior')->'track') = '"candidate"'::jsonb OR ((v->'prior')->'track') = '"professional"'::jsonb)) AND (NOT ((v->'prior') ? 'status') OR (((v->'prior')->'status') = '"draft"'::jsonb OR ((v->'prior')->'status') = '"active"'::jsonb OR ((v->'prior')->'status') = '"retired"'::jsonb OR ((v->'prior')->'status') = '"archived"'::jsonb)) AND (NOT ((v->'prior') ? 'billingModel') OR (((v->'prior')->'billingModel') = '"free"'::jsonb OR ((v->'prior')->'billingModel') = '"subscription"'::jsonb OR ((v->'prior')->'billingModel') = '"commission"'::jsonb OR ((v->'prior')->'billingModel') = '"subscription_plus_commission"'::jsonb OR ((v->'prior')->'billingModel') = '"transaction_perk"'::jsonb OR ((v->'prior')->'billingModel') = '"manual"'::jsonb)) AND (NOT ((v->'prior') ? 'monthlyPriceCents') OR ((jsonb_typeof(((v->'prior')->'monthlyPriceCents')) = 'number' AND (((v->'prior')->'monthlyPriceCents') #>> '{}') ~ '^-?[0-9]+$') OR (jsonb_typeof(((v->'prior')->'monthlyPriceCents')) = 'null'))) AND (NOT ((v->'prior') ? 'currency') OR (jsonb_typeof(((v->'prior')->'currency')) = 'string')) AND (NOT ((v->'prior') ? 'revision') OR (jsonb_typeof(((v->'prior')->'revision')) = 'string' AND (((v->'prior')->'revision') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'prior') ? 'contentHash') OR (jsonb_typeof(((v->'prior')->'contentHash')) = 'string'))))) AND (NOT (v ? 'committed') OR (jsonb_typeof((v->'committed')) = 'object' AND (v->'committed') ?& ARRAY['id','track','status','billingModel','monthlyPriceCents','currency','revision','contentHash']::text[] AND ((v->'committed') - ARRAY['id','track','status','billingModel','monthlyPriceCents','currency','revision','contentHash']::text[]) = '{}'::jsonb AND (NOT ((v->'committed') ? 'id') OR (jsonb_typeof(((v->'committed')->'id')) = 'string' AND (((v->'committed')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'track') OR (((v->'committed')->'track') = '"customer"'::jsonb OR ((v->'committed')->'track') = '"candidate"'::jsonb OR ((v->'committed')->'track') = '"professional"'::jsonb)) AND (NOT ((v->'committed') ? 'status') OR (((v->'committed')->'status') = '"draft"'::jsonb OR ((v->'committed')->'status') = '"active"'::jsonb OR ((v->'committed')->'status') = '"retired"'::jsonb OR ((v->'committed')->'status') = '"archived"'::jsonb)) AND (NOT ((v->'committed') ? 'billingModel') OR (((v->'committed')->'billingModel') = '"free"'::jsonb OR ((v->'committed')->'billingModel') = '"subscription"'::jsonb OR ((v->'committed')->'billingModel') = '"commission"'::jsonb OR ((v->'committed')->'billingModel') = '"subscription_plus_commission"'::jsonb OR ((v->'committed')->'billingModel') = '"transaction_perk"'::jsonb OR ((v->'committed')->'billingModel') = '"manual"'::jsonb)) AND (NOT ((v->'committed') ? 'monthlyPriceCents') OR ((jsonb_typeof(((v->'committed')->'monthlyPriceCents')) = 'number' AND (((v->'committed')->'monthlyPriceCents') #>> '{}') ~ '^-?[0-9]+$') OR (jsonb_typeof(((v->'committed')->'monthlyPriceCents')) = 'null'))) AND (NOT ((v->'committed') ? 'currency') OR (jsonb_typeof(((v->'committed')->'currency')) = 'string')) AND (NOT ((v->'committed') ? 'revision') OR (jsonb_typeof(((v->'committed')->'revision')) = 'string' AND (((v->'committed')->'revision') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'committed') ? 'contentHash') OR (jsonb_typeof(((v->'committed')->'contentHash')) = 'string')))) AND (NOT (v ? 'decisionRef') OR (jsonb_typeof((v->'decisionRef')) = 'string' AND length(((v->'decisionRef') #>> '{}')) >= 1))),false);
$wa$;

CREATE FUNCTION platform_private.json_evidence_trackentitlementdefinition(v jsonb) RETURNS boolean
LANGUAGE sql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
SELECT COALESCE((jsonb_typeof(v) = 'object' AND v ?& ARRAY['schema','owner','model','primaryKey','committed','decisionRef']::text[] AND (v - ARRAY['schema','owner','model','primaryKey','prior','committed','decisionRef']::text[]) = '{}'::jsonb AND (NOT (v ? 'schema') OR ((v->'schema') = '"database-owner-evidence.v1"'::jsonb)) AND (NOT (v ? 'owner') OR ((v->'owner') = '"track_subscription_entitlement"'::jsonb)) AND (NOT (v ? 'model') OR ((v->'model') = '"TrackEntitlementDefinition"'::jsonb)) AND (NOT (v ? 'primaryKey') OR (jsonb_typeof((v->'primaryKey')) = 'object' AND (v->'primaryKey') ?& ARRAY['id']::text[] AND ((v->'primaryKey') - ARRAY['id']::text[]) = '{}'::jsonb AND (NOT ((v->'primaryKey') ? 'id') OR (jsonb_typeof(((v->'primaryKey')->'id')) = 'string' AND (((v->'primaryKey')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')))) AND (NOT (v ? 'prior') OR ((v->'prior') = 'null'::jsonb OR (jsonb_typeof((v->'prior')) = 'object' AND (v->'prior') ?& ARRAY['id','valueType','track','revision']::text[] AND ((v->'prior') - ARRAY['id','valueType','track','revision']::text[]) = '{}'::jsonb AND (NOT ((v->'prior') ? 'id') OR (jsonb_typeof(((v->'prior')->'id')) = 'string' AND (((v->'prior')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'valueType') OR (((v->'prior')->'valueType') = '"boolean"'::jsonb OR ((v->'prior')->'valueType') = '"integer"'::jsonb OR ((v->'prior')->'valueType') = '"decimal"'::jsonb OR ((v->'prior')->'valueType') = '"percent_bps"'::jsonb OR ((v->'prior')->'valueType') = '"money_cents"'::jsonb OR ((v->'prior')->'valueType') = '"string"'::jsonb OR ((v->'prior')->'valueType') = '"json"'::jsonb)) AND (NOT ((v->'prior') ? 'track') OR ((((v->'prior')->'track') = '"customer"'::jsonb OR ((v->'prior')->'track') = '"candidate"'::jsonb OR ((v->'prior')->'track') = '"professional"'::jsonb) OR (jsonb_typeof(((v->'prior')->'track')) = 'null'))) AND (NOT ((v->'prior') ? 'revision') OR (jsonb_typeof(((v->'prior')->'revision')) = 'string' AND (((v->'prior')->'revision') #>> '{}') ~ '^-?[0-9]+$'))))) AND (NOT (v ? 'committed') OR (jsonb_typeof((v->'committed')) = 'object' AND (v->'committed') ?& ARRAY['id','valueType','track','revision']::text[] AND ((v->'committed') - ARRAY['id','valueType','track','revision']::text[]) = '{}'::jsonb AND (NOT ((v->'committed') ? 'id') OR (jsonb_typeof(((v->'committed')->'id')) = 'string' AND (((v->'committed')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'valueType') OR (((v->'committed')->'valueType') = '"boolean"'::jsonb OR ((v->'committed')->'valueType') = '"integer"'::jsonb OR ((v->'committed')->'valueType') = '"decimal"'::jsonb OR ((v->'committed')->'valueType') = '"percent_bps"'::jsonb OR ((v->'committed')->'valueType') = '"money_cents"'::jsonb OR ((v->'committed')->'valueType') = '"string"'::jsonb OR ((v->'committed')->'valueType') = '"json"'::jsonb)) AND (NOT ((v->'committed') ? 'track') OR ((((v->'committed')->'track') = '"customer"'::jsonb OR ((v->'committed')->'track') = '"candidate"'::jsonb OR ((v->'committed')->'track') = '"professional"'::jsonb) OR (jsonb_typeof(((v->'committed')->'track')) = 'null'))) AND (NOT ((v->'committed') ? 'revision') OR (jsonb_typeof(((v->'committed')->'revision')) = 'string' AND (((v->'committed')->'revision') #>> '{}') ~ '^-?[0-9]+$')))) AND (NOT (v ? 'decisionRef') OR (jsonb_typeof((v->'decisionRef')) = 'string' AND length(((v->'decisionRef') #>> '{}')) >= 1))),false);
$wa$;

CREATE FUNCTION platform_private.json_evidence_trackplanentitlement(v jsonb) RETURNS boolean
LANGUAGE sql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
SELECT COALESCE((jsonb_typeof(v) = 'object' AND v ?& ARRAY['schema','owner','model','primaryKey','committed','decisionRef']::text[] AND (v - ARRAY['schema','owner','model','primaryKey','prior','committed','decisionRef']::text[]) = '{}'::jsonb AND (NOT (v ? 'schema') OR ((v->'schema') = '"database-owner-evidence.v1"'::jsonb)) AND (NOT (v ? 'owner') OR ((v->'owner') = '"track_subscription_entitlement"'::jsonb)) AND (NOT (v ? 'model') OR ((v->'model') = '"TrackPlanEntitlement"'::jsonb)) AND (NOT (v ? 'primaryKey') OR (jsonb_typeof((v->'primaryKey')) = 'object' AND (v->'primaryKey') ?& ARRAY['id']::text[] AND ((v->'primaryKey') - ARRAY['id']::text[]) = '{}'::jsonb AND (NOT ((v->'primaryKey') ? 'id') OR (jsonb_typeof(((v->'primaryKey')->'id')) = 'string' AND (((v->'primaryKey')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')))) AND (NOT (v ? 'prior') OR ((v->'prior') = 'null'::jsonb OR (jsonb_typeof((v->'prior')) = 'object' AND (v->'prior') ?& ARRAY['id','valueType','usagePeriod','revision']::text[] AND ((v->'prior') - ARRAY['id','valueType','usagePeriod','revision']::text[]) = '{}'::jsonb AND (NOT ((v->'prior') ? 'id') OR (jsonb_typeof(((v->'prior')->'id')) = 'string' AND (((v->'prior')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'valueType') OR (((v->'prior')->'valueType') = '"boolean"'::jsonb OR ((v->'prior')->'valueType') = '"integer"'::jsonb OR ((v->'prior')->'valueType') = '"decimal"'::jsonb OR ((v->'prior')->'valueType') = '"percent_bps"'::jsonb OR ((v->'prior')->'valueType') = '"money_cents"'::jsonb OR ((v->'prior')->'valueType') = '"string"'::jsonb OR ((v->'prior')->'valueType') = '"json"'::jsonb)) AND (NOT ((v->'prior') ? 'usagePeriod') OR ((((v->'prior')->'usagePeriod') = '"once"'::jsonb OR ((v->'prior')->'usagePeriod') = '"daily"'::jsonb OR ((v->'prior')->'usagePeriod') = '"monthly"'::jsonb OR ((v->'prior')->'usagePeriod') = '"yearly"'::jsonb OR ((v->'prior')->'usagePeriod') = '"lifetime"'::jsonb OR ((v->'prior')->'usagePeriod') = '"rolling_30_day"'::jsonb) OR (jsonb_typeof(((v->'prior')->'usagePeriod')) = 'null'))) AND (NOT ((v->'prior') ? 'revision') OR (jsonb_typeof(((v->'prior')->'revision')) = 'string' AND (((v->'prior')->'revision') #>> '{}') ~ '^-?[0-9]+$'))))) AND (NOT (v ? 'committed') OR (jsonb_typeof((v->'committed')) = 'object' AND (v->'committed') ?& ARRAY['id','valueType','usagePeriod','revision']::text[] AND ((v->'committed') - ARRAY['id','valueType','usagePeriod','revision']::text[]) = '{}'::jsonb AND (NOT ((v->'committed') ? 'id') OR (jsonb_typeof(((v->'committed')->'id')) = 'string' AND (((v->'committed')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'valueType') OR (((v->'committed')->'valueType') = '"boolean"'::jsonb OR ((v->'committed')->'valueType') = '"integer"'::jsonb OR ((v->'committed')->'valueType') = '"decimal"'::jsonb OR ((v->'committed')->'valueType') = '"percent_bps"'::jsonb OR ((v->'committed')->'valueType') = '"money_cents"'::jsonb OR ((v->'committed')->'valueType') = '"string"'::jsonb OR ((v->'committed')->'valueType') = '"json"'::jsonb)) AND (NOT ((v->'committed') ? 'usagePeriod') OR ((((v->'committed')->'usagePeriod') = '"once"'::jsonb OR ((v->'committed')->'usagePeriod') = '"daily"'::jsonb OR ((v->'committed')->'usagePeriod') = '"monthly"'::jsonb OR ((v->'committed')->'usagePeriod') = '"yearly"'::jsonb OR ((v->'committed')->'usagePeriod') = '"lifetime"'::jsonb OR ((v->'committed')->'usagePeriod') = '"rolling_30_day"'::jsonb) OR (jsonb_typeof(((v->'committed')->'usagePeriod')) = 'null'))) AND (NOT ((v->'committed') ? 'revision') OR (jsonb_typeof(((v->'committed')->'revision')) = 'string' AND (((v->'committed')->'revision') #>> '{}') ~ '^-?[0-9]+$')))) AND (NOT (v ? 'decisionRef') OR (jsonb_typeof((v->'decisionRef')) = 'string' AND length(((v->'decisionRef') #>> '{}')) >= 1))),false);
$wa$;

CREATE FUNCTION platform_private.json_evidence_tracksubscription(v jsonb) RETURNS boolean
LANGUAGE sql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
SELECT COALESCE((jsonb_typeof(v) = 'object' AND v ?& ARRAY['schema','owner','model','primaryKey','committed','decisionRef']::text[] AND (v - ARRAY['schema','owner','model','primaryKey','prior','committed','decisionRef']::text[]) = '{}'::jsonb AND (NOT (v ? 'schema') OR ((v->'schema') = '"database-owner-evidence.v1"'::jsonb)) AND (NOT (v ? 'owner') OR ((v->'owner') = '"track_subscription_entitlement"'::jsonb)) AND (NOT (v ? 'model') OR ((v->'model') = '"TrackSubscription"'::jsonb)) AND (NOT (v ? 'primaryKey') OR (jsonb_typeof((v->'primaryKey')) = 'object' AND (v->'primaryKey') ?& ARRAY['id']::text[] AND ((v->'primaryKey') - ARRAY['id']::text[]) = '{}'::jsonb AND (NOT ((v->'primaryKey') ? 'id') OR (jsonb_typeof(((v->'primaryKey')->'id')) = 'string' AND (((v->'primaryKey')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')))) AND (NOT (v ? 'prior') OR ((v->'prior') = 'null'::jsonb OR (jsonb_typeof((v->'prior')) = 'object' AND (v->'prior') ?& ARRAY['id','userId','track','status','provider','revision']::text[] AND ((v->'prior') - ARRAY['id','userId','track','status','provider','revision']::text[]) = '{}'::jsonb AND (NOT ((v->'prior') ? 'id') OR (jsonb_typeof(((v->'prior')->'id')) = 'string' AND (((v->'prior')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'userId') OR (jsonb_typeof(((v->'prior')->'userId')) = 'string' AND (((v->'prior')->'userId') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'track') OR (((v->'prior')->'track') = '"customer"'::jsonb OR ((v->'prior')->'track') = '"candidate"'::jsonb OR ((v->'prior')->'track') = '"professional"'::jsonb)) AND (NOT ((v->'prior') ? 'status') OR (((v->'prior')->'status') = '"active"'::jsonb OR ((v->'prior')->'status') = '"trialing"'::jsonb OR ((v->'prior')->'status') = '"past_due"'::jsonb OR ((v->'prior')->'status') = '"cancelled"'::jsonb OR ((v->'prior')->'status') = '"expired"'::jsonb OR ((v->'prior')->'status') = '"paused"'::jsonb OR ((v->'prior')->'status') = '"incomplete"'::jsonb OR ((v->'prior')->'status') = '"incomplete_expired"'::jsonb)) AND (NOT ((v->'prior') ? 'provider') OR (((v->'prior')->'provider') = '"none"'::jsonb OR ((v->'prior')->'provider') = '"stripe"'::jsonb OR ((v->'prior')->'provider') = '"manual"'::jsonb OR ((v->'prior')->'provider') = '"comped"'::jsonb OR ((v->'prior')->'provider') = '"other"'::jsonb)) AND (NOT ((v->'prior') ? 'revision') OR (jsonb_typeof(((v->'prior')->'revision')) = 'string' AND (((v->'prior')->'revision') #>> '{}') ~ '^-?[0-9]+$'))))) AND (NOT (v ? 'committed') OR (jsonb_typeof((v->'committed')) = 'object' AND (v->'committed') ?& ARRAY['id','userId','track','status','provider','revision']::text[] AND ((v->'committed') - ARRAY['id','userId','track','status','provider','revision']::text[]) = '{}'::jsonb AND (NOT ((v->'committed') ? 'id') OR (jsonb_typeof(((v->'committed')->'id')) = 'string' AND (((v->'committed')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'userId') OR (jsonb_typeof(((v->'committed')->'userId')) = 'string' AND (((v->'committed')->'userId') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'track') OR (((v->'committed')->'track') = '"customer"'::jsonb OR ((v->'committed')->'track') = '"candidate"'::jsonb OR ((v->'committed')->'track') = '"professional"'::jsonb)) AND (NOT ((v->'committed') ? 'status') OR (((v->'committed')->'status') = '"active"'::jsonb OR ((v->'committed')->'status') = '"trialing"'::jsonb OR ((v->'committed')->'status') = '"past_due"'::jsonb OR ((v->'committed')->'status') = '"cancelled"'::jsonb OR ((v->'committed')->'status') = '"expired"'::jsonb OR ((v->'committed')->'status') = '"paused"'::jsonb OR ((v->'committed')->'status') = '"incomplete"'::jsonb OR ((v->'committed')->'status') = '"incomplete_expired"'::jsonb)) AND (NOT ((v->'committed') ? 'provider') OR (((v->'committed')->'provider') = '"none"'::jsonb OR ((v->'committed')->'provider') = '"stripe"'::jsonb OR ((v->'committed')->'provider') = '"manual"'::jsonb OR ((v->'committed')->'provider') = '"comped"'::jsonb OR ((v->'committed')->'provider') = '"other"'::jsonb)) AND (NOT ((v->'committed') ? 'revision') OR (jsonb_typeof(((v->'committed')->'revision')) = 'string' AND (((v->'committed')->'revision') #>> '{}') ~ '^-?[0-9]+$')))) AND (NOT (v ? 'decisionRef') OR (jsonb_typeof((v->'decisionRef')) = 'string' AND length(((v->'decisionRef') #>> '{}')) >= 1))),false);
$wa$;

CREATE FUNCTION platform_private.json_evidence_trackentitlementgrant(v jsonb) RETURNS boolean
LANGUAGE sql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
SELECT COALESCE((jsonb_typeof(v) = 'object' AND v ?& ARRAY['schema','owner','model','primaryKey','committed','decisionRef']::text[] AND (v - ARRAY['schema','owner','model','primaryKey','prior','committed','decisionRef']::text[]) = '{}'::jsonb AND (NOT (v ? 'schema') OR ((v->'schema') = '"database-owner-evidence.v1"'::jsonb)) AND (NOT (v ? 'owner') OR ((v->'owner') = '"track_subscription_entitlement"'::jsonb)) AND (NOT (v ? 'model') OR ((v->'model') = '"TrackEntitlementGrant"'::jsonb)) AND (NOT (v ? 'primaryKey') OR (jsonb_typeof((v->'primaryKey')) = 'object' AND (v->'primaryKey') ?& ARRAY['id']::text[] AND ((v->'primaryKey') - ARRAY['id']::text[]) = '{}'::jsonb AND (NOT ((v->'primaryKey') ? 'id') OR (jsonb_typeof(((v->'primaryKey')->'id')) = 'string' AND (((v->'primaryKey')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')))) AND (NOT (v ? 'prior') OR ((v->'prior') = 'null'::jsonb OR (jsonb_typeof((v->'prior')) = 'object' AND (v->'prior') ?& ARRAY['id','userId','track','status','valueType','revision']::text[] AND ((v->'prior') - ARRAY['id','userId','track','status','valueType','revision']::text[]) = '{}'::jsonb AND (NOT ((v->'prior') ? 'id') OR (jsonb_typeof(((v->'prior')->'id')) = 'string' AND (((v->'prior')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'userId') OR (jsonb_typeof(((v->'prior')->'userId')) = 'string' AND (((v->'prior')->'userId') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'track') OR (((v->'prior')->'track') = '"customer"'::jsonb OR ((v->'prior')->'track') = '"candidate"'::jsonb OR ((v->'prior')->'track') = '"professional"'::jsonb)) AND (NOT ((v->'prior') ? 'status') OR (((v->'prior')->'status') = '"active"'::jsonb OR ((v->'prior')->'status') = '"expired"'::jsonb OR ((v->'prior')->'status') = '"revoked"'::jsonb OR ((v->'prior')->'status') = '"suspended"'::jsonb OR ((v->'prior')->'status') = '"consumed"'::jsonb)) AND (NOT ((v->'prior') ? 'valueType') OR (((v->'prior')->'valueType') = '"boolean"'::jsonb OR ((v->'prior')->'valueType') = '"integer"'::jsonb OR ((v->'prior')->'valueType') = '"decimal"'::jsonb OR ((v->'prior')->'valueType') = '"percent_bps"'::jsonb OR ((v->'prior')->'valueType') = '"money_cents"'::jsonb OR ((v->'prior')->'valueType') = '"string"'::jsonb OR ((v->'prior')->'valueType') = '"json"'::jsonb)) AND (NOT ((v->'prior') ? 'revision') OR (jsonb_typeof(((v->'prior')->'revision')) = 'string' AND (((v->'prior')->'revision') #>> '{}') ~ '^-?[0-9]+$'))))) AND (NOT (v ? 'committed') OR (jsonb_typeof((v->'committed')) = 'object' AND (v->'committed') ?& ARRAY['id','userId','track','status','valueType','revision']::text[] AND ((v->'committed') - ARRAY['id','userId','track','status','valueType','revision']::text[]) = '{}'::jsonb AND (NOT ((v->'committed') ? 'id') OR (jsonb_typeof(((v->'committed')->'id')) = 'string' AND (((v->'committed')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'userId') OR (jsonb_typeof(((v->'committed')->'userId')) = 'string' AND (((v->'committed')->'userId') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'track') OR (((v->'committed')->'track') = '"customer"'::jsonb OR ((v->'committed')->'track') = '"candidate"'::jsonb OR ((v->'committed')->'track') = '"professional"'::jsonb)) AND (NOT ((v->'committed') ? 'status') OR (((v->'committed')->'status') = '"active"'::jsonb OR ((v->'committed')->'status') = '"expired"'::jsonb OR ((v->'committed')->'status') = '"revoked"'::jsonb OR ((v->'committed')->'status') = '"suspended"'::jsonb OR ((v->'committed')->'status') = '"consumed"'::jsonb)) AND (NOT ((v->'committed') ? 'valueType') OR (((v->'committed')->'valueType') = '"boolean"'::jsonb OR ((v->'committed')->'valueType') = '"integer"'::jsonb OR ((v->'committed')->'valueType') = '"decimal"'::jsonb OR ((v->'committed')->'valueType') = '"percent_bps"'::jsonb OR ((v->'committed')->'valueType') = '"money_cents"'::jsonb OR ((v->'committed')->'valueType') = '"string"'::jsonb OR ((v->'committed')->'valueType') = '"json"'::jsonb)) AND (NOT ((v->'committed') ? 'revision') OR (jsonb_typeof(((v->'committed')->'revision')) = 'string' AND (((v->'committed')->'revision') #>> '{}') ~ '^-?[0-9]+$')))) AND (NOT (v ? 'decisionRef') OR (jsonb_typeof((v->'decisionRef')) = 'string' AND length(((v->'decisionRef') #>> '{}')) >= 1))),false);
$wa$;

CREATE FUNCTION platform_private.json_evidence_trackusageevent(v jsonb) RETURNS boolean
LANGUAGE sql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
SELECT COALESCE((jsonb_typeof(v) = 'object' AND v ?& ARRAY['schema','owner','model','primaryKey','committed','decisionRef']::text[] AND (v - ARRAY['schema','owner','model','primaryKey','prior','committed','decisionRef']::text[]) = '{}'::jsonb AND (NOT (v ? 'schema') OR ((v->'schema') = '"database-owner-evidence.v1"'::jsonb)) AND (NOT (v ? 'owner') OR ((v->'owner') = '"track_subscription_entitlement"'::jsonb)) AND (NOT (v ? 'model') OR ((v->'model') = '"TrackUsageEvent"'::jsonb)) AND (NOT (v ? 'primaryKey') OR (jsonb_typeof((v->'primaryKey')) = 'object' AND (v->'primaryKey') ?& ARRAY['id']::text[] AND ((v->'primaryKey') - ARRAY['id']::text[]) = '{}'::jsonb AND (NOT ((v->'primaryKey') ? 'id') OR (jsonb_typeof(((v->'primaryKey')->'id')) = 'string' AND (((v->'primaryKey')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')))) AND (NOT (v ? 'prior') OR ((v->'prior') = 'null'::jsonb OR (jsonb_typeof((v->'prior')) = 'object' AND (v->'prior') ?& ARRAY['id','userId','track','type','semanticEffectKey','sourceRevision','sourceOwner','sourceId','acceptedAt','periodStart','periodEnd']::text[] AND ((v->'prior') - ARRAY['id','userId','track','type','semanticEffectKey','sourceRevision','sourceOwner','sourceId','acceptedAt','periodStart','periodEnd']::text[]) = '{}'::jsonb AND (NOT ((v->'prior') ? 'id') OR (jsonb_typeof(((v->'prior')->'id')) = 'string' AND (((v->'prior')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'userId') OR (jsonb_typeof(((v->'prior')->'userId')) = 'string' AND (((v->'prior')->'userId') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'track') OR (((v->'prior')->'track') = '"customer"'::jsonb OR ((v->'prior')->'track') = '"candidate"'::jsonb OR ((v->'prior')->'track') = '"professional"'::jsonb)) AND (NOT ((v->'prior') ? 'type') OR (((v->'prior')->'type') = '"job_application_submitted"'::jsonb OR ((v->'prior')->'type') = '"candidate_search_boost_applied"'::jsonb OR ((v->'prior')->'type') = '"application_view_tracked"'::jsonb OR ((v->'prior')->'type') = '"buyer_fee_waived"'::jsonb OR ((v->'prior')->'type') = '"priority_scheduling_used"'::jsonb OR ((v->'prior')->'type') = '"professional_order_completed"'::jsonb OR ((v->'prior')->'type') = '"professional_commission_applied"'::jsonb OR ((v->'prior')->'type') = '"custom_domain_connected"'::jsonb OR ((v->'prior')->'type') = '"live_streaming_used"'::jsonb OR ((v->'prior')->'type') = '"internal_ad_campaign_created"'::jsonb OR ((v->'prior')->'type') = '"other"'::jsonb)) AND (NOT ((v->'prior') ? 'semanticEffectKey') OR (jsonb_typeof(((v->'prior')->'semanticEffectKey')) = 'string')) AND (NOT ((v->'prior') ? 'sourceRevision') OR (jsonb_typeof(((v->'prior')->'sourceRevision')) = 'string' AND (((v->'prior')->'sourceRevision') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'prior') ? 'sourceOwner') OR (jsonb_typeof(((v->'prior')->'sourceOwner')) = 'string')) AND (NOT ((v->'prior') ? 'sourceId') OR (jsonb_typeof(((v->'prior')->'sourceId')) = 'string')) AND (NOT ((v->'prior') ? 'acceptedAt') OR (jsonb_typeof(((v->'prior')->'acceptedAt')) = 'string' AND platform_private.json_datetime((((v->'prior')->'acceptedAt') #>> '{}')))) AND (NOT ((v->'prior') ? 'periodStart') OR (jsonb_typeof(((v->'prior')->'periodStart')) = 'string' AND platform_private.json_datetime((((v->'prior')->'periodStart') #>> '{}')))) AND (NOT ((v->'prior') ? 'periodEnd') OR (jsonb_typeof(((v->'prior')->'periodEnd')) = 'string' AND platform_private.json_datetime((((v->'prior')->'periodEnd') #>> '{}'))))))) AND (NOT (v ? 'committed') OR (jsonb_typeof((v->'committed')) = 'object' AND (v->'committed') ?& ARRAY['id','userId','track','type','semanticEffectKey','sourceRevision','sourceOwner','sourceId','acceptedAt','periodStart','periodEnd']::text[] AND ((v->'committed') - ARRAY['id','userId','track','type','semanticEffectKey','sourceRevision','sourceOwner','sourceId','acceptedAt','periodStart','periodEnd']::text[]) = '{}'::jsonb AND (NOT ((v->'committed') ? 'id') OR (jsonb_typeof(((v->'committed')->'id')) = 'string' AND (((v->'committed')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'userId') OR (jsonb_typeof(((v->'committed')->'userId')) = 'string' AND (((v->'committed')->'userId') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'track') OR (((v->'committed')->'track') = '"customer"'::jsonb OR ((v->'committed')->'track') = '"candidate"'::jsonb OR ((v->'committed')->'track') = '"professional"'::jsonb)) AND (NOT ((v->'committed') ? 'type') OR (((v->'committed')->'type') = '"job_application_submitted"'::jsonb OR ((v->'committed')->'type') = '"candidate_search_boost_applied"'::jsonb OR ((v->'committed')->'type') = '"application_view_tracked"'::jsonb OR ((v->'committed')->'type') = '"buyer_fee_waived"'::jsonb OR ((v->'committed')->'type') = '"priority_scheduling_used"'::jsonb OR ((v->'committed')->'type') = '"professional_order_completed"'::jsonb OR ((v->'committed')->'type') = '"professional_commission_applied"'::jsonb OR ((v->'committed')->'type') = '"custom_domain_connected"'::jsonb OR ((v->'committed')->'type') = '"live_streaming_used"'::jsonb OR ((v->'committed')->'type') = '"internal_ad_campaign_created"'::jsonb OR ((v->'committed')->'type') = '"other"'::jsonb)) AND (NOT ((v->'committed') ? 'semanticEffectKey') OR (jsonb_typeof(((v->'committed')->'semanticEffectKey')) = 'string')) AND (NOT ((v->'committed') ? 'sourceRevision') OR (jsonb_typeof(((v->'committed')->'sourceRevision')) = 'string' AND (((v->'committed')->'sourceRevision') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'committed') ? 'sourceOwner') OR (jsonb_typeof(((v->'committed')->'sourceOwner')) = 'string')) AND (NOT ((v->'committed') ? 'sourceId') OR (jsonb_typeof(((v->'committed')->'sourceId')) = 'string')) AND (NOT ((v->'committed') ? 'acceptedAt') OR (jsonb_typeof(((v->'committed')->'acceptedAt')) = 'string' AND platform_private.json_datetime((((v->'committed')->'acceptedAt') #>> '{}')))) AND (NOT ((v->'committed') ? 'periodStart') OR (jsonb_typeof(((v->'committed')->'periodStart')) = 'string' AND platform_private.json_datetime((((v->'committed')->'periodStart') #>> '{}')))) AND (NOT ((v->'committed') ? 'periodEnd') OR (jsonb_typeof(((v->'committed')->'periodEnd')) = 'string' AND platform_private.json_datetime((((v->'committed')->'periodEnd') #>> '{}')))))) AND (NOT (v ? 'decisionRef') OR (jsonb_typeof((v->'decisionRef')) = 'string' AND length(((v->'decisionRef') #>> '{}')) >= 1))),false);
$wa$;

CREATE FUNCTION platform_private.json_evidence_trackusagecounter(v jsonb) RETURNS boolean
LANGUAGE sql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
SELECT COALESCE((jsonb_typeof(v) = 'object' AND v ?& ARRAY['schema','owner','model','primaryKey','committed','decisionRef']::text[] AND (v - ARRAY['schema','owner','model','primaryKey','prior','committed','decisionRef']::text[]) = '{}'::jsonb AND (NOT (v ? 'schema') OR ((v->'schema') = '"database-owner-evidence.v1"'::jsonb)) AND (NOT (v ? 'owner') OR ((v->'owner') = '"track_subscription_entitlement"'::jsonb)) AND (NOT (v ? 'model') OR ((v->'model') = '"TrackUsageCounter"'::jsonb)) AND (NOT (v ? 'primaryKey') OR (jsonb_typeof((v->'primaryKey')) = 'object' AND (v->'primaryKey') ?& ARRAY['id']::text[] AND ((v->'primaryKey') - ARRAY['id']::text[]) = '{}'::jsonb AND (NOT ((v->'primaryKey') ? 'id') OR (jsonb_typeof(((v->'primaryKey')->'id')) = 'string' AND (((v->'primaryKey')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')))) AND (NOT (v ? 'prior') OR ((v->'prior') = 'null'::jsonb OR (jsonb_typeof((v->'prior')) = 'object' AND (v->'prior') ?& ARRAY['id','userId','track','period','periodStart','periodEnd','usedQuantity','limitQuantity','revision','sourceRevision']::text[] AND ((v->'prior') - ARRAY['id','userId','track','period','periodStart','periodEnd','usedQuantity','limitQuantity','revision','sourceRevision']::text[]) = '{}'::jsonb AND (NOT ((v->'prior') ? 'id') OR (jsonb_typeof(((v->'prior')->'id')) = 'string' AND (((v->'prior')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'userId') OR (jsonb_typeof(((v->'prior')->'userId')) = 'string' AND (((v->'prior')->'userId') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'track') OR (((v->'prior')->'track') = '"customer"'::jsonb OR ((v->'prior')->'track') = '"candidate"'::jsonb OR ((v->'prior')->'track') = '"professional"'::jsonb)) AND (NOT ((v->'prior') ? 'period') OR (((v->'prior')->'period') = '"once"'::jsonb OR ((v->'prior')->'period') = '"daily"'::jsonb OR ((v->'prior')->'period') = '"monthly"'::jsonb OR ((v->'prior')->'period') = '"yearly"'::jsonb OR ((v->'prior')->'period') = '"lifetime"'::jsonb OR ((v->'prior')->'period') = '"rolling_30_day"'::jsonb)) AND (NOT ((v->'prior') ? 'periodStart') OR (jsonb_typeof(((v->'prior')->'periodStart')) = 'string' AND platform_private.json_datetime((((v->'prior')->'periodStart') #>> '{}')))) AND (NOT ((v->'prior') ? 'periodEnd') OR (jsonb_typeof(((v->'prior')->'periodEnd')) = 'string' AND platform_private.json_datetime((((v->'prior')->'periodEnd') #>> '{}')))) AND (NOT ((v->'prior') ? 'usedQuantity') OR (jsonb_typeof(((v->'prior')->'usedQuantity')) = 'number' AND (((v->'prior')->'usedQuantity') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'prior') ? 'limitQuantity') OR ((jsonb_typeof(((v->'prior')->'limitQuantity')) = 'number' AND (((v->'prior')->'limitQuantity') #>> '{}') ~ '^-?[0-9]+$') OR (jsonb_typeof(((v->'prior')->'limitQuantity')) = 'null'))) AND (NOT ((v->'prior') ? 'revision') OR (jsonb_typeof(((v->'prior')->'revision')) = 'string' AND (((v->'prior')->'revision') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'prior') ? 'sourceRevision') OR (jsonb_typeof(((v->'prior')->'sourceRevision')) = 'string' AND (((v->'prior')->'sourceRevision') #>> '{}') ~ '^-?[0-9]+$'))))) AND (NOT (v ? 'committed') OR (jsonb_typeof((v->'committed')) = 'object' AND (v->'committed') ?& ARRAY['id','userId','track','period','periodStart','periodEnd','usedQuantity','limitQuantity','revision','sourceRevision']::text[] AND ((v->'committed') - ARRAY['id','userId','track','period','periodStart','periodEnd','usedQuantity','limitQuantity','revision','sourceRevision']::text[]) = '{}'::jsonb AND (NOT ((v->'committed') ? 'id') OR (jsonb_typeof(((v->'committed')->'id')) = 'string' AND (((v->'committed')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'userId') OR (jsonb_typeof(((v->'committed')->'userId')) = 'string' AND (((v->'committed')->'userId') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'track') OR (((v->'committed')->'track') = '"customer"'::jsonb OR ((v->'committed')->'track') = '"candidate"'::jsonb OR ((v->'committed')->'track') = '"professional"'::jsonb)) AND (NOT ((v->'committed') ? 'period') OR (((v->'committed')->'period') = '"once"'::jsonb OR ((v->'committed')->'period') = '"daily"'::jsonb OR ((v->'committed')->'period') = '"monthly"'::jsonb OR ((v->'committed')->'period') = '"yearly"'::jsonb OR ((v->'committed')->'period') = '"lifetime"'::jsonb OR ((v->'committed')->'period') = '"rolling_30_day"'::jsonb)) AND (NOT ((v->'committed') ? 'periodStart') OR (jsonb_typeof(((v->'committed')->'periodStart')) = 'string' AND platform_private.json_datetime((((v->'committed')->'periodStart') #>> '{}')))) AND (NOT ((v->'committed') ? 'periodEnd') OR (jsonb_typeof(((v->'committed')->'periodEnd')) = 'string' AND platform_private.json_datetime((((v->'committed')->'periodEnd') #>> '{}')))) AND (NOT ((v->'committed') ? 'usedQuantity') OR (jsonb_typeof(((v->'committed')->'usedQuantity')) = 'number' AND (((v->'committed')->'usedQuantity') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'committed') ? 'limitQuantity') OR ((jsonb_typeof(((v->'committed')->'limitQuantity')) = 'number' AND (((v->'committed')->'limitQuantity') #>> '{}') ~ '^-?[0-9]+$') OR (jsonb_typeof(((v->'committed')->'limitQuantity')) = 'null'))) AND (NOT ((v->'committed') ? 'revision') OR (jsonb_typeof(((v->'committed')->'revision')) = 'string' AND (((v->'committed')->'revision') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'committed') ? 'sourceRevision') OR (jsonb_typeof(((v->'committed')->'sourceRevision')) = 'string' AND (((v->'committed')->'sourceRevision') #>> '{}') ~ '^-?[0-9]+$')))) AND (NOT (v ? 'decisionRef') OR (jsonb_typeof((v->'decisionRef')) = 'string' AND length(((v->'decisionRef') #>> '{}')) >= 1))),false);
$wa$;

CREATE FUNCTION platform_private.json_evidence_tracksubscriptionevent(v jsonb) RETURNS boolean
LANGUAGE sql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
SELECT COALESCE((jsonb_typeof(v) = 'object' AND v ?& ARRAY['schema','owner','model','primaryKey','committed','decisionRef']::text[] AND (v - ARRAY['schema','owner','model','primaryKey','prior','committed','decisionRef']::text[]) = '{}'::jsonb AND (NOT (v ? 'schema') OR ((v->'schema') = '"database-owner-evidence.v1"'::jsonb)) AND (NOT (v ? 'owner') OR ((v->'owner') = '"track_subscription_entitlement"'::jsonb)) AND (NOT (v ? 'model') OR ((v->'model') = '"TrackSubscriptionEvent"'::jsonb)) AND (NOT (v ? 'primaryKey') OR (jsonb_typeof((v->'primaryKey')) = 'object' AND (v->'primaryKey') ?& ARRAY['id']::text[] AND ((v->'primaryKey') - ARRAY['id']::text[]) = '{}'::jsonb AND (NOT ((v->'primaryKey') ? 'id') OR (jsonb_typeof(((v->'primaryKey')->'id')) = 'string' AND (((v->'primaryKey')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')))) AND (NOT (v ? 'prior') OR ((v->'prior') = 'null'::jsonb OR (jsonb_typeof((v->'prior')) = 'object' AND (v->'prior') ?& ARRAY['id','userId','fromStatus','toStatus','provider']::text[] AND ((v->'prior') - ARRAY['id','userId','fromStatus','toStatus','provider']::text[]) = '{}'::jsonb AND (NOT ((v->'prior') ? 'id') OR (jsonb_typeof(((v->'prior')->'id')) = 'string' AND (((v->'prior')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'userId') OR (jsonb_typeof(((v->'prior')->'userId')) = 'string' AND (((v->'prior')->'userId') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'fromStatus') OR ((((v->'prior')->'fromStatus') = '"active"'::jsonb OR ((v->'prior')->'fromStatus') = '"trialing"'::jsonb OR ((v->'prior')->'fromStatus') = '"past_due"'::jsonb OR ((v->'prior')->'fromStatus') = '"cancelled"'::jsonb OR ((v->'prior')->'fromStatus') = '"expired"'::jsonb OR ((v->'prior')->'fromStatus') = '"paused"'::jsonb OR ((v->'prior')->'fromStatus') = '"incomplete"'::jsonb OR ((v->'prior')->'fromStatus') = '"incomplete_expired"'::jsonb) OR (jsonb_typeof(((v->'prior')->'fromStatus')) = 'null'))) AND (NOT ((v->'prior') ? 'toStatus') OR ((((v->'prior')->'toStatus') = '"active"'::jsonb OR ((v->'prior')->'toStatus') = '"trialing"'::jsonb OR ((v->'prior')->'toStatus') = '"past_due"'::jsonb OR ((v->'prior')->'toStatus') = '"cancelled"'::jsonb OR ((v->'prior')->'toStatus') = '"expired"'::jsonb OR ((v->'prior')->'toStatus') = '"paused"'::jsonb OR ((v->'prior')->'toStatus') = '"incomplete"'::jsonb OR ((v->'prior')->'toStatus') = '"incomplete_expired"'::jsonb) OR (jsonb_typeof(((v->'prior')->'toStatus')) = 'null'))) AND (NOT ((v->'prior') ? 'provider') OR ((((v->'prior')->'provider') = '"none"'::jsonb OR ((v->'prior')->'provider') = '"stripe"'::jsonb OR ((v->'prior')->'provider') = '"manual"'::jsonb OR ((v->'prior')->'provider') = '"comped"'::jsonb OR ((v->'prior')->'provider') = '"other"'::jsonb) OR (jsonb_typeof(((v->'prior')->'provider')) = 'null')))))) AND (NOT (v ? 'committed') OR (jsonb_typeof((v->'committed')) = 'object' AND (v->'committed') ?& ARRAY['id','userId','fromStatus','toStatus','provider']::text[] AND ((v->'committed') - ARRAY['id','userId','fromStatus','toStatus','provider']::text[]) = '{}'::jsonb AND (NOT ((v->'committed') ? 'id') OR (jsonb_typeof(((v->'committed')->'id')) = 'string' AND (((v->'committed')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'userId') OR (jsonb_typeof(((v->'committed')->'userId')) = 'string' AND (((v->'committed')->'userId') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'fromStatus') OR ((((v->'committed')->'fromStatus') = '"active"'::jsonb OR ((v->'committed')->'fromStatus') = '"trialing"'::jsonb OR ((v->'committed')->'fromStatus') = '"past_due"'::jsonb OR ((v->'committed')->'fromStatus') = '"cancelled"'::jsonb OR ((v->'committed')->'fromStatus') = '"expired"'::jsonb OR ((v->'committed')->'fromStatus') = '"paused"'::jsonb OR ((v->'committed')->'fromStatus') = '"incomplete"'::jsonb OR ((v->'committed')->'fromStatus') = '"incomplete_expired"'::jsonb) OR (jsonb_typeof(((v->'committed')->'fromStatus')) = 'null'))) AND (NOT ((v->'committed') ? 'toStatus') OR ((((v->'committed')->'toStatus') = '"active"'::jsonb OR ((v->'committed')->'toStatus') = '"trialing"'::jsonb OR ((v->'committed')->'toStatus') = '"past_due"'::jsonb OR ((v->'committed')->'toStatus') = '"cancelled"'::jsonb OR ((v->'committed')->'toStatus') = '"expired"'::jsonb OR ((v->'committed')->'toStatus') = '"paused"'::jsonb OR ((v->'committed')->'toStatus') = '"incomplete"'::jsonb OR ((v->'committed')->'toStatus') = '"incomplete_expired"'::jsonb) OR (jsonb_typeof(((v->'committed')->'toStatus')) = 'null'))) AND (NOT ((v->'committed') ? 'provider') OR ((((v->'committed')->'provider') = '"none"'::jsonb OR ((v->'committed')->'provider') = '"stripe"'::jsonb OR ((v->'committed')->'provider') = '"manual"'::jsonb OR ((v->'committed')->'provider') = '"comped"'::jsonb OR ((v->'committed')->'provider') = '"other"'::jsonb) OR (jsonb_typeof(((v->'committed')->'provider')) = 'null'))))) AND (NOT (v ? 'decisionRef') OR (jsonb_typeof((v->'decisionRef')) = 'string' AND length(((v->'decisionRef') #>> '{}')) >= 1))),false);
$wa$;

CREATE FUNCTION platform_private.json_evidence_consentcontentrevision(v jsonb) RETURNS boolean
LANGUAGE sql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
SELECT COALESCE((jsonb_typeof(v) = 'object' AND v ?& ARRAY['schema','owner','model','primaryKey','committed','decisionRef']::text[] AND (v - ARRAY['schema','owner','model','primaryKey','prior','committed','decisionRef']::text[]) = '{}'::jsonb AND (NOT (v ? 'schema') OR ((v->'schema') = '"database-owner-evidence.v1"'::jsonb)) AND (NOT (v ? 'owner') OR ((v->'owner') = '"consent_disclosure"'::jsonb)) AND (NOT (v ? 'model') OR ((v->'model') = '"ConsentContentRevision"'::jsonb)) AND (NOT (v ? 'primaryKey') OR (jsonb_typeof((v->'primaryKey')) = 'object' AND (v->'primaryKey') ?& ARRAY['id']::text[] AND ((v->'primaryKey') - ARRAY['id']::text[]) = '{}'::jsonb AND (NOT ((v->'primaryKey') ? 'id') OR (jsonb_typeof(((v->'primaryKey')->'id')) = 'string' AND (((v->'primaryKey')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')))) AND (NOT (v ? 'prior') OR ((v->'prior') = 'null'::jsonb OR (jsonb_typeof((v->'prior')) = 'object' AND (v->'prior') ?& ARRAY['id','type','contentHash','reviewState']::text[] AND ((v->'prior') - ARRAY['id','type','contentHash','reviewState']::text[]) = '{}'::jsonb AND (NOT ((v->'prior') ? 'id') OR (jsonb_typeof(((v->'prior')->'id')) = 'string' AND (((v->'prior')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'type') OR (((v->'prior')->'type') = '"terms"'::jsonb OR ((v->'prior')->'type') = '"privacy_policy"'::jsonb OR ((v->'prior')->'type') = '"cookies"'::jsonb OR ((v->'prior')->'type') = '"marketing"'::jsonb OR ((v->'prior')->'type') = '"age_gate"'::jsonb OR ((v->'prior')->'type') = '"calendar_sync"'::jsonb OR ((v->'prior')->'type') = '"sweepstakes_rules"'::jsonb OR ((v->'prior')->'type') = '"gamification_terms"'::jsonb OR ((v->'prior')->'type') = '"reward_redemption_terms"'::jsonb OR ((v->'prior')->'type') = '"healthcare_baa"'::jsonb OR ((v->'prior')->'type') = '"fcra_background_check"'::jsonb OR ((v->'prior')->'type') = '"license_verification"'::jsonb OR ((v->'prior')->'type') = '"dmv_check"'::jsonb OR ((v->'prior')->'type') = '"passkey_login"'::jsonb OR ((v->'prior')->'type') = '"sms_mfa"'::jsonb OR ((v->'prior')->'type') = '"sensitive_financial_access"'::jsonb OR ((v->'prior')->'type') = '"account_recovery_identity_verification"'::jsonb OR ((v->'prior')->'type') = '"phone_number_update"'::jsonb OR ((v->'prior')->'type') = '"digital_goods_terms"'::jsonb OR ((v->'prior')->'type') = '"digital_goods_refund_policy"'::jsonb OR ((v->'prior')->'type') = '"digital_goods_license"'::jsonb OR ((v->'prior')->'type') = '"child_directed_content_declaration"'::jsonb OR ((v->'prior')->'type') = '"course_accessibility_disclosure"'::jsonb OR ((v->'prior')->'type') = '"electronic_records_consent"'::jsonb OR ((v->'prior')->'type') = '"electronic_signature_consent"'::jsonb OR ((v->'prior')->'type') = '"agreement_execution_consent"'::jsonb OR ((v->'prior')->'type') = '"manual_signature_opt_out"'::jsonb OR ((v->'prior')->'type') = '"calendar_free_busy_access"'::jsonb OR ((v->'prior')->'type') = '"calendar_writeback_access"'::jsonb OR ((v->'prior')->'type') = '"calendar_disconnect_notice"'::jsonb OR ((v->'prior')->'type') = '"web_push_notifications"'::jsonb OR ((v->'prior')->'type') = '"pwa_install_guidance"'::jsonb OR ((v->'prior')->'type') = '"subscription_terms"'::jsonb OR ((v->'prior')->'type') = '"recurring_billing_authorization"'::jsonb OR ((v->'prior')->'type') = '"plan_change_terms"'::jsonb OR ((v->'prior')->'type') = '"commission_terms"'::jsonb OR ((v->'prior')->'type') = '"buyer_fee_waiver_terms"'::jsonb)) AND (NOT ((v->'prior') ? 'contentHash') OR (jsonb_typeof(((v->'prior')->'contentHash')) = 'string')) AND (NOT ((v->'prior') ? 'reviewState') OR (((v->'prior')->'reviewState') = '"draft"'::jsonb OR ((v->'prior')->'reviewState') = '"test_only"'::jsonb OR ((v->'prior')->'reviewState') = '"legal_approved"'::jsonb))))) AND (NOT (v ? 'committed') OR (jsonb_typeof((v->'committed')) = 'object' AND (v->'committed') ?& ARRAY['id','type','contentHash','reviewState']::text[] AND ((v->'committed') - ARRAY['id','type','contentHash','reviewState']::text[]) = '{}'::jsonb AND (NOT ((v->'committed') ? 'id') OR (jsonb_typeof(((v->'committed')->'id')) = 'string' AND (((v->'committed')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'type') OR (((v->'committed')->'type') = '"terms"'::jsonb OR ((v->'committed')->'type') = '"privacy_policy"'::jsonb OR ((v->'committed')->'type') = '"cookies"'::jsonb OR ((v->'committed')->'type') = '"marketing"'::jsonb OR ((v->'committed')->'type') = '"age_gate"'::jsonb OR ((v->'committed')->'type') = '"calendar_sync"'::jsonb OR ((v->'committed')->'type') = '"sweepstakes_rules"'::jsonb OR ((v->'committed')->'type') = '"gamification_terms"'::jsonb OR ((v->'committed')->'type') = '"reward_redemption_terms"'::jsonb OR ((v->'committed')->'type') = '"healthcare_baa"'::jsonb OR ((v->'committed')->'type') = '"fcra_background_check"'::jsonb OR ((v->'committed')->'type') = '"license_verification"'::jsonb OR ((v->'committed')->'type') = '"dmv_check"'::jsonb OR ((v->'committed')->'type') = '"passkey_login"'::jsonb OR ((v->'committed')->'type') = '"sms_mfa"'::jsonb OR ((v->'committed')->'type') = '"sensitive_financial_access"'::jsonb OR ((v->'committed')->'type') = '"account_recovery_identity_verification"'::jsonb OR ((v->'committed')->'type') = '"phone_number_update"'::jsonb OR ((v->'committed')->'type') = '"digital_goods_terms"'::jsonb OR ((v->'committed')->'type') = '"digital_goods_refund_policy"'::jsonb OR ((v->'committed')->'type') = '"digital_goods_license"'::jsonb OR ((v->'committed')->'type') = '"child_directed_content_declaration"'::jsonb OR ((v->'committed')->'type') = '"course_accessibility_disclosure"'::jsonb OR ((v->'committed')->'type') = '"electronic_records_consent"'::jsonb OR ((v->'committed')->'type') = '"electronic_signature_consent"'::jsonb OR ((v->'committed')->'type') = '"agreement_execution_consent"'::jsonb OR ((v->'committed')->'type') = '"manual_signature_opt_out"'::jsonb OR ((v->'committed')->'type') = '"calendar_free_busy_access"'::jsonb OR ((v->'committed')->'type') = '"calendar_writeback_access"'::jsonb OR ((v->'committed')->'type') = '"calendar_disconnect_notice"'::jsonb OR ((v->'committed')->'type') = '"web_push_notifications"'::jsonb OR ((v->'committed')->'type') = '"pwa_install_guidance"'::jsonb OR ((v->'committed')->'type') = '"subscription_terms"'::jsonb OR ((v->'committed')->'type') = '"recurring_billing_authorization"'::jsonb OR ((v->'committed')->'type') = '"plan_change_terms"'::jsonb OR ((v->'committed')->'type') = '"commission_terms"'::jsonb OR ((v->'committed')->'type') = '"buyer_fee_waiver_terms"'::jsonb)) AND (NOT ((v->'committed') ? 'contentHash') OR (jsonb_typeof(((v->'committed')->'contentHash')) = 'string')) AND (NOT ((v->'committed') ? 'reviewState') OR (((v->'committed')->'reviewState') = '"draft"'::jsonb OR ((v->'committed')->'reviewState') = '"test_only"'::jsonb OR ((v->'committed')->'reviewState') = '"legal_approved"'::jsonb)))) AND (NOT (v ? 'decisionRef') OR (jsonb_typeof((v->'decisionRef')) = 'string' AND length(((v->'decisionRef') #>> '{}')) >= 1))),false);
$wa$;

CREATE FUNCTION platform_private.json_evidence_consentpresentation(v jsonb) RETURNS boolean
LANGUAGE sql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
SELECT COALESCE((jsonb_typeof(v) = 'object' AND v ?& ARRAY['schema','owner','model','primaryKey','committed','decisionRef']::text[] AND (v - ARRAY['schema','owner','model','primaryKey','prior','committed','decisionRef']::text[]) = '{}'::jsonb AND (NOT (v ? 'schema') OR ((v->'schema') = '"database-owner-evidence.v1"'::jsonb)) AND (NOT (v ? 'owner') OR ((v->'owner') = '"consent_disclosure"'::jsonb)) AND (NOT (v ? 'model') OR ((v->'model') = '"ConsentPresentation"'::jsonb)) AND (NOT (v ? 'primaryKey') OR (jsonb_typeof((v->'primaryKey')) = 'object' AND (v->'primaryKey') ?& ARRAY['id']::text[] AND ((v->'primaryKey') - ARRAY['id']::text[]) = '{}'::jsonb AND (NOT ((v->'primaryKey') ? 'id') OR (jsonb_typeof(((v->'primaryKey')->'id')) = 'string' AND (((v->'primaryKey')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')))) AND (NOT (v ? 'prior') OR ((v->'prior') = 'null'::jsonb OR (jsonb_typeof((v->'prior')) = 'object' AND (v->'prior') ?& ARRAY['id','userId','renderedHash']::text[] AND ((v->'prior') - ARRAY['id','userId','renderedHash']::text[]) = '{}'::jsonb AND (NOT ((v->'prior') ? 'id') OR (jsonb_typeof(((v->'prior')->'id')) = 'string' AND (((v->'prior')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'userId') OR (jsonb_typeof(((v->'prior')->'userId')) = 'string' AND (((v->'prior')->'userId') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'renderedHash') OR (jsonb_typeof(((v->'prior')->'renderedHash')) = 'string'))))) AND (NOT (v ? 'committed') OR (jsonb_typeof((v->'committed')) = 'object' AND (v->'committed') ?& ARRAY['id','userId','renderedHash']::text[] AND ((v->'committed') - ARRAY['id','userId','renderedHash']::text[]) = '{}'::jsonb AND (NOT ((v->'committed') ? 'id') OR (jsonb_typeof(((v->'committed')->'id')) = 'string' AND (((v->'committed')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'userId') OR (jsonb_typeof(((v->'committed')->'userId')) = 'string' AND (((v->'committed')->'userId') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'renderedHash') OR (jsonb_typeof(((v->'committed')->'renderedHash')) = 'string')))) AND (NOT (v ? 'decisionRef') OR (jsonb_typeof((v->'decisionRef')) = 'string' AND length(((v->'decisionRef') #>> '{}')) >= 1))),false);
$wa$;

CREATE FUNCTION platform_private.json_evidence_consentdisposition(v jsonb) RETURNS boolean
LANGUAGE sql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
SELECT COALESCE((jsonb_typeof(v) = 'object' AND v ?& ARRAY['schema','owner','model','primaryKey','committed','decisionRef']::text[] AND (v - ARRAY['schema','owner','model','primaryKey','prior','committed','decisionRef']::text[]) = '{}'::jsonb AND (NOT (v ? 'schema') OR ((v->'schema') = '"database-owner-evidence.v1"'::jsonb)) AND (NOT (v ? 'owner') OR ((v->'owner') = '"consent_disclosure"'::jsonb)) AND (NOT (v ? 'model') OR ((v->'model') = '"ConsentDisposition"'::jsonb)) AND (NOT (v ? 'primaryKey') OR (jsonb_typeof((v->'primaryKey')) = 'object' AND (v->'primaryKey') ?& ARRAY['id']::text[] AND ((v->'primaryKey') - ARRAY['id']::text[]) = '{}'::jsonb AND (NOT ((v->'primaryKey') ? 'id') OR (jsonb_typeof(((v->'primaryKey')->'id')) = 'string' AND (((v->'primaryKey')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')))) AND (NOT (v ? 'prior') OR ((v->'prior') = 'null'::jsonb OR (jsonb_typeof((v->'prior')) = 'object' AND (v->'prior') ?& ARRAY['id','userId','kind']::text[] AND ((v->'prior') - ARRAY['id','userId','kind']::text[]) = '{}'::jsonb AND (NOT ((v->'prior') ? 'id') OR (jsonb_typeof(((v->'prior')->'id')) = 'string' AND (((v->'prior')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'userId') OR (jsonb_typeof(((v->'prior')->'userId')) = 'string' AND (((v->'prior')->'userId') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'kind') OR (((v->'prior')->'kind') = '"declined"'::jsonb OR ((v->'prior')->'kind') = '"withdrawn"'::jsonb OR ((v->'prior')->'kind') = '"superseded"'::jsonb))))) AND (NOT (v ? 'committed') OR (jsonb_typeof((v->'committed')) = 'object' AND (v->'committed') ?& ARRAY['id','userId','kind']::text[] AND ((v->'committed') - ARRAY['id','userId','kind']::text[]) = '{}'::jsonb AND (NOT ((v->'committed') ? 'id') OR (jsonb_typeof(((v->'committed')->'id')) = 'string' AND (((v->'committed')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'userId') OR (jsonb_typeof(((v->'committed')->'userId')) = 'string' AND (((v->'committed')->'userId') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'kind') OR (((v->'committed')->'kind') = '"declined"'::jsonb OR ((v->'committed')->'kind') = '"withdrawn"'::jsonb OR ((v->'committed')->'kind') = '"superseded"'::jsonb)))) AND (NOT (v ? 'decisionRef') OR (jsonb_typeof((v->'decisionRef')) = 'string' AND length(((v->'decisionRef') #>> '{}')) >= 1))),false);
$wa$;

CREATE FUNCTION platform_private.json_evidence_databaseactiongrant(v jsonb) RETURNS boolean
LANGUAGE sql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
SELECT COALESCE((jsonb_typeof(v) = 'object' AND v ?& ARRAY['schema','owner','model','primaryKey','committed','decisionRef']::text[] AND (v - ARRAY['schema','owner','model','primaryKey','prior','committed','decisionRef']::text[]) = '{}'::jsonb AND (NOT (v ? 'schema') OR ((v->'schema') = '"database-owner-evidence.v1"'::jsonb)) AND (NOT (v ? 'owner') OR ((v->'owner') = '"platform_integration_owner"'::jsonb)) AND (NOT (v ? 'model') OR ((v->'model') = '"DatabaseActionGrant"'::jsonb)) AND (NOT (v ? 'primaryKey') OR (jsonb_typeof((v->'primaryKey')) = 'object' AND (v->'primaryKey') ?& ARRAY['id']::text[] AND ((v->'primaryKey') - ARRAY['id']::text[]) = '{}'::jsonb AND (NOT ((v->'primaryKey') ? 'id') OR (jsonb_typeof(((v->'primaryKey')->'id')) = 'string' AND (((v->'primaryKey')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')))) AND (NOT (v ? 'prior') OR ((v->'prior') = 'null'::jsonb OR (jsonb_typeof((v->'prior')) = 'object' AND (v->'prior') ?& ARRAY['id','tokenHash','securityGeneration','sourceGeneration']::text[] AND ((v->'prior') - ARRAY['id','tokenHash','securityGeneration','sourceGeneration']::text[]) = '{}'::jsonb AND (NOT ((v->'prior') ? 'id') OR (jsonb_typeof(((v->'prior')->'id')) = 'string' AND (((v->'prior')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'tokenHash') OR (jsonb_typeof(((v->'prior')->'tokenHash')) = 'string')) AND (NOT ((v->'prior') ? 'securityGeneration') OR (jsonb_typeof(((v->'prior')->'securityGeneration')) = 'string' AND (((v->'prior')->'securityGeneration') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'prior') ? 'sourceGeneration') OR (jsonb_typeof(((v->'prior')->'sourceGeneration')) = 'string' AND (((v->'prior')->'sourceGeneration') #>> '{}') ~ '^-?[0-9]+$'))))) AND (NOT (v ? 'committed') OR (jsonb_typeof((v->'committed')) = 'object' AND (v->'committed') ?& ARRAY['id','tokenHash','securityGeneration','sourceGeneration']::text[] AND ((v->'committed') - ARRAY['id','tokenHash','securityGeneration','sourceGeneration']::text[]) = '{}'::jsonb AND (NOT ((v->'committed') ? 'id') OR (jsonb_typeof(((v->'committed')->'id')) = 'string' AND (((v->'committed')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'tokenHash') OR (jsonb_typeof(((v->'committed')->'tokenHash')) = 'string')) AND (NOT ((v->'committed') ? 'securityGeneration') OR (jsonb_typeof(((v->'committed')->'securityGeneration')) = 'string' AND (((v->'committed')->'securityGeneration') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'committed') ? 'sourceGeneration') OR (jsonb_typeof(((v->'committed')->'sourceGeneration')) = 'string' AND (((v->'committed')->'sourceGeneration') #>> '{}') ~ '^-?[0-9]+$')))) AND (NOT (v ? 'decisionRef') OR (jsonb_typeof((v->'decisionRef')) = 'string' AND length(((v->'decisionRef') #>> '{}')) >= 1))),false);
$wa$;

CREATE FUNCTION platform_private.json_evidence_runtimecommandreceipt(v jsonb) RETURNS boolean
LANGUAGE sql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
SELECT COALESCE((jsonb_typeof(v) = 'object' AND v ?& ARRAY['schema','owner','model','primaryKey','committed','decisionRef']::text[] AND (v - ARRAY['schema','owner','model','primaryKey','prior','committed','decisionRef']::text[]) = '{}'::jsonb AND (NOT (v ? 'schema') OR ((v->'schema') = '"database-owner-evidence.v1"'::jsonb)) AND (NOT (v ? 'owner') OR ((v->'owner') = '"platform_integration_owner"'::jsonb)) AND (NOT (v ? 'model') OR ((v->'model') = '"RuntimeCommandReceipt"'::jsonb)) AND (NOT (v ? 'primaryKey') OR (jsonb_typeof((v->'primaryKey')) = 'object' AND (v->'primaryKey') ?& ARRAY['id']::text[] AND ((v->'primaryKey') - ARRAY['id']::text[]) = '{}'::jsonb AND (NOT ((v->'primaryKey') ? 'id') OR (jsonb_typeof(((v->'primaryKey')->'id')) = 'string' AND (((v->'primaryKey')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')))) AND (NOT (v ? 'prior') OR ((v->'prior') = 'null'::jsonb OR (jsonb_typeof((v->'prior')) = 'object' AND (v->'prior') ?& ARRAY['id','state','sourceRevision','resultDigest']::text[] AND ((v->'prior') - ARRAY['id','state','sourceRevision','resultDigest']::text[]) = '{}'::jsonb AND (NOT ((v->'prior') ? 'id') OR (jsonb_typeof(((v->'prior')->'id')) = 'string' AND (((v->'prior')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'state') OR (((v->'prior')->'state') = '"pending"'::jsonb OR ((v->'prior')->'state') = '"committed"'::jsonb OR ((v->'prior')->'state') = '"denied"'::jsonb OR ((v->'prior')->'state') = '"unknown"'::jsonb OR ((v->'prior')->'state') = '"fenced_noncommit"'::jsonb)) AND (NOT ((v->'prior') ? 'sourceRevision') OR ((jsonb_typeof(((v->'prior')->'sourceRevision')) = 'string' AND (((v->'prior')->'sourceRevision') #>> '{}') ~ '^-?[0-9]+$') OR (jsonb_typeof(((v->'prior')->'sourceRevision')) = 'null'))) AND (NOT ((v->'prior') ? 'resultDigest') OR ((jsonb_typeof(((v->'prior')->'resultDigest')) = 'string') OR (jsonb_typeof(((v->'prior')->'resultDigest')) = 'null')))))) AND (NOT (v ? 'committed') OR (jsonb_typeof((v->'committed')) = 'object' AND (v->'committed') ?& ARRAY['id','state','sourceRevision','resultDigest']::text[] AND ((v->'committed') - ARRAY['id','state','sourceRevision','resultDigest']::text[]) = '{}'::jsonb AND (NOT ((v->'committed') ? 'id') OR (jsonb_typeof(((v->'committed')->'id')) = 'string' AND (((v->'committed')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'state') OR (((v->'committed')->'state') = '"pending"'::jsonb OR ((v->'committed')->'state') = '"committed"'::jsonb OR ((v->'committed')->'state') = '"denied"'::jsonb OR ((v->'committed')->'state') = '"unknown"'::jsonb OR ((v->'committed')->'state') = '"fenced_noncommit"'::jsonb)) AND (NOT ((v->'committed') ? 'sourceRevision') OR ((jsonb_typeof(((v->'committed')->'sourceRevision')) = 'string' AND (((v->'committed')->'sourceRevision') #>> '{}') ~ '^-?[0-9]+$') OR (jsonb_typeof(((v->'committed')->'sourceRevision')) = 'null'))) AND (NOT ((v->'committed') ? 'resultDigest') OR ((jsonb_typeof(((v->'committed')->'resultDigest')) = 'string') OR (jsonb_typeof(((v->'committed')->'resultDigest')) = 'null'))))) AND (NOT (v ? 'decisionRef') OR (jsonb_typeof((v->'decisionRef')) = 'string' AND length(((v->'decisionRef') #>> '{}')) >= 1))),false);
$wa$;

CREATE FUNCTION platform_private.json_evidence_runtimeoutboxmessage(v jsonb) RETURNS boolean
LANGUAGE sql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
SELECT COALESCE((jsonb_typeof(v) = 'object' AND v ?& ARRAY['schema','owner','model','primaryKey','committed','decisionRef']::text[] AND (v - ARRAY['schema','owner','model','primaryKey','prior','committed','decisionRef']::text[]) = '{}'::jsonb AND (NOT (v ? 'schema') OR ((v->'schema') = '"database-owner-evidence.v1"'::jsonb)) AND (NOT (v ? 'owner') OR ((v->'owner') = '"platform_integration_owner"'::jsonb)) AND (NOT (v ? 'model') OR ((v->'model') = '"RuntimeOutboxMessage"'::jsonb)) AND (NOT (v ? 'primaryKey') OR (jsonb_typeof((v->'primaryKey')) = 'object' AND (v->'primaryKey') ?& ARRAY['id']::text[] AND ((v->'primaryKey') - ARRAY['id']::text[]) = '{}'::jsonb AND (NOT ((v->'primaryKey') ? 'id') OR (jsonb_typeof(((v->'primaryKey')->'id')) = 'string' AND (((v->'primaryKey')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')))) AND (NOT (v ? 'prior') OR ((v->'prior') = 'null'::jsonb OR (jsonb_typeof((v->'prior')) = 'object' AND (v->'prior') ?& ARRAY['id','kind','sourceRevision','sourceGeneration','payloadHash']::text[] AND ((v->'prior') - ARRAY['id','kind','sourceRevision','sourceGeneration','payloadHash']::text[]) = '{}'::jsonb AND (NOT ((v->'prior') ? 'id') OR (jsonb_typeof(((v->'prior')->'id')) = 'string' AND (((v->'prior')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'kind') OR (((v->'prior')->'kind') = '"event"'::jsonb OR ((v->'prior')->'kind') = '"command"'::jsonb)) AND (NOT ((v->'prior') ? 'sourceRevision') OR (jsonb_typeof(((v->'prior')->'sourceRevision')) = 'string' AND (((v->'prior')->'sourceRevision') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'prior') ? 'sourceGeneration') OR (jsonb_typeof(((v->'prior')->'sourceGeneration')) = 'string' AND (((v->'prior')->'sourceGeneration') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'prior') ? 'payloadHash') OR (jsonb_typeof(((v->'prior')->'payloadHash')) = 'string'))))) AND (NOT (v ? 'committed') OR (jsonb_typeof((v->'committed')) = 'object' AND (v->'committed') ?& ARRAY['id','kind','sourceRevision','sourceGeneration','payloadHash']::text[] AND ((v->'committed') - ARRAY['id','kind','sourceRevision','sourceGeneration','payloadHash']::text[]) = '{}'::jsonb AND (NOT ((v->'committed') ? 'id') OR (jsonb_typeof(((v->'committed')->'id')) = 'string' AND (((v->'committed')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'kind') OR (((v->'committed')->'kind') = '"event"'::jsonb OR ((v->'committed')->'kind') = '"command"'::jsonb)) AND (NOT ((v->'committed') ? 'sourceRevision') OR (jsonb_typeof(((v->'committed')->'sourceRevision')) = 'string' AND (((v->'committed')->'sourceRevision') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'committed') ? 'sourceGeneration') OR (jsonb_typeof(((v->'committed')->'sourceGeneration')) = 'string' AND (((v->'committed')->'sourceGeneration') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'committed') ? 'payloadHash') OR (jsonb_typeof(((v->'committed')->'payloadHash')) = 'string')))) AND (NOT (v ? 'decisionRef') OR (jsonb_typeof((v->'decisionRef')) = 'string' AND length(((v->'decisionRef') #>> '{}')) >= 1))),false);
$wa$;

CREATE FUNCTION platform_private.json_evidence_runtimeeffectreceipt(v jsonb) RETURNS boolean
LANGUAGE sql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
SELECT COALESCE((jsonb_typeof(v) = 'object' AND v ?& ARRAY['schema','owner','model','primaryKey','committed','decisionRef']::text[] AND (v - ARRAY['schema','owner','model','primaryKey','prior','committed','decisionRef']::text[]) = '{}'::jsonb AND (NOT (v ? 'schema') OR ((v->'schema') = '"database-owner-evidence.v1"'::jsonb)) AND (NOT (v ? 'owner') OR ((v->'owner') = '"platform_integration_owner"'::jsonb)) AND (NOT (v ? 'model') OR ((v->'model') = '"RuntimeEffectReceipt"'::jsonb)) AND (NOT (v ? 'primaryKey') OR (jsonb_typeof((v->'primaryKey')) = 'object' AND (v->'primaryKey') ?& ARRAY['id']::text[] AND ((v->'primaryKey') - ARRAY['id']::text[]) = '{}'::jsonb AND (NOT ((v->'primaryKey') ? 'id') OR (jsonb_typeof(((v->'primaryKey')->'id')) = 'string' AND (((v->'primaryKey')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')))) AND (NOT (v ? 'prior') OR ((v->'prior') = 'null'::jsonb OR (jsonb_typeof((v->'prior')) = 'object' AND (v->'prior') ?& ARRAY['id','semanticEffectKey','state','sourceRevision','fence','resultHash']::text[] AND ((v->'prior') - ARRAY['id','semanticEffectKey','state','sourceRevision','fence','resultHash']::text[]) = '{}'::jsonb AND (NOT ((v->'prior') ? 'id') OR (jsonb_typeof(((v->'prior')->'id')) = 'string' AND (((v->'prior')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'semanticEffectKey') OR (jsonb_typeof(((v->'prior')->'semanticEffectKey')) = 'string')) AND (NOT ((v->'prior') ? 'state') OR (((v->'prior')->'state') = '"pending"'::jsonb OR ((v->'prior')->'state') = '"committed"'::jsonb OR ((v->'prior')->'state') = '"denied"'::jsonb OR ((v->'prior')->'state') = '"unknown"'::jsonb OR ((v->'prior')->'state') = '"fenced_noncommit"'::jsonb)) AND (NOT ((v->'prior') ? 'sourceRevision') OR ((jsonb_typeof(((v->'prior')->'sourceRevision')) = 'string' AND (((v->'prior')->'sourceRevision') #>> '{}') ~ '^-?[0-9]+$') OR (jsonb_typeof(((v->'prior')->'sourceRevision')) = 'null'))) AND (NOT ((v->'prior') ? 'fence') OR (jsonb_typeof(((v->'prior')->'fence')) = 'string' AND (((v->'prior')->'fence') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'prior') ? 'resultHash') OR ((jsonb_typeof(((v->'prior')->'resultHash')) = 'string') OR (jsonb_typeof(((v->'prior')->'resultHash')) = 'null')))))) AND (NOT (v ? 'committed') OR (jsonb_typeof((v->'committed')) = 'object' AND (v->'committed') ?& ARRAY['id','semanticEffectKey','state','sourceRevision','fence','resultHash']::text[] AND ((v->'committed') - ARRAY['id','semanticEffectKey','state','sourceRevision','fence','resultHash']::text[]) = '{}'::jsonb AND (NOT ((v->'committed') ? 'id') OR (jsonb_typeof(((v->'committed')->'id')) = 'string' AND (((v->'committed')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'semanticEffectKey') OR (jsonb_typeof(((v->'committed')->'semanticEffectKey')) = 'string')) AND (NOT ((v->'committed') ? 'state') OR (((v->'committed')->'state') = '"pending"'::jsonb OR ((v->'committed')->'state') = '"committed"'::jsonb OR ((v->'committed')->'state') = '"denied"'::jsonb OR ((v->'committed')->'state') = '"unknown"'::jsonb OR ((v->'committed')->'state') = '"fenced_noncommit"'::jsonb)) AND (NOT ((v->'committed') ? 'sourceRevision') OR ((jsonb_typeof(((v->'committed')->'sourceRevision')) = 'string' AND (((v->'committed')->'sourceRevision') #>> '{}') ~ '^-?[0-9]+$') OR (jsonb_typeof(((v->'committed')->'sourceRevision')) = 'null'))) AND (NOT ((v->'committed') ? 'fence') OR (jsonb_typeof(((v->'committed')->'fence')) = 'string' AND (((v->'committed')->'fence') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'committed') ? 'resultHash') OR ((jsonb_typeof(((v->'committed')->'resultHash')) = 'string') OR (jsonb_typeof(((v->'committed')->'resultHash')) = 'null'))))) AND (NOT (v ? 'decisionRef') OR (jsonb_typeof((v->'decisionRef')) = 'string' AND length(((v->'decisionRef') #>> '{}')) >= 1))),false);
$wa$;

CREATE FUNCTION platform_private.json_evidence_runtimeworkitem(v jsonb) RETURNS boolean
LANGUAGE sql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
SELECT COALESCE((jsonb_typeof(v) = 'object' AND v ?& ARRAY['schema','owner','model','primaryKey','committed','decisionRef']::text[] AND (v - ARRAY['schema','owner','model','primaryKey','prior','committed','decisionRef']::text[]) = '{}'::jsonb AND (NOT (v ? 'schema') OR ((v->'schema') = '"database-owner-evidence.v1"'::jsonb)) AND (NOT (v ? 'owner') OR ((v->'owner') = '"platform_integration_owner"'::jsonb)) AND (NOT (v ? 'model') OR ((v->'model') = '"RuntimeWorkItem"'::jsonb)) AND (NOT (v ? 'primaryKey') OR (jsonb_typeof((v->'primaryKey')) = 'object' AND (v->'primaryKey') ?& ARRAY['id']::text[] AND ((v->'primaryKey') - ARRAY['id']::text[]) = '{}'::jsonb AND (NOT ((v->'primaryKey') ? 'id') OR (jsonb_typeof(((v->'primaryKey')->'id')) = 'string' AND (((v->'primaryKey')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')))) AND (NOT (v ? 'prior') OR ((v->'prior') = 'null'::jsonb OR (jsonb_typeof((v->'prior')) = 'object' AND (v->'prior') ?& ARRAY['id','state','fence','leaseTokenHash','attemptCount']::text[] AND ((v->'prior') - ARRAY['id','state','fence','leaseTokenHash','attemptCount']::text[]) = '{}'::jsonb AND (NOT ((v->'prior') ? 'id') OR (jsonb_typeof(((v->'prior')->'id')) = 'string' AND (((v->'prior')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'state') OR (((v->'prior')->'state') = '"pending"'::jsonb OR ((v->'prior')->'state') = '"leased"'::jsonb OR ((v->'prior')->'state') = '"completed"'::jsonb OR ((v->'prior')->'state') = '"retry_wait"'::jsonb OR ((v->'prior')->'state') = '"dead_letter"'::jsonb OR ((v->'prior')->'state') = '"unknown"'::jsonb)) AND (NOT ((v->'prior') ? 'fence') OR (jsonb_typeof(((v->'prior')->'fence')) = 'string' AND (((v->'prior')->'fence') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'prior') ? 'leaseTokenHash') OR ((jsonb_typeof(((v->'prior')->'leaseTokenHash')) = 'string') OR (jsonb_typeof(((v->'prior')->'leaseTokenHash')) = 'null'))) AND (NOT ((v->'prior') ? 'attemptCount') OR (jsonb_typeof(((v->'prior')->'attemptCount')) = 'number' AND (((v->'prior')->'attemptCount') #>> '{}') ~ '^-?[0-9]+$'))))) AND (NOT (v ? 'committed') OR (jsonb_typeof((v->'committed')) = 'object' AND (v->'committed') ?& ARRAY['id','state','fence','leaseTokenHash','attemptCount']::text[] AND ((v->'committed') - ARRAY['id','state','fence','leaseTokenHash','attemptCount']::text[]) = '{}'::jsonb AND (NOT ((v->'committed') ? 'id') OR (jsonb_typeof(((v->'committed')->'id')) = 'string' AND (((v->'committed')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'state') OR (((v->'committed')->'state') = '"pending"'::jsonb OR ((v->'committed')->'state') = '"leased"'::jsonb OR ((v->'committed')->'state') = '"completed"'::jsonb OR ((v->'committed')->'state') = '"retry_wait"'::jsonb OR ((v->'committed')->'state') = '"dead_letter"'::jsonb OR ((v->'committed')->'state') = '"unknown"'::jsonb)) AND (NOT ((v->'committed') ? 'fence') OR (jsonb_typeof(((v->'committed')->'fence')) = 'string' AND (((v->'committed')->'fence') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'committed') ? 'leaseTokenHash') OR ((jsonb_typeof(((v->'committed')->'leaseTokenHash')) = 'string') OR (jsonb_typeof(((v->'committed')->'leaseTokenHash')) = 'null'))) AND (NOT ((v->'committed') ? 'attemptCount') OR (jsonb_typeof(((v->'committed')->'attemptCount')) = 'number' AND (((v->'committed')->'attemptCount') #>> '{}') ~ '^-?[0-9]+$')))) AND (NOT (v ? 'decisionRef') OR (jsonb_typeof((v->'decisionRef')) = 'string' AND length(((v->'decisionRef') #>> '{}')) >= 1))),false);
$wa$;

CREATE FUNCTION platform_private.json_evidence_runtimeattempt(v jsonb) RETURNS boolean
LANGUAGE sql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
SELECT COALESCE((jsonb_typeof(v) = 'object' AND v ?& ARRAY['schema','owner','model','primaryKey','committed','decisionRef']::text[] AND (v - ARRAY['schema','owner','model','primaryKey','prior','committed','decisionRef']::text[]) = '{}'::jsonb AND (NOT (v ? 'schema') OR ((v->'schema') = '"database-owner-evidence.v1"'::jsonb)) AND (NOT (v ? 'owner') OR ((v->'owner') = '"platform_integration_owner"'::jsonb)) AND (NOT (v ? 'model') OR ((v->'model') = '"RuntimeAttempt"'::jsonb)) AND (NOT (v ? 'primaryKey') OR (jsonb_typeof((v->'primaryKey')) = 'object' AND (v->'primaryKey') ?& ARRAY['id']::text[] AND ((v->'primaryKey') - ARRAY['id']::text[]) = '{}'::jsonb AND (NOT ((v->'primaryKey') ? 'id') OR (jsonb_typeof(((v->'primaryKey')->'id')) = 'string' AND (((v->'primaryKey')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')))) AND (NOT (v ? 'prior') OR ((v->'prior') = 'null'::jsonb OR (jsonb_typeof((v->'prior')) = 'object' AND (v->'prior') ?& ARRAY['id','fence','result']::text[] AND ((v->'prior') - ARRAY['id','fence','result']::text[]) = '{}'::jsonb AND (NOT ((v->'prior') ? 'id') OR (jsonb_typeof(((v->'prior')->'id')) = 'string' AND (((v->'prior')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'fence') OR (jsonb_typeof(((v->'prior')->'fence')) = 'string' AND (((v->'prior')->'fence') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'prior') ? 'result') OR (((v->'prior')->'result') = '"pending"'::jsonb OR ((v->'prior')->'result') = '"committed"'::jsonb OR ((v->'prior')->'result') = '"denied"'::jsonb OR ((v->'prior')->'result') = '"unknown"'::jsonb OR ((v->'prior')->'result') = '"fenced_noncommit"'::jsonb))))) AND (NOT (v ? 'committed') OR (jsonb_typeof((v->'committed')) = 'object' AND (v->'committed') ?& ARRAY['id','fence','result']::text[] AND ((v->'committed') - ARRAY['id','fence','result']::text[]) = '{}'::jsonb AND (NOT ((v->'committed') ? 'id') OR (jsonb_typeof(((v->'committed')->'id')) = 'string' AND (((v->'committed')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'fence') OR (jsonb_typeof(((v->'committed')->'fence')) = 'string' AND (((v->'committed')->'fence') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'committed') ? 'result') OR (((v->'committed')->'result') = '"pending"'::jsonb OR ((v->'committed')->'result') = '"committed"'::jsonb OR ((v->'committed')->'result') = '"denied"'::jsonb OR ((v->'committed')->'result') = '"unknown"'::jsonb OR ((v->'committed')->'result') = '"fenced_noncommit"'::jsonb)))) AND (NOT (v ? 'decisionRef') OR (jsonb_typeof((v->'decisionRef')) = 'string' AND length(((v->'decisionRef') #>> '{}')) >= 1))),false);
$wa$;

CREATE FUNCTION platform_private.json_evidence_runtimeinboxreceipt(v jsonb) RETURNS boolean
LANGUAGE sql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
SELECT COALESCE((jsonb_typeof(v) = 'object' AND v ?& ARRAY['schema','owner','model','primaryKey','committed','decisionRef']::text[] AND (v - ARRAY['schema','owner','model','primaryKey','prior','committed','decisionRef']::text[]) = '{}'::jsonb AND (NOT (v ? 'schema') OR ((v->'schema') = '"database-owner-evidence.v1"'::jsonb)) AND (NOT (v ? 'owner') OR ((v->'owner') = '"platform_integration_owner"'::jsonb)) AND (NOT (v ? 'model') OR ((v->'model') = '"RuntimeInboxReceipt"'::jsonb)) AND (NOT (v ? 'primaryKey') OR (jsonb_typeof((v->'primaryKey')) = 'object' AND (v->'primaryKey') ?& ARRAY['id']::text[] AND ((v->'primaryKey') - ARRAY['id']::text[]) = '{}'::jsonb AND (NOT ((v->'primaryKey') ? 'id') OR (jsonb_typeof(((v->'primaryKey')->'id')) = 'string' AND (((v->'primaryKey')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')))) AND (NOT (v ? 'prior') OR ((v->'prior') = 'null'::jsonb OR (jsonb_typeof((v->'prior')) = 'object' AND (v->'prior') ?& ARRAY['id','payloadHash']::text[] AND ((v->'prior') - ARRAY['id','payloadHash']::text[]) = '{}'::jsonb AND (NOT ((v->'prior') ? 'id') OR (jsonb_typeof(((v->'prior')->'id')) = 'string' AND (((v->'prior')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'payloadHash') OR (jsonb_typeof(((v->'prior')->'payloadHash')) = 'string'))))) AND (NOT (v ? 'committed') OR (jsonb_typeof((v->'committed')) = 'object' AND (v->'committed') ?& ARRAY['id','payloadHash']::text[] AND ((v->'committed') - ARRAY['id','payloadHash']::text[]) = '{}'::jsonb AND (NOT ((v->'committed') ? 'id') OR (jsonb_typeof(((v->'committed')->'id')) = 'string' AND (((v->'committed')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'payloadHash') OR (jsonb_typeof(((v->'committed')->'payloadHash')) = 'string')))) AND (NOT (v ? 'decisionRef') OR (jsonb_typeof((v->'decisionRef')) = 'string' AND length(((v->'decisionRef') #>> '{}')) >= 1))),false);
$wa$;

CREATE FUNCTION platform_private.json_evidence_runtimereservation(v jsonb) RETURNS boolean
LANGUAGE sql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
SELECT COALESCE((jsonb_typeof(v) = 'object' AND v ?& ARRAY['schema','owner','model','primaryKey','committed','decisionRef']::text[] AND (v - ARRAY['schema','owner','model','primaryKey','prior','committed','decisionRef']::text[]) = '{}'::jsonb AND (NOT (v ? 'schema') OR ((v->'schema') = '"database-owner-evidence.v1"'::jsonb)) AND (NOT (v ? 'owner') OR ((v->'owner') = '"platform_integration_owner"'::jsonb)) AND (NOT (v ? 'model') OR ((v->'model') = '"RuntimeReservation"'::jsonb)) AND (NOT (v ? 'primaryKey') OR (jsonb_typeof((v->'primaryKey')) = 'object' AND (v->'primaryKey') ?& ARRAY['id']::text[] AND ((v->'primaryKey') - ARRAY['id']::text[]) = '{}'::jsonb AND (NOT ((v->'primaryKey') ? 'id') OR (jsonb_typeof(((v->'primaryKey')->'id')) = 'string' AND (((v->'primaryKey')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')))) AND (NOT (v ? 'prior') OR ((v->'prior') = 'null'::jsonb OR (jsonb_typeof((v->'prior')) = 'object' AND (v->'prior') ?& ARRAY['id','state','fence']::text[] AND ((v->'prior') - ARRAY['id','state','fence']::text[]) = '{}'::jsonb AND (NOT ((v->'prior') ? 'id') OR (jsonb_typeof(((v->'prior')->'id')) = 'string' AND (((v->'prior')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'state') OR (((v->'prior')->'state') = '"active"'::jsonb OR ((v->'prior')->'state') = '"committed"'::jsonb OR ((v->'prior')->'state') = '"released"'::jsonb OR ((v->'prior')->'state') = '"unknown"'::jsonb)) AND (NOT ((v->'prior') ? 'fence') OR (jsonb_typeof(((v->'prior')->'fence')) = 'string' AND (((v->'prior')->'fence') #>> '{}') ~ '^-?[0-9]+$'))))) AND (NOT (v ? 'committed') OR (jsonb_typeof((v->'committed')) = 'object' AND (v->'committed') ?& ARRAY['id','state','fence']::text[] AND ((v->'committed') - ARRAY['id','state','fence']::text[]) = '{}'::jsonb AND (NOT ((v->'committed') ? 'id') OR (jsonb_typeof(((v->'committed')->'id')) = 'string' AND (((v->'committed')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'state') OR (((v->'committed')->'state') = '"active"'::jsonb OR ((v->'committed')->'state') = '"committed"'::jsonb OR ((v->'committed')->'state') = '"released"'::jsonb OR ((v->'committed')->'state') = '"unknown"'::jsonb)) AND (NOT ((v->'committed') ? 'fence') OR (jsonb_typeof(((v->'committed')->'fence')) = 'string' AND (((v->'committed')->'fence') #>> '{}') ~ '^-?[0-9]+$')))) AND (NOT (v ? 'decisionRef') OR (jsonb_typeof((v->'decisionRef')) = 'string' AND length(((v->'decisionRef') #>> '{}')) >= 1))),false);
$wa$;

CREATE FUNCTION platform_private.json_evidence_ownermutationevidence(v jsonb) RETURNS boolean
LANGUAGE sql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
SELECT COALESCE((jsonb_typeof(v) = 'object' AND v ?& ARRAY['schema','owner','model','primaryKey','committed','decisionRef']::text[] AND (v - ARRAY['schema','owner','model','primaryKey','prior','committed','decisionRef']::text[]) = '{}'::jsonb AND (NOT (v ? 'schema') OR ((v->'schema') = '"database-owner-evidence.v1"'::jsonb)) AND (NOT (v ? 'owner') OR ((v->'owner') = '"platform_integration_owner"'::jsonb)) AND (NOT (v ? 'model') OR ((v->'model') = '"OwnerMutationEvidence"'::jsonb)) AND (NOT (v ? 'primaryKey') OR (jsonb_typeof((v->'primaryKey')) = 'object' AND (v->'primaryKey') ?& ARRAY['id']::text[] AND ((v->'primaryKey') - ARRAY['id']::text[]) = '{}'::jsonb AND (NOT ((v->'primaryKey') ? 'id') OR (jsonb_typeof(((v->'primaryKey')->'id')) = 'string' AND (((v->'primaryKey')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')))) AND (NOT (v ? 'prior') OR ((v->'prior') = 'null'::jsonb OR (jsonb_typeof((v->'prior')) = 'object' AND (v->'prior') ?& ARRAY['id','previousRevision','committedRevision','evidenceDigest']::text[] AND ((v->'prior') - ARRAY['id','previousRevision','committedRevision','evidenceDigest']::text[]) = '{}'::jsonb AND (NOT ((v->'prior') ? 'id') OR (jsonb_typeof(((v->'prior')->'id')) = 'string' AND (((v->'prior')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'previousRevision') OR ((jsonb_typeof(((v->'prior')->'previousRevision')) = 'string' AND (((v->'prior')->'previousRevision') #>> '{}') ~ '^-?[0-9]+$') OR (jsonb_typeof(((v->'prior')->'previousRevision')) = 'null'))) AND (NOT ((v->'prior') ? 'committedRevision') OR (jsonb_typeof(((v->'prior')->'committedRevision')) = 'string' AND (((v->'prior')->'committedRevision') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'prior') ? 'evidenceDigest') OR (jsonb_typeof(((v->'prior')->'evidenceDigest')) = 'string'))))) AND (NOT (v ? 'committed') OR (jsonb_typeof((v->'committed')) = 'object' AND (v->'committed') ?& ARRAY['id','previousRevision','committedRevision','evidenceDigest']::text[] AND ((v->'committed') - ARRAY['id','previousRevision','committedRevision','evidenceDigest']::text[]) = '{}'::jsonb AND (NOT ((v->'committed') ? 'id') OR (jsonb_typeof(((v->'committed')->'id')) = 'string' AND (((v->'committed')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'previousRevision') OR ((jsonb_typeof(((v->'committed')->'previousRevision')) = 'string' AND (((v->'committed')->'previousRevision') #>> '{}') ~ '^-?[0-9]+$') OR (jsonb_typeof(((v->'committed')->'previousRevision')) = 'null'))) AND (NOT ((v->'committed') ? 'committedRevision') OR (jsonb_typeof(((v->'committed')->'committedRevision')) = 'string' AND (((v->'committed')->'committedRevision') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'committed') ? 'evidenceDigest') OR (jsonb_typeof(((v->'committed')->'evidenceDigest')) = 'string')))) AND (NOT (v ? 'decisionRef') OR (jsonb_typeof((v->'decisionRef')) = 'string' AND length(((v->'decisionRef') #>> '{}')) >= 1))),false);
$wa$;

CREATE FUNCTION platform_private.json_evidence_customerprofilelifecycleevent(v jsonb) RETURNS boolean
LANGUAGE sql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
SELECT COALESCE((jsonb_typeof(v) = 'object' AND v ?& ARRAY['schema','owner','model','primaryKey','committed','decisionRef']::text[] AND (v - ARRAY['schema','owner','model','primaryKey','prior','committed','decisionRef']::text[]) = '{}'::jsonb AND (NOT (v ? 'schema') OR ((v->'schema') = '"database-owner-evidence.v1"'::jsonb)) AND (NOT (v ? 'owner') OR ((v->'owner') = '"customer_buyer_profile"'::jsonb)) AND (NOT (v ? 'model') OR ((v->'model') = '"CustomerProfileLifecycleEvent"'::jsonb)) AND (NOT (v ? 'primaryKey') OR (jsonb_typeof((v->'primaryKey')) = 'object' AND (v->'primaryKey') ?& ARRAY['id']::text[] AND ((v->'primaryKey') - ARRAY['id']::text[]) = '{}'::jsonb AND (NOT ((v->'primaryKey') ? 'id') OR (jsonb_typeof(((v->'primaryKey')->'id')) = 'string' AND (((v->'primaryKey')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')))) AND (NOT (v ? 'prior') OR ((v->'prior') = 'null'::jsonb OR (jsonb_typeof((v->'prior')) = 'object' AND (v->'prior') ?& ARRAY['id','sourceRevision','fromStatus','toStatus']::text[] AND ((v->'prior') - ARRAY['id','sourceRevision','fromStatus','toStatus']::text[]) = '{}'::jsonb AND (NOT ((v->'prior') ? 'id') OR (jsonb_typeof(((v->'prior')->'id')) = 'string' AND (((v->'prior')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'sourceRevision') OR (jsonb_typeof(((v->'prior')->'sourceRevision')) = 'string' AND (((v->'prior')->'sourceRevision') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'prior') ? 'fromStatus') OR ((((v->'prior')->'fromStatus') = '"draft"'::jsonb OR ((v->'prior')->'fromStatus') = '"active"'::jsonb OR ((v->'prior')->'fromStatus') = '"paused"'::jsonb OR ((v->'prior')->'fromStatus') = '"suspended"'::jsonb OR ((v->'prior')->'fromStatus') = '"archived"'::jsonb) OR (jsonb_typeof(((v->'prior')->'fromStatus')) = 'null'))) AND (NOT ((v->'prior') ? 'toStatus') OR (((v->'prior')->'toStatus') = '"draft"'::jsonb OR ((v->'prior')->'toStatus') = '"active"'::jsonb OR ((v->'prior')->'toStatus') = '"paused"'::jsonb OR ((v->'prior')->'toStatus') = '"suspended"'::jsonb OR ((v->'prior')->'toStatus') = '"archived"'::jsonb))))) AND (NOT (v ? 'committed') OR (jsonb_typeof((v->'committed')) = 'object' AND (v->'committed') ?& ARRAY['id','sourceRevision','fromStatus','toStatus']::text[] AND ((v->'committed') - ARRAY['id','sourceRevision','fromStatus','toStatus']::text[]) = '{}'::jsonb AND (NOT ((v->'committed') ? 'id') OR (jsonb_typeof(((v->'committed')->'id')) = 'string' AND (((v->'committed')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'sourceRevision') OR (jsonb_typeof(((v->'committed')->'sourceRevision')) = 'string' AND (((v->'committed')->'sourceRevision') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'committed') ? 'fromStatus') OR ((((v->'committed')->'fromStatus') = '"draft"'::jsonb OR ((v->'committed')->'fromStatus') = '"active"'::jsonb OR ((v->'committed')->'fromStatus') = '"paused"'::jsonb OR ((v->'committed')->'fromStatus') = '"suspended"'::jsonb OR ((v->'committed')->'fromStatus') = '"archived"'::jsonb) OR (jsonb_typeof(((v->'committed')->'fromStatus')) = 'null'))) AND (NOT ((v->'committed') ? 'toStatus') OR (((v->'committed')->'toStatus') = '"draft"'::jsonb OR ((v->'committed')->'toStatus') = '"active"'::jsonb OR ((v->'committed')->'toStatus') = '"paused"'::jsonb OR ((v->'committed')->'toStatus') = '"suspended"'::jsonb OR ((v->'committed')->'toStatus') = '"archived"'::jsonb)))) AND (NOT (v ? 'decisionRef') OR (jsonb_typeof((v->'decisionRef')) = 'string' AND length(((v->'decisionRef') #>> '{}')) >= 1))),false);
$wa$;

CREATE FUNCTION platform_private.json_evidence_trackbaseselection(v jsonb) RETURNS boolean
LANGUAGE sql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
SELECT COALESCE((jsonb_typeof(v) = 'object' AND v ?& ARRAY['schema','owner','model','primaryKey','committed','decisionRef']::text[] AND (v - ARRAY['schema','owner','model','primaryKey','prior','committed','decisionRef']::text[]) = '{}'::jsonb AND (NOT (v ? 'schema') OR ((v->'schema') = '"database-owner-evidence.v1"'::jsonb)) AND (NOT (v ? 'owner') OR ((v->'owner') = '"track_subscription_entitlement"'::jsonb)) AND (NOT (v ? 'model') OR ((v->'model') = '"TrackBaseSelection"'::jsonb)) AND (NOT (v ? 'primaryKey') OR (jsonb_typeof((v->'primaryKey')) = 'object' AND (v->'primaryKey') ?& ARRAY['id']::text[] AND ((v->'primaryKey') - ARRAY['id']::text[]) = '{}'::jsonb AND (NOT ((v->'primaryKey') ? 'id') OR (jsonb_typeof(((v->'primaryKey')->'id')) = 'string' AND (((v->'primaryKey')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')))) AND (NOT (v ? 'prior') OR ((v->'prior') = 'null'::jsonb OR (jsonb_typeof((v->'prior')) = 'object' AND (v->'prior') ?& ARRAY['id','userId','track','revision','sourceGeneration']::text[] AND ((v->'prior') - ARRAY['id','userId','track','revision','sourceGeneration']::text[]) = '{}'::jsonb AND (NOT ((v->'prior') ? 'id') OR (jsonb_typeof(((v->'prior')->'id')) = 'string' AND (((v->'prior')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'userId') OR (jsonb_typeof(((v->'prior')->'userId')) = 'string' AND (((v->'prior')->'userId') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'track') OR (((v->'prior')->'track') = '"customer"'::jsonb OR ((v->'prior')->'track') = '"candidate"'::jsonb OR ((v->'prior')->'track') = '"professional"'::jsonb)) AND (NOT ((v->'prior') ? 'revision') OR (jsonb_typeof(((v->'prior')->'revision')) = 'string' AND (((v->'prior')->'revision') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'prior') ? 'sourceGeneration') OR (jsonb_typeof(((v->'prior')->'sourceGeneration')) = 'string' AND (((v->'prior')->'sourceGeneration') #>> '{}') ~ '^-?[0-9]+$'))))) AND (NOT (v ? 'committed') OR (jsonb_typeof((v->'committed')) = 'object' AND (v->'committed') ?& ARRAY['id','userId','track','revision','sourceGeneration']::text[] AND ((v->'committed') - ARRAY['id','userId','track','revision','sourceGeneration']::text[]) = '{}'::jsonb AND (NOT ((v->'committed') ? 'id') OR (jsonb_typeof(((v->'committed')->'id')) = 'string' AND (((v->'committed')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'userId') OR (jsonb_typeof(((v->'committed')->'userId')) = 'string' AND (((v->'committed')->'userId') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'track') OR (((v->'committed')->'track') = '"customer"'::jsonb OR ((v->'committed')->'track') = '"candidate"'::jsonb OR ((v->'committed')->'track') = '"professional"'::jsonb)) AND (NOT ((v->'committed') ? 'revision') OR (jsonb_typeof(((v->'committed')->'revision')) = 'string' AND (((v->'committed')->'revision') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'committed') ? 'sourceGeneration') OR (jsonb_typeof(((v->'committed')->'sourceGeneration')) = 'string' AND (((v->'committed')->'sourceGeneration') #>> '{}') ~ '^-?[0-9]+$')))) AND (NOT (v ? 'decisionRef') OR (jsonb_typeof((v->'decisionRef')) = 'string' AND length(((v->'decisionRef') #>> '{}')) >= 1))),false);
$wa$;

CREATE FUNCTION platform_private.json_evidence_trackenrollmentreceipt(v jsonb) RETURNS boolean
LANGUAGE sql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
SELECT COALESCE((jsonb_typeof(v) = 'object' AND v ?& ARRAY['schema','owner','model','primaryKey','committed','decisionRef']::text[] AND (v - ARRAY['schema','owner','model','primaryKey','prior','committed','decisionRef']::text[]) = '{}'::jsonb AND (NOT (v ? 'schema') OR ((v->'schema') = '"database-owner-evidence.v1"'::jsonb)) AND (NOT (v ? 'owner') OR ((v->'owner') = '"track_subscription_entitlement"'::jsonb)) AND (NOT (v ? 'model') OR ((v->'model') = '"TrackEnrollmentReceipt"'::jsonb)) AND (NOT (v ? 'primaryKey') OR (jsonb_typeof((v->'primaryKey')) = 'object' AND (v->'primaryKey') ?& ARRAY['id']::text[] AND ((v->'primaryKey') - ARRAY['id']::text[]) = '{}'::jsonb AND (NOT ((v->'primaryKey') ? 'id') OR (jsonb_typeof(((v->'primaryKey')->'id')) = 'string' AND (((v->'primaryKey')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')))) AND (NOT (v ? 'prior') OR ((v->'prior') = 'null'::jsonb OR (jsonb_typeof((v->'prior')) = 'object' AND (v->'prior') ?& ARRAY['id','userId','track','sourceOwner','sourceCreationRevision','selectionRevision']::text[] AND ((v->'prior') - ARRAY['id','userId','track','sourceOwner','sourceCreationRevision','selectionRevision']::text[]) = '{}'::jsonb AND (NOT ((v->'prior') ? 'id') OR (jsonb_typeof(((v->'prior')->'id')) = 'string' AND (((v->'prior')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'userId') OR (jsonb_typeof(((v->'prior')->'userId')) = 'string' AND (((v->'prior')->'userId') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'track') OR (((v->'prior')->'track') = '"customer"'::jsonb OR ((v->'prior')->'track') = '"candidate"'::jsonb OR ((v->'prior')->'track') = '"professional"'::jsonb)) AND (NOT ((v->'prior') ? 'sourceOwner') OR (jsonb_typeof(((v->'prior')->'sourceOwner')) = 'string')) AND (NOT ((v->'prior') ? 'sourceCreationRevision') OR (jsonb_typeof(((v->'prior')->'sourceCreationRevision')) = 'string' AND (((v->'prior')->'sourceCreationRevision') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'prior') ? 'selectionRevision') OR (jsonb_typeof(((v->'prior')->'selectionRevision')) = 'string' AND (((v->'prior')->'selectionRevision') #>> '{}') ~ '^-?[0-9]+$'))))) AND (NOT (v ? 'committed') OR (jsonb_typeof((v->'committed')) = 'object' AND (v->'committed') ?& ARRAY['id','userId','track','sourceOwner','sourceCreationRevision','selectionRevision']::text[] AND ((v->'committed') - ARRAY['id','userId','track','sourceOwner','sourceCreationRevision','selectionRevision']::text[]) = '{}'::jsonb AND (NOT ((v->'committed') ? 'id') OR (jsonb_typeof(((v->'committed')->'id')) = 'string' AND (((v->'committed')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'userId') OR (jsonb_typeof(((v->'committed')->'userId')) = 'string' AND (((v->'committed')->'userId') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'track') OR (((v->'committed')->'track') = '"customer"'::jsonb OR ((v->'committed')->'track') = '"candidate"'::jsonb OR ((v->'committed')->'track') = '"professional"'::jsonb)) AND (NOT ((v->'committed') ? 'sourceOwner') OR (jsonb_typeof(((v->'committed')->'sourceOwner')) = 'string')) AND (NOT ((v->'committed') ? 'sourceCreationRevision') OR (jsonb_typeof(((v->'committed')->'sourceCreationRevision')) = 'string' AND (((v->'committed')->'sourceCreationRevision') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'committed') ? 'selectionRevision') OR (jsonb_typeof(((v->'committed')->'selectionRevision')) = 'string' AND (((v->'committed')->'selectionRevision') #>> '{}') ~ '^-?[0-9]+$')))) AND (NOT (v ? 'decisionRef') OR (jsonb_typeof((v->'decisionRef')) = 'string' AND length(((v->'decisionRef') #>> '{}')) >= 1))),false);
$wa$;

CREATE FUNCTION platform_private.json_evidence_trackusagereservation(v jsonb) RETURNS boolean
LANGUAGE sql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
SELECT COALESCE((jsonb_typeof(v) = 'object' AND v ?& ARRAY['schema','owner','model','primaryKey','committed','decisionRef']::text[] AND (v - ARRAY['schema','owner','model','primaryKey','prior','committed','decisionRef']::text[]) = '{}'::jsonb AND (NOT (v ? 'schema') OR ((v->'schema') = '"database-owner-evidence.v1"'::jsonb)) AND (NOT (v ? 'owner') OR ((v->'owner') = '"track_subscription_entitlement"'::jsonb)) AND (NOT (v ? 'model') OR ((v->'model') = '"TrackUsageReservation"'::jsonb)) AND (NOT (v ? 'primaryKey') OR (jsonb_typeof((v->'primaryKey')) = 'object' AND (v->'primaryKey') ?& ARRAY['id']::text[] AND ((v->'primaryKey') - ARRAY['id']::text[]) = '{}'::jsonb AND (NOT ((v->'primaryKey') ? 'id') OR (jsonb_typeof(((v->'primaryKey')->'id')) = 'string' AND (((v->'primaryKey')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')))) AND (NOT (v ? 'prior') OR ((v->'prior') = 'null'::jsonb OR (jsonb_typeof((v->'prior')) = 'object' AND (v->'prior') ?& ARRAY['id','userId','periodStart','periodEnd','acceptedAt','revision']::text[] AND ((v->'prior') - ARRAY['id','userId','periodStart','periodEnd','acceptedAt','revision']::text[]) = '{}'::jsonb AND (NOT ((v->'prior') ? 'id') OR (jsonb_typeof(((v->'prior')->'id')) = 'string' AND (((v->'prior')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'userId') OR (jsonb_typeof(((v->'prior')->'userId')) = 'string' AND (((v->'prior')->'userId') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'periodStart') OR (jsonb_typeof(((v->'prior')->'periodStart')) = 'string' AND platform_private.json_datetime((((v->'prior')->'periodStart') #>> '{}')))) AND (NOT ((v->'prior') ? 'periodEnd') OR (jsonb_typeof(((v->'prior')->'periodEnd')) = 'string' AND platform_private.json_datetime((((v->'prior')->'periodEnd') #>> '{}')))) AND (NOT ((v->'prior') ? 'acceptedAt') OR ((jsonb_typeof(((v->'prior')->'acceptedAt')) = 'string' AND platform_private.json_datetime((((v->'prior')->'acceptedAt') #>> '{}'))) OR (jsonb_typeof(((v->'prior')->'acceptedAt')) = 'null'))) AND (NOT ((v->'prior') ? 'revision') OR (jsonb_typeof(((v->'prior')->'revision')) = 'string' AND (((v->'prior')->'revision') #>> '{}') ~ '^-?[0-9]+$'))))) AND (NOT (v ? 'committed') OR (jsonb_typeof((v->'committed')) = 'object' AND (v->'committed') ?& ARRAY['id','userId','periodStart','periodEnd','acceptedAt','revision']::text[] AND ((v->'committed') - ARRAY['id','userId','periodStart','periodEnd','acceptedAt','revision']::text[]) = '{}'::jsonb AND (NOT ((v->'committed') ? 'id') OR (jsonb_typeof(((v->'committed')->'id')) = 'string' AND (((v->'committed')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'userId') OR (jsonb_typeof(((v->'committed')->'userId')) = 'string' AND (((v->'committed')->'userId') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'periodStart') OR (jsonb_typeof(((v->'committed')->'periodStart')) = 'string' AND platform_private.json_datetime((((v->'committed')->'periodStart') #>> '{}')))) AND (NOT ((v->'committed') ? 'periodEnd') OR (jsonb_typeof(((v->'committed')->'periodEnd')) = 'string' AND platform_private.json_datetime((((v->'committed')->'periodEnd') #>> '{}')))) AND (NOT ((v->'committed') ? 'acceptedAt') OR ((jsonb_typeof(((v->'committed')->'acceptedAt')) = 'string' AND platform_private.json_datetime((((v->'committed')->'acceptedAt') #>> '{}'))) OR (jsonb_typeof(((v->'committed')->'acceptedAt')) = 'null'))) AND (NOT ((v->'committed') ? 'revision') OR (jsonb_typeof(((v->'committed')->'revision')) = 'string' AND (((v->'committed')->'revision') #>> '{}') ~ '^-?[0-9]+$')))) AND (NOT (v ? 'decisionRef') OR (jsonb_typeof((v->'decisionRef')) = 'string' AND length(((v->'decisionRef') #>> '{}')) >= 1))),false);
$wa$;

CREATE FUNCTION platform_private.json_evidence_privacytargetinstruction(v jsonb) RETURNS boolean
LANGUAGE sql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
SELECT COALESCE((jsonb_typeof(v) = 'object' AND v ?& ARRAY['schema','owner','model','primaryKey','committed','decisionRef']::text[] AND (v - ARRAY['schema','owner','model','primaryKey','prior','committed','decisionRef']::text[]) = '{}'::jsonb AND (NOT (v ? 'schema') OR ((v->'schema') = '"database-owner-evidence.v1"'::jsonb)) AND (NOT (v ? 'owner') OR ((v->'owner') = '"privacy_data_erasure"'::jsonb)) AND (NOT (v ? 'model') OR ((v->'model') = '"PrivacyTargetInstruction"'::jsonb)) AND (NOT (v ? 'primaryKey') OR (jsonb_typeof((v->'primaryKey')) = 'object' AND (v->'primaryKey') ?& ARRAY['id']::text[] AND ((v->'primaryKey') - ARRAY['id']::text[]) = '{}'::jsonb AND (NOT ((v->'primaryKey') ? 'id') OR (jsonb_typeof(((v->'primaryKey')->'id')) = 'string' AND (((v->'primaryKey')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')))) AND (NOT (v ? 'prior') OR ((v->'prior') = 'null'::jsonb OR (jsonb_typeof((v->'prior')) = 'object' AND (v->'prior') ?& ARRAY['id','sourceId','sourceRevision','action','generation','descriptorHash']::text[] AND ((v->'prior') - ARRAY['id','sourceId','sourceRevision','action','generation','descriptorHash']::text[]) = '{}'::jsonb AND (NOT ((v->'prior') ? 'id') OR (jsonb_typeof(((v->'prior')->'id')) = 'string' AND (((v->'prior')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'sourceId') OR (jsonb_typeof(((v->'prior')->'sourceId')) = 'string')) AND (NOT ((v->'prior') ? 'sourceRevision') OR (jsonb_typeof(((v->'prior')->'sourceRevision')) = 'string')) AND (NOT ((v->'prior') ? 'action') OR (((v->'prior')->'action') = '"export"'::jsonb OR ((v->'prior')->'action') = '"erase"'::jsonb OR ((v->'prior')->'action') = '"restrict"'::jsonb OR ((v->'prior')->'action') = '"restore_marker"'::jsonb)) AND (NOT ((v->'prior') ? 'generation') OR (jsonb_typeof(((v->'prior')->'generation')) = 'string' AND (((v->'prior')->'generation') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'prior') ? 'descriptorHash') OR (jsonb_typeof(((v->'prior')->'descriptorHash')) = 'string'))))) AND (NOT (v ? 'committed') OR (jsonb_typeof((v->'committed')) = 'object' AND (v->'committed') ?& ARRAY['id','sourceId','sourceRevision','action','generation','descriptorHash']::text[] AND ((v->'committed') - ARRAY['id','sourceId','sourceRevision','action','generation','descriptorHash']::text[]) = '{}'::jsonb AND (NOT ((v->'committed') ? 'id') OR (jsonb_typeof(((v->'committed')->'id')) = 'string' AND (((v->'committed')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'sourceId') OR (jsonb_typeof(((v->'committed')->'sourceId')) = 'string')) AND (NOT ((v->'committed') ? 'sourceRevision') OR (jsonb_typeof(((v->'committed')->'sourceRevision')) = 'string')) AND (NOT ((v->'committed') ? 'action') OR (((v->'committed')->'action') = '"export"'::jsonb OR ((v->'committed')->'action') = '"erase"'::jsonb OR ((v->'committed')->'action') = '"restrict"'::jsonb OR ((v->'committed')->'action') = '"restore_marker"'::jsonb)) AND (NOT ((v->'committed') ? 'generation') OR (jsonb_typeof(((v->'committed')->'generation')) = 'string' AND (((v->'committed')->'generation') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'committed') ? 'descriptorHash') OR (jsonb_typeof(((v->'committed')->'descriptorHash')) = 'string')))) AND (NOT (v ? 'decisionRef') OR (jsonb_typeof((v->'decisionRef')) = 'string' AND length(((v->'decisionRef') #>> '{}')) >= 1))),false);
$wa$;

CREATE FUNCTION platform_private.json_evidence_privacyownerreceipt(v jsonb) RETURNS boolean
LANGUAGE sql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
SELECT COALESCE((jsonb_typeof(v) = 'object' AND v ?& ARRAY['schema','owner','model','primaryKey','committed','decisionRef']::text[] AND (v - ARRAY['schema','owner','model','primaryKey','prior','committed','decisionRef']::text[]) = '{}'::jsonb AND (NOT (v ? 'schema') OR ((v->'schema') = '"database-owner-evidence.v1"'::jsonb)) AND (NOT (v ? 'owner') OR ((v->'owner') = '"privacy_data_erasure"'::jsonb)) AND (NOT (v ? 'model') OR ((v->'model') = '"PrivacyOwnerReceipt"'::jsonb)) AND (NOT (v ? 'primaryKey') OR (jsonb_typeof((v->'primaryKey')) = 'object' AND (v->'primaryKey') ?& ARRAY['id']::text[] AND ((v->'primaryKey') - ARRAY['id']::text[]) = '{}'::jsonb AND (NOT ((v->'primaryKey') ? 'id') OR (jsonb_typeof(((v->'primaryKey')->'id')) = 'string' AND (((v->'primaryKey')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')))) AND (NOT (v ? 'prior') OR ((v->'prior') = 'null'::jsonb OR (jsonb_typeof((v->'prior')) = 'object' AND (v->'prior') ?& ARRAY['id','generation','disposition','artifactDigest']::text[] AND ((v->'prior') - ARRAY['id','generation','disposition','artifactDigest']::text[]) = '{}'::jsonb AND (NOT ((v->'prior') ? 'id') OR (jsonb_typeof(((v->'prior')->'id')) = 'string' AND (((v->'prior')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'generation') OR (jsonb_typeof(((v->'prior')->'generation')) = 'string' AND (((v->'prior')->'generation') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'prior') ? 'disposition') OR (((v->'prior')->'disposition') = '"completed"'::jsonb OR ((v->'prior')->'disposition') = '"retained"'::jsonb OR ((v->'prior')->'disposition') = '"omitted"'::jsonb OR ((v->'prior')->'disposition') = '"failed"'::jsonb OR ((v->'prior')->'disposition') = '"unknown"'::jsonb)) AND (NOT ((v->'prior') ? 'artifactDigest') OR ((jsonb_typeof(((v->'prior')->'artifactDigest')) = 'string') OR (jsonb_typeof(((v->'prior')->'artifactDigest')) = 'null')))))) AND (NOT (v ? 'committed') OR (jsonb_typeof((v->'committed')) = 'object' AND (v->'committed') ?& ARRAY['id','generation','disposition','artifactDigest']::text[] AND ((v->'committed') - ARRAY['id','generation','disposition','artifactDigest']::text[]) = '{}'::jsonb AND (NOT ((v->'committed') ? 'id') OR (jsonb_typeof(((v->'committed')->'id')) = 'string' AND (((v->'committed')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'generation') OR (jsonb_typeof(((v->'committed')->'generation')) = 'string' AND (((v->'committed')->'generation') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'committed') ? 'disposition') OR (((v->'committed')->'disposition') = '"completed"'::jsonb OR ((v->'committed')->'disposition') = '"retained"'::jsonb OR ((v->'committed')->'disposition') = '"omitted"'::jsonb OR ((v->'committed')->'disposition') = '"failed"'::jsonb OR ((v->'committed')->'disposition') = '"unknown"'::jsonb)) AND (NOT ((v->'committed') ? 'artifactDigest') OR ((jsonb_typeof(((v->'committed')->'artifactDigest')) = 'string') OR (jsonb_typeof(((v->'committed')->'artifactDigest')) = 'null'))))) AND (NOT (v ? 'decisionRef') OR (jsonb_typeof((v->'decisionRef')) = 'string' AND length(((v->'decisionRef') #>> '{}')) >= 1))),false);
$wa$;

CREATE FUNCTION platform_private.json_evidence_privacyrestoremarker(v jsonb) RETURNS boolean
LANGUAGE sql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
SELECT COALESCE((jsonb_typeof(v) = 'object' AND v ?& ARRAY['schema','owner','model','primaryKey','committed','decisionRef']::text[] AND (v - ARRAY['schema','owner','model','primaryKey','prior','committed','decisionRef']::text[]) = '{}'::jsonb AND (NOT (v ? 'schema') OR ((v->'schema') = '"database-owner-evidence.v1"'::jsonb)) AND (NOT (v ? 'owner') OR ((v->'owner') = '"privacy_data_erasure"'::jsonb)) AND (NOT (v ? 'model') OR ((v->'model') = '"PrivacyRestoreMarker"'::jsonb)) AND (NOT (v ? 'primaryKey') OR (jsonb_typeof((v->'primaryKey')) = 'object' AND (v->'primaryKey') ?& ARRAY['id']::text[] AND ((v->'primaryKey') - ARRAY['id']::text[]) = '{}'::jsonb AND (NOT ((v->'primaryKey') ? 'id') OR (jsonb_typeof(((v->'primaryKey')->'id')) = 'string' AND (((v->'primaryKey')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')))) AND (NOT (v ? 'prior') OR ((v->'prior') = 'null'::jsonb OR (jsonb_typeof((v->'prior')) = 'object' AND (v->'prior') ?& ARRAY['id','sourceId','generation','action','revision']::text[] AND ((v->'prior') - ARRAY['id','sourceId','generation','action','revision']::text[]) = '{}'::jsonb AND (NOT ((v->'prior') ? 'id') OR (jsonb_typeof(((v->'prior')->'id')) = 'string' AND (((v->'prior')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'prior') ? 'sourceId') OR (jsonb_typeof(((v->'prior')->'sourceId')) = 'string')) AND (NOT ((v->'prior') ? 'generation') OR (jsonb_typeof(((v->'prior')->'generation')) = 'string' AND (((v->'prior')->'generation') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'prior') ? 'action') OR (((v->'prior')->'action') = '"export"'::jsonb OR ((v->'prior')->'action') = '"erase"'::jsonb OR ((v->'prior')->'action') = '"restrict"'::jsonb OR ((v->'prior')->'action') = '"restore_marker"'::jsonb)) AND (NOT ((v->'prior') ? 'revision') OR (jsonb_typeof(((v->'prior')->'revision')) = 'string' AND (((v->'prior')->'revision') #>> '{}') ~ '^-?[0-9]+$'))))) AND (NOT (v ? 'committed') OR (jsonb_typeof((v->'committed')) = 'object' AND (v->'committed') ?& ARRAY['id','sourceId','generation','action','revision']::text[] AND ((v->'committed') - ARRAY['id','sourceId','generation','action','revision']::text[]) = '{}'::jsonb AND (NOT ((v->'committed') ? 'id') OR (jsonb_typeof(((v->'committed')->'id')) = 'string' AND (((v->'committed')->'id') #>> '{}') ~ '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')) AND (NOT ((v->'committed') ? 'sourceId') OR (jsonb_typeof(((v->'committed')->'sourceId')) = 'string')) AND (NOT ((v->'committed') ? 'generation') OR (jsonb_typeof(((v->'committed')->'generation')) = 'string' AND (((v->'committed')->'generation') #>> '{}') ~ '^-?[0-9]+$')) AND (NOT ((v->'committed') ? 'action') OR (((v->'committed')->'action') = '"export"'::jsonb OR ((v->'committed')->'action') = '"erase"'::jsonb OR ((v->'committed')->'action') = '"restrict"'::jsonb OR ((v->'committed')->'action') = '"restore_marker"'::jsonb)) AND (NOT ((v->'committed') ? 'revision') OR (jsonb_typeof(((v->'committed')->'revision')) = 'string' AND (((v->'committed')->'revision') #>> '{}') ~ '^-?[0-9]+$')))) AND (NOT (v ? 'decisionRef') OR (jsonb_typeof((v->'decisionRef')) = 'string' AND length(((v->'decisionRef') #>> '{}')) >= 1))),false);
$wa$;

CREATE FUNCTION platform_private.json_customer_event(v jsonb) RETURNS boolean
LANGUAGE sql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
SELECT COALESCE((jsonb_typeof(v) = 'object' AND v ?& ARRAY['eventName','customerProfileId','userId','lifecycleRevision','safeState']::text[] AND (v - ARRAY['eventName','customerProfileId','userId','lifecycleRevision','safeState']::text[]) = '{}'::jsonb AND (NOT (v ? 'eventName') OR ((v->'eventName') = '"customer.lifecycle_changed.v1"'::jsonb)) AND (NOT (v ? 'customerProfileId') OR (jsonb_typeof((v->'customerProfileId')) = 'string' AND length(((v->'customerProfileId') #>> '{}')) >= 1 AND length(((v->'customerProfileId') #>> '{}')) <= 128 AND ((v->'customerProfileId') #>> '{}') ~ '^[A-Za-z0-9][A-Za-z0-9._:-]*$')) AND (NOT (v ? 'userId') OR (jsonb_typeof((v->'userId')) = 'string' AND length(((v->'userId') #>> '{}')) >= 1 AND length(((v->'userId') #>> '{}')) <= 128 AND ((v->'userId') #>> '{}') ~ '^[A-Za-z0-9][A-Za-z0-9._:-]*$')) AND (NOT (v ? 'lifecycleRevision') OR (jsonb_typeof((v->'lifecycleRevision')) = 'string' AND length(((v->'lifecycleRevision') #>> '{}')) >= 1 AND length(((v->'lifecycleRevision') #>> '{}')) <= 128 AND ((v->'lifecycleRevision') #>> '{}') ~ '^[A-Za-z0-9][A-Za-z0-9._:-]*$')) AND (NOT (v ? 'safeState') OR (jsonb_typeof((v->'safeState')) = 'string' AND length(((v->'safeState') #>> '{}')) >= 1 AND length(((v->'safeState') #>> '{}')) <= 128 AND ((v->'safeState') #>> '{}') ~ '^[A-Za-z0-9][A-Za-z0-9._:-]*$'))),false);
$wa$;

CREATE FUNCTION platform_private.json_track_command(v jsonb) RETURNS boolean
LANGUAGE sql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
SELECT COALESCE((jsonb_typeof(v) = 'object' AND v ?& ARRAY['sourceOwner','userId','track','customerProfileId','sourceCreationRevision','sourceCreationReceipt','semanticKey']::text[] AND (v - ARRAY['sourceOwner','userId','track','customerProfileId','sourceCreationRevision','sourceCreationReceipt','semanticKey']::text[]) = '{}'::jsonb AND (NOT (v ? 'sourceOwner') OR ((v->'sourceOwner') = '"customer_buyer_profile"'::jsonb)) AND (NOT (v ? 'userId') OR (jsonb_typeof((v->'userId')) = 'string' AND length(((v->'userId') #>> '{}')) >= 1 AND length(((v->'userId') #>> '{}')) <= 128 AND ((v->'userId') #>> '{}') ~ '^[A-Za-z0-9][A-Za-z0-9._:-]*$')) AND (NOT (v ? 'track') OR ((v->'track') = '"customer"'::jsonb)) AND (NOT (v ? 'customerProfileId') OR (jsonb_typeof((v->'customerProfileId')) = 'string' AND length(((v->'customerProfileId') #>> '{}')) >= 1 AND length(((v->'customerProfileId') #>> '{}')) <= 128 AND ((v->'customerProfileId') #>> '{}') ~ '^[A-Za-z0-9][A-Za-z0-9._:-]*$')) AND (NOT (v ? 'sourceCreationRevision') OR (jsonb_typeof((v->'sourceCreationRevision')) = 'string' AND length(((v->'sourceCreationRevision') #>> '{}')) >= 1 AND length(((v->'sourceCreationRevision') #>> '{}')) <= 128 AND ((v->'sourceCreationRevision') #>> '{}') ~ '^[A-Za-z0-9][A-Za-z0-9._:-]*$')) AND (NOT (v ? 'sourceCreationReceipt') OR (jsonb_typeof((v->'sourceCreationReceipt')) = 'string' AND length(((v->'sourceCreationReceipt') #>> '{}')) >= 1 AND length(((v->'sourceCreationReceipt') #>> '{}')) <= 128 AND ((v->'sourceCreationReceipt') #>> '{}') ~ '^[A-Za-z0-9][A-Za-z0-9._:-]*$')) AND (NOT (v ? 'semanticKey') OR (jsonb_typeof((v->'semanticKey')) = 'string' AND length(((v->'semanticKey') #>> '{}')) >= 1))),false);
$wa$;

CREATE FUNCTION platform_private.json_track_result(v jsonb) RETURNS boolean
LANGUAGE sql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
SELECT COALESCE((jsonb_typeof(v) = 'object' AND v ?& ARRAY['outcome','selectionRevision','receipt']::text[] AND (v - ARRAY['outcome','selectionRevision','receipt']::text[]) = '{}'::jsonb AND (NOT (v ? 'outcome') OR ((v->'outcome') = '"enrolled"'::jsonb OR (v->'outcome') = '"already_enrolled"'::jsonb OR (v->'outcome') = '"conflict"'::jsonb OR (v->'outcome') = '"denied"'::jsonb OR (v->'outcome') = '"unavailable"'::jsonb)) AND (NOT (v ? 'selectionRevision') OR ((jsonb_typeof((v->'selectionRevision')) = 'string' AND length(((v->'selectionRevision') #>> '{}')) >= 1 AND length(((v->'selectionRevision') #>> '{}')) <= 128 AND ((v->'selectionRevision') #>> '{}') ~ '^[A-Za-z0-9][A-Za-z0-9._:-]*$') OR (jsonb_typeof((v->'selectionRevision')) = 'null'))) AND (NOT (v ? 'receipt') OR (jsonb_typeof((v->'receipt')) = 'string' AND length(((v->'receipt') #>> '{}')) >= 1 AND length(((v->'receipt') #>> '{}')) <= 128 AND ((v->'receipt') #>> '{}') ~ '^[A-Za-z0-9][A-Za-z0-9._:-]*$'))),false);
$wa$;

CREATE FUNCTION platform_private.json_sh004_result(v jsonb) RETURNS boolean
LANGUAGE sql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
SELECT COALESCE((CASE WHEN COALESCE((jsonb_typeof(v) = 'object' AND v ?& ARRAY['contract','requestId','status','value']::text[] AND (v - ARRAY['contract','requestId','status','value']::text[]) = '{}'::jsonb AND (NOT (v ? 'contract') OR ((v->'contract') = '"SH-004.v1"'::jsonb)) AND (NOT (v ? 'requestId') OR (jsonb_typeof((v->'requestId')) = 'string' AND length(((v->'requestId') #>> '{}')) >= 1 AND length(((v->'requestId') #>> '{}')) <= 128 AND ((v->'requestId') #>> '{}') ~ '^[A-Za-z0-9][A-Za-z0-9._:-]*$')) AND (NOT (v ? 'status') OR ((v->'status') = '"ok"'::jsonb)) AND (NOT (v ? 'value') OR (jsonb_typeof((v->'value')) = 'object' AND (v->'value') ?& ARRAY['customerProfileId','userId','lifecycle','sourceToken','receipt']::text[] AND ((v->'value') - ARRAY['customerProfileId','userId','lifecycle','sourceToken','receipt']::text[]) = '{}'::jsonb AND (NOT ((v->'value') ? 'customerProfileId') OR (jsonb_typeof(((v->'value')->'customerProfileId')) = 'string' AND length((((v->'value')->'customerProfileId') #>> '{}')) >= 1 AND length((((v->'value')->'customerProfileId') #>> '{}')) <= 128 AND (((v->'value')->'customerProfileId') #>> '{}') ~ '^[A-Za-z0-9][A-Za-z0-9._:-]*$')) AND (NOT ((v->'value') ? 'userId') OR (jsonb_typeof(((v->'value')->'userId')) = 'string' AND length((((v->'value')->'userId') #>> '{}')) >= 1 AND length((((v->'value')->'userId') #>> '{}')) <= 128 AND (((v->'value')->'userId') #>> '{}') ~ '^[A-Za-z0-9][A-Za-z0-9._:-]*$')) AND (NOT ((v->'value') ? 'lifecycle') OR (((v->'value')->'lifecycle') = '"draft"'::jsonb OR ((v->'value')->'lifecycle') = '"active"'::jsonb OR ((v->'value')->'lifecycle') = '"paused"'::jsonb OR ((v->'value')->'lifecycle') = '"suspended"'::jsonb OR ((v->'value')->'lifecycle') = '"archived"'::jsonb)) AND (NOT ((v->'value') ? 'sourceToken') OR (jsonb_typeof(((v->'value')->'sourceToken')) = 'string' AND length((((v->'value')->'sourceToken') #>> '{}')) >= 1 AND length((((v->'value')->'sourceToken') #>> '{}')) <= 128 AND (((v->'value')->'sourceToken') #>> '{}') ~ '^[A-Za-z0-9][A-Za-z0-9._:-]*$')) AND (NOT ((v->'value') ? 'receipt') OR (jsonb_typeof(((v->'value')->'receipt')) = 'object' AND ((v->'value')->'receipt') ?& ARRAY['owner','id','semanticKey','fingerprint','sourceToken','recordedAt']::text[] AND (((v->'value')->'receipt') - ARRAY['owner','id','semanticKey','fingerprint','sourceToken','recordedAt']::text[]) = '{}'::jsonb AND (NOT (((v->'value')->'receipt') ? 'owner') OR ((((v->'value')->'receipt')->'owner') = '"identity_access"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"role_authority"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"consent_disclosure"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"privacy_data_erasure"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"taxonomy_classification"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"professional_eligibility"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"trust_verification_screening"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"marketplace_supply"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"gig_demand"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"transaction_order"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"payment_payout_tax"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"booking_calendar"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"video_session"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"organization_hiring"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"job_compliance"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"candidate_application_resume_privacy"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"job_interview"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"messaging"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"notification"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"media_file_access"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"search_public_visibility"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"review_dispute"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"content_moderation_legal_notice"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"audit_event_ledger"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"admin_review_compliance_hold"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"sweepstakes_prize"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"gamification_rewards"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"healthcare_regulated_services"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"location_safety"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"ai_taxonomy"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"observability_ops"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"digital_goods_access"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"customer_buyer_profile"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"track_subscription_entitlement"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"platform_integration_owner"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"platform_execution"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"platform_security"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"platform_realtime"'::jsonb)) AND (NOT (((v->'value')->'receipt') ? 'id') OR (jsonb_typeof((((v->'value')->'receipt')->'id')) = 'string' AND length(((((v->'value')->'receipt')->'id') #>> '{}')) >= 1 AND length(((((v->'value')->'receipt')->'id') #>> '{}')) <= 128 AND ((((v->'value')->'receipt')->'id') #>> '{}') ~ '^[A-Za-z0-9][A-Za-z0-9._:-]*$')) AND (NOT (((v->'value')->'receipt') ? 'semanticKey') OR (jsonb_typeof((((v->'value')->'receipt')->'semanticKey')) = 'string' AND length(((((v->'value')->'receipt')->'semanticKey') #>> '{}')) >= 1 AND length(((((v->'value')->'receipt')->'semanticKey') #>> '{}')) <= 128 AND ((((v->'value')->'receipt')->'semanticKey') #>> '{}') ~ '^[A-Za-z0-9][A-Za-z0-9._:-]*$')) AND (NOT (((v->'value')->'receipt') ? 'fingerprint') OR (jsonb_typeof((((v->'value')->'receipt')->'fingerprint')) = 'string' AND length(((((v->'value')->'receipt')->'fingerprint') #>> '{}')) >= 64 AND length(((((v->'value')->'receipt')->'fingerprint') #>> '{}')) <= 64 AND ((((v->'value')->'receipt')->'fingerprint') #>> '{}') ~ '^[a-f0-9]{64}$')) AND (NOT (((v->'value')->'receipt') ? 'sourceToken') OR (jsonb_typeof((((v->'value')->'receipt')->'sourceToken')) = 'string' AND length(((((v->'value')->'receipt')->'sourceToken') #>> '{}')) >= 1 AND length(((((v->'value')->'receipt')->'sourceToken') #>> '{}')) <= 128 AND ((((v->'value')->'receipt')->'sourceToken') #>> '{}') ~ '^[A-Za-z0-9][A-Za-z0-9._:-]*$')) AND (NOT (((v->'value')->'receipt') ? 'recordedAt') OR (jsonb_typeof((((v->'value')->'receipt')->'recordedAt')) = 'string' AND ((((v->'value')->'receipt')->'recordedAt') #>> '{}') ~ '^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?(?:Z|[+-]\d\d:\d\d)$' AND platform_private.json_datetime(((((v->'value')->'receipt')->'recordedAt') #>> '{}'))))))))),false) THEN 1 ELSE 0 END + CASE WHEN COALESCE((jsonb_typeof(v) = 'object' AND v ?& ARRAY['contract','requestId','status','reasonCode','retryable','safeMessageKey']::text[] AND (v - ARRAY['contract','requestId','status','reasonCode','retryable','safeMessageKey']::text[]) = '{}'::jsonb AND (NOT (v ? 'contract') OR ((v->'contract') = '"SH-004.v1"'::jsonb)) AND (NOT (v ? 'requestId') OR (jsonb_typeof((v->'requestId')) = 'string' AND length(((v->'requestId') #>> '{}')) >= 1 AND length(((v->'requestId') #>> '{}')) <= 128 AND ((v->'requestId') #>> '{}') ~ '^[A-Za-z0-9][A-Za-z0-9._:-]*$')) AND (NOT (v ? 'status') OR ((v->'status') = '"denied"'::jsonb OR (v->'status') = '"not_found"'::jsonb OR (v->'status') = '"stale"'::jsonb OR (v->'status') = '"conflict"'::jsonb OR (v->'status') = '"unsupported"'::jsonb OR (v->'status') = '"unavailable"'::jsonb OR (v->'status') = '"invalid"'::jsonb)) AND (NOT (v ? 'reasonCode') OR (jsonb_typeof((v->'reasonCode')) = 'string' AND length(((v->'reasonCode') #>> '{}')) >= 1 AND length(((v->'reasonCode') #>> '{}')) <= 128 AND ((v->'reasonCode') #>> '{}') ~ '^[A-Za-z0-9][A-Za-z0-9._:-]*$')) AND (NOT (v ? 'retryable') OR (jsonb_typeof((v->'retryable')) = 'boolean')) AND (NOT (v ? 'safeMessageKey') OR (jsonb_typeof((v->'safeMessageKey')) = 'string' AND length(((v->'safeMessageKey') #>> '{}')) >= 1 AND length(((v->'safeMessageKey') #>> '{}')) <= 128 AND ((v->'safeMessageKey') #>> '{}') ~ '^[A-Za-z0-9][A-Za-z0-9._:-]*$'))),false) THEN 1 ELSE 0 END = 1),false);
$wa$;

CREATE FUNCTION platform_private.json_sh114_result(v jsonb) RETURNS boolean
LANGUAGE sql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
SELECT COALESCE((CASE WHEN COALESCE((jsonb_typeof(v) = 'object' AND v ?& ARRAY['contract','requestId','status','value']::text[] AND (v - ARRAY['contract','requestId','status','value']::text[]) = '{}'::jsonb AND (NOT (v ? 'contract') OR ((v->'contract') = '"SH-114.v1"'::jsonb)) AND (NOT (v ? 'requestId') OR (jsonb_typeof((v->'requestId')) = 'string' AND length(((v->'requestId') #>> '{}')) >= 1 AND length(((v->'requestId') #>> '{}')) <= 128 AND ((v->'requestId') #>> '{}') ~ '^[A-Za-z0-9][A-Za-z0-9._:-]*$')) AND (NOT (v ? 'status') OR ((v->'status') = '"ok"'::jsonb)) AND (NOT (v ? 'value') OR (jsonb_typeof((v->'value')) = 'object' AND (v->'value') ?& ARRAY['profileId','sourceToken','receipt']::text[] AND ((v->'value') - ARRAY['profileId','sourceToken','receipt']::text[]) = '{}'::jsonb AND (NOT ((v->'value') ? 'profileId') OR (jsonb_typeof(((v->'value')->'profileId')) = 'string' AND length((((v->'value')->'profileId') #>> '{}')) >= 1 AND length((((v->'value')->'profileId') #>> '{}')) <= 128 AND (((v->'value')->'profileId') #>> '{}') ~ '^[A-Za-z0-9][A-Za-z0-9._:-]*$')) AND (NOT ((v->'value') ? 'sourceToken') OR (jsonb_typeof(((v->'value')->'sourceToken')) = 'string' AND length((((v->'value')->'sourceToken') #>> '{}')) >= 1 AND length((((v->'value')->'sourceToken') #>> '{}')) <= 128 AND (((v->'value')->'sourceToken') #>> '{}') ~ '^[A-Za-z0-9][A-Za-z0-9._:-]*$')) AND (NOT ((v->'value') ? 'receipt') OR (jsonb_typeof(((v->'value')->'receipt')) = 'object' AND ((v->'value')->'receipt') ?& ARRAY['owner','id','semanticKey','fingerprint','sourceToken','recordedAt']::text[] AND (((v->'value')->'receipt') - ARRAY['owner','id','semanticKey','fingerprint','sourceToken','recordedAt']::text[]) = '{}'::jsonb AND (NOT (((v->'value')->'receipt') ? 'owner') OR ((((v->'value')->'receipt')->'owner') = '"identity_access"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"role_authority"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"consent_disclosure"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"privacy_data_erasure"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"taxonomy_classification"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"professional_eligibility"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"trust_verification_screening"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"marketplace_supply"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"gig_demand"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"transaction_order"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"payment_payout_tax"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"booking_calendar"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"video_session"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"organization_hiring"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"job_compliance"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"candidate_application_resume_privacy"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"job_interview"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"messaging"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"notification"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"media_file_access"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"search_public_visibility"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"review_dispute"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"content_moderation_legal_notice"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"audit_event_ledger"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"admin_review_compliance_hold"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"sweepstakes_prize"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"gamification_rewards"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"healthcare_regulated_services"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"location_safety"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"ai_taxonomy"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"observability_ops"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"digital_goods_access"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"customer_buyer_profile"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"track_subscription_entitlement"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"platform_integration_owner"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"platform_execution"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"platform_security"'::jsonb OR (((v->'value')->'receipt')->'owner') = '"platform_realtime"'::jsonb)) AND (NOT (((v->'value')->'receipt') ? 'id') OR (jsonb_typeof((((v->'value')->'receipt')->'id')) = 'string' AND length(((((v->'value')->'receipt')->'id') #>> '{}')) >= 1 AND length(((((v->'value')->'receipt')->'id') #>> '{}')) <= 128 AND ((((v->'value')->'receipt')->'id') #>> '{}') ~ '^[A-Za-z0-9][A-Za-z0-9._:-]*$')) AND (NOT (((v->'value')->'receipt') ? 'semanticKey') OR (jsonb_typeof((((v->'value')->'receipt')->'semanticKey')) = 'string' AND length(((((v->'value')->'receipt')->'semanticKey') #>> '{}')) >= 1 AND length(((((v->'value')->'receipt')->'semanticKey') #>> '{}')) <= 128 AND ((((v->'value')->'receipt')->'semanticKey') #>> '{}') ~ '^[A-Za-z0-9][A-Za-z0-9._:-]*$')) AND (NOT (((v->'value')->'receipt') ? 'fingerprint') OR (jsonb_typeof((((v->'value')->'receipt')->'fingerprint')) = 'string' AND length(((((v->'value')->'receipt')->'fingerprint') #>> '{}')) >= 64 AND length(((((v->'value')->'receipt')->'fingerprint') #>> '{}')) <= 64 AND ((((v->'value')->'receipt')->'fingerprint') #>> '{}') ~ '^[a-f0-9]{64}$')) AND (NOT (((v->'value')->'receipt') ? 'sourceToken') OR (jsonb_typeof((((v->'value')->'receipt')->'sourceToken')) = 'string' AND length(((((v->'value')->'receipt')->'sourceToken') #>> '{}')) >= 1 AND length(((((v->'value')->'receipt')->'sourceToken') #>> '{}')) <= 128 AND ((((v->'value')->'receipt')->'sourceToken') #>> '{}') ~ '^[A-Za-z0-9][A-Za-z0-9._:-]*$')) AND (NOT (((v->'value')->'receipt') ? 'recordedAt') OR (jsonb_typeof((((v->'value')->'receipt')->'recordedAt')) = 'string' AND ((((v->'value')->'receipt')->'recordedAt') #>> '{}') ~ '^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?(?:Z|[+-]\d\d:\d\d)$' AND platform_private.json_datetime(((((v->'value')->'receipt')->'recordedAt') #>> '{}'))))))))),false) THEN 1 ELSE 0 END + CASE WHEN COALESCE((jsonb_typeof(v) = 'object' AND v ?& ARRAY['contract','requestId','status','reasonCode','retryable','safeMessageKey']::text[] AND (v - ARRAY['contract','requestId','status','reasonCode','retryable','safeMessageKey']::text[]) = '{}'::jsonb AND (NOT (v ? 'contract') OR ((v->'contract') = '"SH-114.v1"'::jsonb)) AND (NOT (v ? 'requestId') OR (jsonb_typeof((v->'requestId')) = 'string' AND length(((v->'requestId') #>> '{}')) >= 1 AND length(((v->'requestId') #>> '{}')) <= 128 AND ((v->'requestId') #>> '{}') ~ '^[A-Za-z0-9][A-Za-z0-9._:-]*$')) AND (NOT (v ? 'status') OR ((v->'status') = '"denied"'::jsonb OR (v->'status') = '"not_found"'::jsonb OR (v->'status') = '"stale"'::jsonb OR (v->'status') = '"conflict"'::jsonb OR (v->'status') = '"unsupported"'::jsonb OR (v->'status') = '"unavailable"'::jsonb OR (v->'status') = '"invalid"'::jsonb)) AND (NOT (v ? 'reasonCode') OR (jsonb_typeof((v->'reasonCode')) = 'string' AND length(((v->'reasonCode') #>> '{}')) >= 1 AND length(((v->'reasonCode') #>> '{}')) <= 128 AND ((v->'reasonCode') #>> '{}') ~ '^[A-Za-z0-9][A-Za-z0-9._:-]*$')) AND (NOT (v ? 'retryable') OR (jsonb_typeof((v->'retryable')) = 'boolean')) AND (NOT (v ? 'safeMessageKey') OR (jsonb_typeof((v->'safeMessageKey')) = 'string' AND length(((v->'safeMessageKey') #>> '{}')) >= 1 AND length(((v->'safeMessageKey') #>> '{}')) <= 128 AND ((v->'safeMessageKey') #>> '{}') ~ '^[A-Za-z0-9][A-Za-z0-9._:-]*$'))),false) THEN 1 ELSE 0 END = 1),false);
$wa$;

-- SQL-01/02/06: only the issuer and SELECT-only private helper can read grants.
ALTER TABLE platform.database_action_grant ENABLE ROW LEVEL SECURITY;
ALTER TABLE platform.database_action_grant FORCE ROW LEVEL SECURITY;
GRANT SELECT,INSERT ON platform.database_action_grant TO wa_context_issuer;
GRANT UPDATE(revoked_at) ON platform.database_action_grant TO wa_context_issuer;
GRANT SELECT ON platform.database_action_grant TO wa_private_helper_owner;
CREATE POLICY grant_issuer_select ON platform.database_action_grant FOR SELECT TO wa_context_issuer USING (issuer_service = session_user::text);
CREATE POLICY grant_issuer_insert ON platform.database_action_grant FOR INSERT TO wa_context_issuer WITH CHECK (issuer_service = session_user::text);
CREATE POLICY grant_issuer_revoke ON platform.database_action_grant FOR UPDATE TO wa_context_issuer USING (issuer_service = session_user::text) WITH CHECK (issuer_service = session_user::text);
CREATE POLICY grant_helper_read ON platform.database_action_grant FOR SELECT TO wa_private_helper_owner USING (database_login_role = session_user::text AND backend_pid = pg_backend_pid() AND transaction_id = pg_current_xact_id()::text);
GRANT SELECT(user_id,security_generation) ON app.user_security_profiles TO wa_private_helper_owner;
CREATE POLICY security_helper_read ON app.user_security_profiles FOR SELECT TO wa_private_helper_owner USING (true);
-- Minimal Identity columns only; this nonrecursive leaf policy exposes no source body.

CREATE FUNCTION platform_private.bound_grant(take_action_lock boolean DEFAULT true) RETURNS platform.database_action_grant
LANGUAGE plpgsql VOLATILE SECURITY DEFINER
SET search_path = pg_catalog
AS $wa$
DECLARE g platform.database_action_grant; handle text;
BEGIN
 IF current_setting('transaction_isolation') <> 'read committed' THEN RETURN NULL; END IF;
 handle := current_setting('wa.context_hash',true);
 IF handle IS NULL OR handle !~ '^[0-9a-f]{64}$' THEN RETURN NULL; END IF;
 IF take_action_lock THEN
  -- Bind takes no lock: a separately committed revocation can win before action.
  PERFORM pg_advisory_xact_lock_shared(hashtextextended('grant:'||handle,0));
 END IF;
 SELECT * INTO g FROM platform.database_action_grant WHERE token_hash=handle
  AND database_login_role=session_user::text AND backend_pid=pg_backend_pid()
  AND transaction_id=pg_current_xact_id()::text AND revoked_at IS NULL
  AND expires_at > clock_timestamp();
 IF NOT FOUND THEN RETURN NULL; END IF;
 IF g.principal_user_id IS NULL THEN
  IF take_action_lock THEN
   PERFORM pg_advisory_xact_lock_shared(hashtextextended('service:'||g.service_principal,0));
  END IF;
  IF NOT EXISTS (SELECT 1 FROM platform_private.identity_service_authorization a
   WHERE a.service_principal=g.service_principal AND a.security_generation=g.security_generation AND a.revoked_at IS NULL)
  THEN RETURN NULL; END IF;
  RETURN g;
 END IF;
 IF take_action_lock THEN
  PERFORM pg_advisory_xact_lock_shared(hashtextextended('identity:'||g.principal_user_id::text,0));
 END IF;
 IF NOT EXISTS (SELECT 1 FROM app.user_security_profiles s WHERE s.user_id=g.principal_user_id
  AND s.security_generation=g.security_generation) THEN RETURN NULL; END IF;
 RETURN g;
END;
$wa$;

CREATE FUNCTION platform_private.bind_request_context(secret text) RETURNS void
LANGUAGE plpgsql VOLATILE SECURITY DEFINER
SET search_path = pg_catalog
AS $wa$
DECLARE g platform.database_action_grant;
BEGIN
 IF secret IS NULL OR secret !~ '^[0-9a-f]{64}$' THEN RAISE EXCEPTION 'invalid context' USING ERRCODE='42501'; END IF;
 PERFORM set_config('wa.context_hash',encode(sha256(decode(secret,'hex')),'hex'),true);
 g:=platform_private.bound_grant(false);
 IF g.id IS NULL THEN RAISE EXCEPTION 'invalid, stale or unsupported context' USING ERRCODE='42501'; END IF;
END;
$wa$;

CREATE FUNCTION platform_private.context_allows(owner_id text, action_name text, target_kind text, target_id text, purpose_name text) RETURNS boolean
LANGUAGE plpgsql VOLATILE SECURITY DEFINER
SET search_path = pg_catalog
AS $wa$
DECLARE g platform.database_action_grant;
BEGIN
 g:=platform_private.bound_grant(true);
 RETURN COALESCE(g.id IS NOT NULL AND g.owner_module_id=owner_id AND g.action=action_name
  AND g.target_kind=target_kind AND g.target_id=target_id AND g.purpose=purpose_name,false);
END;
$wa$;

CREATE FUNCTION platform_private.protected_scope(model_name text, row_key text, verb text) RETURNS boolean
LANGUAGE plpgsql VOLATILE SECURITY DEFINER
SET search_path = pg_catalog
AS $wa$
DECLARE g platform.database_action_grant; BEGIN
g:=platform_private.bound_grant(true); IF g.id IS NULL THEN RETURN false; END IF;
IF model_name=g.target_kind AND row_key<>g.target_id THEN RETURN false; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='ConsentLog' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('consent_disclosure','SH-003.v1','ConsentLog',g.target_id,'owner:queryOwnerFacts') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='ConsentLog' OR (verb='SELECT' AND model_name='ConsentPresentation' AND 'ConsentLog/'||g.target_id||'/presentation/'||row_key=ANY(g.allowed_fields)) OR (verb='SELECT' AND model_name='ConsentContentRevision' AND 'ConsentLog/'||g.target_id||'/contentRevision/'||row_key=ANY(g.allowed_fields)) OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('consent_disclosure','SH-007.v1','ConsentLog',g.target_id,'owner:recordConsentProof') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='ConsentLog' OR (verb='SELECT' AND model_name='ConsentPresentation' AND 'ConsentLog/'||g.target_id||'/presentation/'||row_key=ANY(g.allowed_fields)) OR (verb='SELECT' AND model_name='ConsentContentRevision' AND 'ConsentLog/'||g.target_id||'/contentRevision/'||row_key=ANY(g.allowed_fields)) OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('consent_disclosure','SH-008.v1','ConsentLog',g.target_id,'owner:queryConsentProof') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='ConsentLog' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('consent_disclosure','SH-009.v1','ConsentLog',g.target_id,'owner:resolveActiveConsentVersion') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='ConsentLog' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('consent_disclosure','SH-010.v1','ConsentLog',g.target_id,'owner:presentStandaloneConsent') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='ConsentLog' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('consent_disclosure','SH-015.v1','ConsentLog',g.target_id,'owner:returnDecisionResult') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='ConsentLog' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('consent_disclosure','SH-031.v1','ConsentLog',g.target_id,'owner:appendDomainLifecycleEvent') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='ConsentLog' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('consent_disclosure','SH-043.v1','ConsentLog',g.target_id,'owner:resolveNotificationRecipients') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='ConsentLog' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('consent_disclosure','SH-053.v1','ConsentLog',g.target_id,'owner:transitionLifecycleState') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='ConsentLog' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('consent_disclosure','SH-080.v1','ConsentLog',g.target_id,'owner:manageVersionedRules') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='ConsentLog' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('consent_disclosure','SH-095.v1','ConsentLog',g.target_id,'owner:executePrivacyInstruction') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='ConsentLog' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('consent_disclosure','SH-096.v1','ConsentLog',g.target_id,'owner:enumerateSubjectData') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='ConsentLog' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('consent_disclosure','SH-097.v1','ConsentLog',g.target_id,'owner:evaluateRetentionRequirement') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='ConsentLog' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('consent_disclosure','SH-098.v1','ConsentLog',g.target_id,'owner:anonymizePersonalFields') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='ConsentLog' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('consent_disclosure','SH-123.v1','ConsentLog',g.target_id,'owner:validateOwnedTargetReference') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='PrivacyRequest' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('privacy_data_erasure','SH-003.v1','PrivacyRequest',g.target_id,'owner:queryOwnerFacts') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='PrivacyRequest' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('privacy_data_erasure','SH-015.v1','PrivacyRequest',g.target_id,'owner:returnDecisionResult') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='PrivacyRequest' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('privacy_data_erasure','SH-026.v1','PrivacyRequest',g.target_id,'owner:authorizeContextualResourceAccess') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='PrivacyRequest' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('privacy_data_erasure','SH-031.v1','PrivacyRequest',g.target_id,'owner:appendDomainLifecycleEvent') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='PrivacyRequest' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('privacy_data_erasure','SH-043.v1','PrivacyRequest',g.target_id,'owner:resolveNotificationRecipients') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='PrivacyRequest' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('privacy_data_erasure','SH-049.v1','PrivacyRequest',g.target_id,'owner:orchestrateWorkflowSteps') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='PrivacyRequest' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('privacy_data_erasure','SH-050.v1','PrivacyRequest',g.target_id,'owner:reconcileWorkflowStatus') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='PrivacyRequest' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('privacy_data_erasure','SH-053.v1','PrivacyRequest',g.target_id,'owner:transitionLifecycleState') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='PrivacyRequest' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('privacy_data_erasure','SH-088.v1','PrivacyRequest',g.target_id,'owner:manageTemporaryAccessGrant') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='PrivacyRequest' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('privacy_data_erasure','SH-089.v1','PrivacyRequest',g.target_id,'owner:revokeTemporaryAccessGrant') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='PrivacyRequest' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('privacy_data_erasure','SH-095.v1','PrivacyRequest',g.target_id,'owner:executePrivacyInstruction') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='PrivacyRequest' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('privacy_data_erasure','SH-096.v1','PrivacyRequest',g.target_id,'owner:enumerateSubjectData') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='PrivacyRequest' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('privacy_data_erasure','SH-097.v1','PrivacyRequest',g.target_id,'owner:evaluateRetentionRequirement') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='PrivacyRequest' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('privacy_data_erasure','SH-098.v1','PrivacyRequest',g.target_id,'owner:anonymizePersonalFields') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='PrivacyRequest' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('privacy_data_erasure','SH-099.v1','PrivacyRequest',g.target_id,'owner:orchestratePrivacyFulfillment') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='PrivacyRequest' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('privacy_data_erasure','SH-100.v1','PrivacyRequest',g.target_id,'owner:createPrivacyExportArtifact') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='PrivacyRequest' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('privacy_data_erasure','SH-104.v1','PrivacyRequest',g.target_id,'owner:preserveEvidenceSnapshot') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='PrivacyRequest' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('privacy_data_erasure','SH-110.v1','PrivacyRequest',g.target_id,'owner:createDomainSnapshot') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='PrivacyRequest' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('privacy_data_erasure','SH-123.v1','PrivacyRequest',g.target_id,'owner:validateOwnedTargetReference') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='PrivacyRequest' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('privacy_data_erasure','SH-125.v1','PrivacyRequest',g.target_id,'owner:recordDomainAccessEvent') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='AgeGateAttempt' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-001.v1','AgeGateAttempt',g.target_id,'owner:resolveAuthenticatedActor') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='AgeGateAttempt' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-003.v1','AgeGateAttempt',g.target_id,'owner:queryOwnerFacts') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='AgeGateAttempt' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-014.v1','AgeGateAttempt',g.target_id,'owner:requireStepUpForSensitiveAction') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='AgeGateAttempt' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-015.v1','AgeGateAttempt',g.target_id,'owner:returnDecisionResult') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='AgeGateAttempt' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-031.v1','AgeGateAttempt',g.target_id,'owner:appendDomainLifecycleEvent') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='AgeGateAttempt' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-043.v1','AgeGateAttempt',g.target_id,'owner:resolveNotificationRecipients') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='AgeGateAttempt' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-053.v1','AgeGateAttempt',g.target_id,'owner:transitionLifecycleState') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='AgeGateAttempt' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-060.v1','AgeGateAttempt',g.target_id,'owner:deduplicateProviderEvent') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='AgeGateAttempt' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-061.v1','AgeGateAttempt',g.target_id,'owner:translateProviderStatus') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='AgeGateAttempt' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-062.v1','AgeGateAttempt',g.target_id,'owner:reconcileProviderState') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='AgeGateAttempt' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-063.v1','AgeGateAttempt',g.target_id,'owner:captureProviderSnapshot') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='AgeGateAttempt' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-064.v1','AgeGateAttempt',g.target_id,'owner:authorizeExternalProviderConnection') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='AgeGateAttempt' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-070.v1','AgeGateAttempt',g.target_id,'owner:deleteProviderResource') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='AgeGateAttempt' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-088.v1','AgeGateAttempt',g.target_id,'owner:manageTemporaryAccessGrant') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='AgeGateAttempt' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-089.v1','AgeGateAttempt',g.target_id,'owner:revokeTemporaryAccessGrant') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='AgeGateAttempt' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-095.v1','AgeGateAttempt',g.target_id,'owner:executePrivacyInstruction') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='AgeGateAttempt' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-096.v1','AgeGateAttempt',g.target_id,'owner:enumerateSubjectData') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='AgeGateAttempt' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-097.v1','AgeGateAttempt',g.target_id,'owner:evaluateRetentionRequirement') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='AgeGateAttempt' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-098.v1','AgeGateAttempt',g.target_id,'owner:anonymizePersonalFields') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='AgeGateAttempt' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-123.v1','AgeGateAttempt',g.target_id,'owner:validateOwnedTargetReference') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='AgeGateBlock' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-001.v1','AgeGateBlock',g.target_id,'owner:resolveAuthenticatedActor') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='AgeGateBlock' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-003.v1','AgeGateBlock',g.target_id,'owner:queryOwnerFacts') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='AgeGateBlock' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-014.v1','AgeGateBlock',g.target_id,'owner:requireStepUpForSensitiveAction') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='AgeGateBlock' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-015.v1','AgeGateBlock',g.target_id,'owner:returnDecisionResult') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='AgeGateBlock' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-031.v1','AgeGateBlock',g.target_id,'owner:appendDomainLifecycleEvent') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='AgeGateBlock' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-043.v1','AgeGateBlock',g.target_id,'owner:resolveNotificationRecipients') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='AgeGateBlock' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-053.v1','AgeGateBlock',g.target_id,'owner:transitionLifecycleState') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='AgeGateBlock' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-060.v1','AgeGateBlock',g.target_id,'owner:deduplicateProviderEvent') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='AgeGateBlock' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-061.v1','AgeGateBlock',g.target_id,'owner:translateProviderStatus') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='AgeGateBlock' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-062.v1','AgeGateBlock',g.target_id,'owner:reconcileProviderState') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='AgeGateBlock' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-063.v1','AgeGateBlock',g.target_id,'owner:captureProviderSnapshot') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='AgeGateBlock' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-064.v1','AgeGateBlock',g.target_id,'owner:authorizeExternalProviderConnection') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='AgeGateBlock' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-070.v1','AgeGateBlock',g.target_id,'owner:deleteProviderResource') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='AgeGateBlock' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-088.v1','AgeGateBlock',g.target_id,'owner:manageTemporaryAccessGrant') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='AgeGateBlock' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-089.v1','AgeGateBlock',g.target_id,'owner:revokeTemporaryAccessGrant') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='AgeGateBlock' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-095.v1','AgeGateBlock',g.target_id,'owner:executePrivacyInstruction') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='AgeGateBlock' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-096.v1','AgeGateBlock',g.target_id,'owner:enumerateSubjectData') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='AgeGateBlock' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-097.v1','AgeGateBlock',g.target_id,'owner:evaluateRetentionRequirement') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='AgeGateBlock' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-098.v1','AgeGateBlock',g.target_id,'owner:anonymizePersonalFields') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='AgeGateBlock' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-123.v1','AgeGateBlock',g.target_id,'owner:validateOwnedTargetReference') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='AccessAuditLog' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('audit_event_ledger','SH-003.v1','AccessAuditLog',g.target_id,'owner:queryOwnerFacts') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='AccessAuditLog' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('audit_event_ledger','SH-015.v1','AccessAuditLog',g.target_id,'owner:returnDecisionResult') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='AccessAuditLog' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('audit_event_ledger','SH-029.v1','AccessAuditLog',g.target_id,'owner:appendAuditEvent') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='AccessAuditLog' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('audit_event_ledger','SH-030.v1','AccessAuditLog',g.target_id,'owner:recordSensitiveAccess') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='AccessAuditLog' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('audit_event_ledger','SH-031.v1','AccessAuditLog',g.target_id,'owner:appendDomainLifecycleEvent') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='AccessAuditLog' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('audit_event_ledger','SH-043.v1','AccessAuditLog',g.target_id,'owner:resolveNotificationRecipients') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='AccessAuditLog' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('audit_event_ledger','SH-053.v1','AccessAuditLog',g.target_id,'owner:transitionLifecycleState') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='AccessAuditLog' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('audit_event_ledger','SH-095.v1','AccessAuditLog',g.target_id,'owner:executePrivacyInstruction') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='AccessAuditLog' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('audit_event_ledger','SH-096.v1','AccessAuditLog',g.target_id,'owner:enumerateSubjectData') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='AccessAuditLog' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('audit_event_ledger','SH-097.v1','AccessAuditLog',g.target_id,'owner:evaluateRetentionRequirement') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='AccessAuditLog' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('audit_event_ledger','SH-098.v1','AccessAuditLog',g.target_id,'owner:anonymizePersonalFields') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='AccessAuditLog' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('audit_event_ledger','SH-123.v1','AccessAuditLog',g.target_id,'owner:validateOwnedTargetReference') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='User' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-001.v1','User',g.target_id,'owner:resolveAuthenticatedActor') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='User' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-003.v1','User',g.target_id,'owner:queryOwnerFacts') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='User' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-014.v1','User',g.target_id,'owner:requireStepUpForSensitiveAction') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='User' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-015.v1','User',g.target_id,'owner:returnDecisionResult') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='User' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-031.v1','User',g.target_id,'owner:appendDomainLifecycleEvent') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='User' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-043.v1','User',g.target_id,'owner:resolveNotificationRecipients') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='User' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-053.v1','User',g.target_id,'owner:transitionLifecycleState') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='User' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-060.v1','User',g.target_id,'owner:deduplicateProviderEvent') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='User' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-061.v1','User',g.target_id,'owner:translateProviderStatus') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='User' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-062.v1','User',g.target_id,'owner:reconcileProviderState') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='User' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-063.v1','User',g.target_id,'owner:captureProviderSnapshot') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='User' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-064.v1','User',g.target_id,'owner:authorizeExternalProviderConnection') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='User' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-070.v1','User',g.target_id,'owner:deleteProviderResource') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='User' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-088.v1','User',g.target_id,'owner:manageTemporaryAccessGrant') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='User' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-089.v1','User',g.target_id,'owner:revokeTemporaryAccessGrant') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='User' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-095.v1','User',g.target_id,'owner:executePrivacyInstruction') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='User' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-096.v1','User',g.target_id,'owner:enumerateSubjectData') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='User' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-097.v1','User',g.target_id,'owner:evaluateRetentionRequirement') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='User' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-098.v1','User',g.target_id,'owner:anonymizePersonalFields') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='User' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-123.v1','User',g.target_id,'owner:validateOwnedTargetReference') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='UserRole' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-001.v1','UserRole',g.target_id,'owner:resolveAuthenticatedActor') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='UserRole' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-003.v1','UserRole',g.target_id,'owner:queryOwnerFacts') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='UserRole' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-014.v1','UserRole',g.target_id,'owner:requireStepUpForSensitiveAction') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='UserRole' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-015.v1','UserRole',g.target_id,'owner:returnDecisionResult') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='UserRole' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-031.v1','UserRole',g.target_id,'owner:appendDomainLifecycleEvent') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='UserRole' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-043.v1','UserRole',g.target_id,'owner:resolveNotificationRecipients') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='UserRole' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-053.v1','UserRole',g.target_id,'owner:transitionLifecycleState') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='UserRole' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-060.v1','UserRole',g.target_id,'owner:deduplicateProviderEvent') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='UserRole' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-061.v1','UserRole',g.target_id,'owner:translateProviderStatus') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='UserRole' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-062.v1','UserRole',g.target_id,'owner:reconcileProviderState') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='UserRole' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-063.v1','UserRole',g.target_id,'owner:captureProviderSnapshot') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='UserRole' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-064.v1','UserRole',g.target_id,'owner:authorizeExternalProviderConnection') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='UserRole' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-070.v1','UserRole',g.target_id,'owner:deleteProviderResource') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='UserRole' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-088.v1','UserRole',g.target_id,'owner:manageTemporaryAccessGrant') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='UserRole' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-089.v1','UserRole',g.target_id,'owner:revokeTemporaryAccessGrant') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='UserRole' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-095.v1','UserRole',g.target_id,'owner:executePrivacyInstruction') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='UserRole' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-096.v1','UserRole',g.target_id,'owner:enumerateSubjectData') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='UserRole' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-097.v1','UserRole',g.target_id,'owner:evaluateRetentionRequirement') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='UserRole' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-098.v1','UserRole',g.target_id,'owner:anonymizePersonalFields') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='UserRole' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-123.v1','UserRole',g.target_id,'owner:validateOwnedTargetReference') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='ProfessionalProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('professional_eligibility','SH-003.v1','ProfessionalProfile',g.target_id,'owner:queryOwnerFacts') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='ProfessionalProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('professional_eligibility','SH-015.v1','ProfessionalProfile',g.target_id,'owner:returnDecisionResult') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='ProfessionalProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('professional_eligibility','SH-016.v1','ProfessionalProfile',g.target_id,'owner:evaluateProfessionalReadiness') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='ProfessionalProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('professional_eligibility','SH-024.v1','ProfessionalProfile',g.target_id,'owner:evaluatePublicReadiness') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='ProfessionalProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('professional_eligibility','SH-031.v1','ProfessionalProfile',g.target_id,'owner:appendDomainLifecycleEvent') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='ProfessionalProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('professional_eligibility','SH-043.v1','ProfessionalProfile',g.target_id,'owner:resolveNotificationRecipients') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='ProfessionalProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('professional_eligibility','SH-053.v1','ProfessionalProfile',g.target_id,'owner:transitionLifecycleState') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='ProfessionalProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('professional_eligibility','SH-090.v1','ProfessionalProfile',g.target_id,'owner:attachValidatedMedia') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='ProfessionalProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('professional_eligibility','SH-094.v1','ProfessionalProfile',g.target_id,'owner:buildSourceProjection') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='ProfessionalProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('professional_eligibility','SH-095.v1','ProfessionalProfile',g.target_id,'owner:executePrivacyInstruction') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='ProfessionalProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('professional_eligibility','SH-096.v1','ProfessionalProfile',g.target_id,'owner:enumerateSubjectData') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='ProfessionalProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('professional_eligibility','SH-097.v1','ProfessionalProfile',g.target_id,'owner:evaluateRetentionRequirement') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='ProfessionalProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('professional_eligibility','SH-098.v1','ProfessionalProfile',g.target_id,'owner:anonymizePersonalFields') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='ProfessionalProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('professional_eligibility','SH-102.v1','ProfessionalProfile',g.target_id,'owner:resolveModerationTarget') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='ProfessionalProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('professional_eligibility','SH-103.v1','ProfessionalProfile',g.target_id,'owner:executeModerationDecision') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='ProfessionalProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('professional_eligibility','SH-114.v1','ProfessionalProfile',g.target_id,'owner:provisionOneToOneProfile') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='ProfessionalProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('professional_eligibility','SH-115.v1','ProfessionalProfile',g.target_id,'owner:buildAggregateProjection') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='ProfessionalProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('professional_eligibility','SH-121.v1','ProfessionalProfile',g.target_id,'owner:applyAiSuggestion') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='ProfessionalProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('professional_eligibility','SH-123.v1','ProfessionalProfile',g.target_id,'owner:validateOwnedTargetReference') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='ProfessionalProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('professional_eligibility','SH-124.v1','ProfessionalProfile',g.target_id,'owner:generateUniqueSlug') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='CandidateProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('candidate_application_resume_privacy','SH-003.v1','CandidateProfile',g.target_id,'owner:queryOwnerFacts') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='CandidateProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('candidate_application_resume_privacy','SH-015.v1','CandidateProfile',g.target_id,'owner:returnDecisionResult') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='CandidateProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('candidate_application_resume_privacy','SH-024.v1','CandidateProfile',g.target_id,'owner:evaluatePublicReadiness') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='CandidateProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('candidate_application_resume_privacy','SH-026.v1','CandidateProfile',g.target_id,'owner:authorizeContextualResourceAccess') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='CandidateProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('candidate_application_resume_privacy','SH-031.v1','CandidateProfile',g.target_id,'owner:appendDomainLifecycleEvent') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='CandidateProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('candidate_application_resume_privacy','SH-043.v1','CandidateProfile',g.target_id,'owner:resolveNotificationRecipients') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='CandidateProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('candidate_application_resume_privacy','SH-053.v1','CandidateProfile',g.target_id,'owner:transitionLifecycleState') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='CandidateProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('candidate_application_resume_privacy','SH-090.v1','CandidateProfile',g.target_id,'owner:attachValidatedMedia') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='CandidateProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('candidate_application_resume_privacy','SH-094.v1','CandidateProfile',g.target_id,'owner:buildSourceProjection') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='CandidateProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('candidate_application_resume_privacy','SH-095.v1','CandidateProfile',g.target_id,'owner:executePrivacyInstruction') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='CandidateProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('candidate_application_resume_privacy','SH-096.v1','CandidateProfile',g.target_id,'owner:enumerateSubjectData') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='CandidateProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('candidate_application_resume_privacy','SH-097.v1','CandidateProfile',g.target_id,'owner:evaluateRetentionRequirement') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='CandidateProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('candidate_application_resume_privacy','SH-098.v1','CandidateProfile',g.target_id,'owner:anonymizePersonalFields') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='CandidateProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('candidate_application_resume_privacy','SH-102.v1','CandidateProfile',g.target_id,'owner:resolveModerationTarget') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='CandidateProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('candidate_application_resume_privacy','SH-103.v1','CandidateProfile',g.target_id,'owner:executeModerationDecision') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='CandidateProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('candidate_application_resume_privacy','SH-114.v1','CandidateProfile',g.target_id,'owner:provisionOneToOneProfile') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='CandidateProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('candidate_application_resume_privacy','SH-115.v1','CandidateProfile',g.target_id,'owner:buildAggregateProjection') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='CandidateProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('candidate_application_resume_privacy','SH-121.v1','CandidateProfile',g.target_id,'owner:applyAiSuggestion') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='CandidateProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('candidate_application_resume_privacy','SH-123.v1','CandidateProfile',g.target_id,'owner:validateOwnedTargetReference') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='CandidateProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('candidate_application_resume_privacy','SH-125.v1','CandidateProfile',g.target_id,'owner:recordDomainAccessEvent') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='AuditEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('audit_event_ledger','SH-003.v1','AuditEvent',g.target_id,'owner:queryOwnerFacts') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='AuditEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('audit_event_ledger','SH-015.v1','AuditEvent',g.target_id,'owner:returnDecisionResult') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='AuditEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('audit_event_ledger','SH-029.v1','AuditEvent',g.target_id,'owner:appendAuditEvent') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='AuditEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('audit_event_ledger','SH-030.v1','AuditEvent',g.target_id,'owner:recordSensitiveAccess') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='AuditEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('audit_event_ledger','SH-031.v1','AuditEvent',g.target_id,'owner:appendDomainLifecycleEvent') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='AuditEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('audit_event_ledger','SH-043.v1','AuditEvent',g.target_id,'owner:resolveNotificationRecipients') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='AuditEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('audit_event_ledger','SH-053.v1','AuditEvent',g.target_id,'owner:transitionLifecycleState') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='AuditEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('audit_event_ledger','SH-095.v1','AuditEvent',g.target_id,'owner:executePrivacyInstruction') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='AuditEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('audit_event_ledger','SH-096.v1','AuditEvent',g.target_id,'owner:enumerateSubjectData') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='AuditEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('audit_event_ledger','SH-097.v1','AuditEvent',g.target_id,'owner:evaluateRetentionRequirement') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='AuditEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('audit_event_ledger','SH-098.v1','AuditEvent',g.target_id,'owner:anonymizePersonalFields') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='AuditEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('audit_event_ledger','SH-123.v1','AuditEvent',g.target_id,'owner:validateOwnedTargetReference') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='UserSecurityProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-001.v1','UserSecurityProfile',g.target_id,'owner:resolveAuthenticatedActor') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='UserSecurityProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-003.v1','UserSecurityProfile',g.target_id,'owner:queryOwnerFacts') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='UserSecurityProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-014.v1','UserSecurityProfile',g.target_id,'owner:requireStepUpForSensitiveAction') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='UserSecurityProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-015.v1','UserSecurityProfile',g.target_id,'owner:returnDecisionResult') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='UserSecurityProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-031.v1','UserSecurityProfile',g.target_id,'owner:appendDomainLifecycleEvent') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='UserSecurityProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-043.v1','UserSecurityProfile',g.target_id,'owner:resolveNotificationRecipients') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='UserSecurityProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-053.v1','UserSecurityProfile',g.target_id,'owner:transitionLifecycleState') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='UserSecurityProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-060.v1','UserSecurityProfile',g.target_id,'owner:deduplicateProviderEvent') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='UserSecurityProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-061.v1','UserSecurityProfile',g.target_id,'owner:translateProviderStatus') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='UserSecurityProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-062.v1','UserSecurityProfile',g.target_id,'owner:reconcileProviderState') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='UserSecurityProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-063.v1','UserSecurityProfile',g.target_id,'owner:captureProviderSnapshot') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='UserSecurityProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-064.v1','UserSecurityProfile',g.target_id,'owner:authorizeExternalProviderConnection') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='UserSecurityProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-070.v1','UserSecurityProfile',g.target_id,'owner:deleteProviderResource') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='UserSecurityProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-088.v1','UserSecurityProfile',g.target_id,'owner:manageTemporaryAccessGrant') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='UserSecurityProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-089.v1','UserSecurityProfile',g.target_id,'owner:revokeTemporaryAccessGrant') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='UserSecurityProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-095.v1','UserSecurityProfile',g.target_id,'owner:executePrivacyInstruction') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='UserSecurityProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-096.v1','UserSecurityProfile',g.target_id,'owner:enumerateSubjectData') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='UserSecurityProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-097.v1','UserSecurityProfile',g.target_id,'owner:evaluateRetentionRequirement') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='UserSecurityProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-098.v1','UserSecurityProfile',g.target_id,'owner:anonymizePersonalFields') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='UserSecurityProfile' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-123.v1','UserSecurityProfile',g.target_id,'owner:validateOwnedTargetReference') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='AuthProviderAccount' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-001.v1','AuthProviderAccount',g.target_id,'owner:resolveAuthenticatedActor') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='AuthProviderAccount' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-003.v1','AuthProviderAccount',g.target_id,'owner:queryOwnerFacts') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='AuthProviderAccount' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-014.v1','AuthProviderAccount',g.target_id,'owner:requireStepUpForSensitiveAction') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='AuthProviderAccount' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-015.v1','AuthProviderAccount',g.target_id,'owner:returnDecisionResult') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='AuthProviderAccount' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-031.v1','AuthProviderAccount',g.target_id,'owner:appendDomainLifecycleEvent') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='AuthProviderAccount' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-043.v1','AuthProviderAccount',g.target_id,'owner:resolveNotificationRecipients') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='AuthProviderAccount' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-053.v1','AuthProviderAccount',g.target_id,'owner:transitionLifecycleState') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='AuthProviderAccount' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-060.v1','AuthProviderAccount',g.target_id,'owner:deduplicateProviderEvent') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='AuthProviderAccount' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-061.v1','AuthProviderAccount',g.target_id,'owner:translateProviderStatus') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='AuthProviderAccount' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-062.v1','AuthProviderAccount',g.target_id,'owner:reconcileProviderState') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='AuthProviderAccount' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-063.v1','AuthProviderAccount',g.target_id,'owner:captureProviderSnapshot') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='AuthProviderAccount' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-064.v1','AuthProviderAccount',g.target_id,'owner:authorizeExternalProviderConnection') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='AuthProviderAccount' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-070.v1','AuthProviderAccount',g.target_id,'owner:deleteProviderResource') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='AuthProviderAccount' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-088.v1','AuthProviderAccount',g.target_id,'owner:manageTemporaryAccessGrant') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='AuthProviderAccount' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-089.v1','AuthProviderAccount',g.target_id,'owner:revokeTemporaryAccessGrant') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='AuthProviderAccount' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-095.v1','AuthProviderAccount',g.target_id,'owner:executePrivacyInstruction') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='AuthProviderAccount' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-096.v1','AuthProviderAccount',g.target_id,'owner:enumerateSubjectData') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='AuthProviderAccount' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-097.v1','AuthProviderAccount',g.target_id,'owner:evaluateRetentionRequirement') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='AuthProviderAccount' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-098.v1','AuthProviderAccount',g.target_id,'owner:anonymizePersonalFields') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='AuthProviderAccount' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-123.v1','AuthProviderAccount',g.target_id,'owner:validateOwnedTargetReference') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackPlan' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-003.v1','TrackPlan',g.target_id,'owner:queryOwnerFacts') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackPlan' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-005.v1','TrackPlan',g.target_id,'owner:resolveEntitlement') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackPlan' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-006.v1','TrackPlan',g.target_id,'owner:consumeMeteredEntitlement') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackPlan' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-015.v1','TrackPlan',g.target_id,'owner:returnDecisionResult') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackPlan' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-031.v1','TrackPlan',g.target_id,'owner:appendDomainLifecycleEvent') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackPlan' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-043.v1','TrackPlan',g.target_id,'owner:resolveNotificationRecipients') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackPlan' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-053.v1','TrackPlan',g.target_id,'owner:transitionLifecycleState') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackPlan' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-060.v1','TrackPlan',g.target_id,'owner:deduplicateProviderEvent') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackPlan' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-061.v1','TrackPlan',g.target_id,'owner:translateProviderStatus') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackPlan' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-062.v1','TrackPlan',g.target_id,'owner:reconcileProviderState') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackPlan' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-063.v1','TrackPlan',g.target_id,'owner:captureProviderSnapshot') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackPlan' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-064.v1','TrackPlan',g.target_id,'owner:authorizeExternalProviderConnection') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackPlan' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-070.v1','TrackPlan',g.target_id,'owner:deleteProviderResource') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackPlan' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-080.v1','TrackPlan',g.target_id,'owner:manageVersionedRules') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackPlan' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-095.v1','TrackPlan',g.target_id,'owner:executePrivacyInstruction') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackPlan' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-096.v1','TrackPlan',g.target_id,'owner:enumerateSubjectData') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackPlan' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-097.v1','TrackPlan',g.target_id,'owner:evaluateRetentionRequirement') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackPlan' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-098.v1','TrackPlan',g.target_id,'owner:anonymizePersonalFields') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackPlan' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-109.v1','TrackPlan',g.target_id,'owner:snapshotExternalDecision') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackPlan' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-119.v1','TrackPlan',g.target_id,'owner:applyTemporaryFeatureGrant') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackPlan' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-123.v1','TrackPlan',g.target_id,'owner:validateOwnedTargetReference') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackEntitlementDefinition' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-003.v1','TrackEntitlementDefinition',g.target_id,'owner:queryOwnerFacts') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackEntitlementDefinition' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-005.v1','TrackEntitlementDefinition',g.target_id,'owner:resolveEntitlement') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackEntitlementDefinition' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-006.v1','TrackEntitlementDefinition',g.target_id,'owner:consumeMeteredEntitlement') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackEntitlementDefinition' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-015.v1','TrackEntitlementDefinition',g.target_id,'owner:returnDecisionResult') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackEntitlementDefinition' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-031.v1','TrackEntitlementDefinition',g.target_id,'owner:appendDomainLifecycleEvent') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackEntitlementDefinition' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-043.v1','TrackEntitlementDefinition',g.target_id,'owner:resolveNotificationRecipients') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackEntitlementDefinition' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-053.v1','TrackEntitlementDefinition',g.target_id,'owner:transitionLifecycleState') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackEntitlementDefinition' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-060.v1','TrackEntitlementDefinition',g.target_id,'owner:deduplicateProviderEvent') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackEntitlementDefinition' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-061.v1','TrackEntitlementDefinition',g.target_id,'owner:translateProviderStatus') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackEntitlementDefinition' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-062.v1','TrackEntitlementDefinition',g.target_id,'owner:reconcileProviderState') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackEntitlementDefinition' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-063.v1','TrackEntitlementDefinition',g.target_id,'owner:captureProviderSnapshot') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackEntitlementDefinition' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-064.v1','TrackEntitlementDefinition',g.target_id,'owner:authorizeExternalProviderConnection') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackEntitlementDefinition' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-070.v1','TrackEntitlementDefinition',g.target_id,'owner:deleteProviderResource') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackEntitlementDefinition' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-080.v1','TrackEntitlementDefinition',g.target_id,'owner:manageVersionedRules') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackEntitlementDefinition' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-095.v1','TrackEntitlementDefinition',g.target_id,'owner:executePrivacyInstruction') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackEntitlementDefinition' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-096.v1','TrackEntitlementDefinition',g.target_id,'owner:enumerateSubjectData') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackEntitlementDefinition' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-097.v1','TrackEntitlementDefinition',g.target_id,'owner:evaluateRetentionRequirement') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackEntitlementDefinition' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-098.v1','TrackEntitlementDefinition',g.target_id,'owner:anonymizePersonalFields') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackEntitlementDefinition' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-109.v1','TrackEntitlementDefinition',g.target_id,'owner:snapshotExternalDecision') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackEntitlementDefinition' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-119.v1','TrackEntitlementDefinition',g.target_id,'owner:applyTemporaryFeatureGrant') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackEntitlementDefinition' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-123.v1','TrackEntitlementDefinition',g.target_id,'owner:validateOwnedTargetReference') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackPlanEntitlement' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-003.v1','TrackPlanEntitlement',g.target_id,'owner:queryOwnerFacts') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackPlanEntitlement' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-005.v1','TrackPlanEntitlement',g.target_id,'owner:resolveEntitlement') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackPlanEntitlement' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-006.v1','TrackPlanEntitlement',g.target_id,'owner:consumeMeteredEntitlement') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackPlanEntitlement' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-015.v1','TrackPlanEntitlement',g.target_id,'owner:returnDecisionResult') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackPlanEntitlement' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-031.v1','TrackPlanEntitlement',g.target_id,'owner:appendDomainLifecycleEvent') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackPlanEntitlement' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-043.v1','TrackPlanEntitlement',g.target_id,'owner:resolveNotificationRecipients') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackPlanEntitlement' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-053.v1','TrackPlanEntitlement',g.target_id,'owner:transitionLifecycleState') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackPlanEntitlement' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-060.v1','TrackPlanEntitlement',g.target_id,'owner:deduplicateProviderEvent') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackPlanEntitlement' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-061.v1','TrackPlanEntitlement',g.target_id,'owner:translateProviderStatus') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackPlanEntitlement' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-062.v1','TrackPlanEntitlement',g.target_id,'owner:reconcileProviderState') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackPlanEntitlement' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-063.v1','TrackPlanEntitlement',g.target_id,'owner:captureProviderSnapshot') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackPlanEntitlement' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-064.v1','TrackPlanEntitlement',g.target_id,'owner:authorizeExternalProviderConnection') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackPlanEntitlement' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-070.v1','TrackPlanEntitlement',g.target_id,'owner:deleteProviderResource') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackPlanEntitlement' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-080.v1','TrackPlanEntitlement',g.target_id,'owner:manageVersionedRules') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackPlanEntitlement' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-095.v1','TrackPlanEntitlement',g.target_id,'owner:executePrivacyInstruction') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackPlanEntitlement' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-096.v1','TrackPlanEntitlement',g.target_id,'owner:enumerateSubjectData') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackPlanEntitlement' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-097.v1','TrackPlanEntitlement',g.target_id,'owner:evaluateRetentionRequirement') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackPlanEntitlement' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-098.v1','TrackPlanEntitlement',g.target_id,'owner:anonymizePersonalFields') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackPlanEntitlement' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-109.v1','TrackPlanEntitlement',g.target_id,'owner:snapshotExternalDecision') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackPlanEntitlement' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-119.v1','TrackPlanEntitlement',g.target_id,'owner:applyTemporaryFeatureGrant') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackPlanEntitlement' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-123.v1','TrackPlanEntitlement',g.target_id,'owner:validateOwnedTargetReference') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackSubscription' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-003.v1','TrackSubscription',g.target_id,'owner:queryOwnerFacts') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackSubscription' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-005.v1','TrackSubscription',g.target_id,'owner:resolveEntitlement') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackSubscription' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-006.v1','TrackSubscription',g.target_id,'owner:consumeMeteredEntitlement') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackSubscription' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-015.v1','TrackSubscription',g.target_id,'owner:returnDecisionResult') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackSubscription' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-031.v1','TrackSubscription',g.target_id,'owner:appendDomainLifecycleEvent') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackSubscription' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-043.v1','TrackSubscription',g.target_id,'owner:resolveNotificationRecipients') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackSubscription' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-053.v1','TrackSubscription',g.target_id,'owner:transitionLifecycleState') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackSubscription' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-060.v1','TrackSubscription',g.target_id,'owner:deduplicateProviderEvent') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackSubscription' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-061.v1','TrackSubscription',g.target_id,'owner:translateProviderStatus') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackSubscription' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-062.v1','TrackSubscription',g.target_id,'owner:reconcileProviderState') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackSubscription' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-063.v1','TrackSubscription',g.target_id,'owner:captureProviderSnapshot') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackSubscription' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-064.v1','TrackSubscription',g.target_id,'owner:authorizeExternalProviderConnection') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackSubscription' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-070.v1','TrackSubscription',g.target_id,'owner:deleteProviderResource') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackSubscription' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-080.v1','TrackSubscription',g.target_id,'owner:manageVersionedRules') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackSubscription' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-095.v1','TrackSubscription',g.target_id,'owner:executePrivacyInstruction') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackSubscription' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-096.v1','TrackSubscription',g.target_id,'owner:enumerateSubjectData') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackSubscription' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-097.v1','TrackSubscription',g.target_id,'owner:evaluateRetentionRequirement') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackSubscription' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-098.v1','TrackSubscription',g.target_id,'owner:anonymizePersonalFields') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackSubscription' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-109.v1','TrackSubscription',g.target_id,'owner:snapshotExternalDecision') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackSubscription' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-119.v1','TrackSubscription',g.target_id,'owner:applyTemporaryFeatureGrant') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackSubscription' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-123.v1','TrackSubscription',g.target_id,'owner:validateOwnedTargetReference') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackEntitlementGrant' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-003.v1','TrackEntitlementGrant',g.target_id,'owner:queryOwnerFacts') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackEntitlementGrant' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-005.v1','TrackEntitlementGrant',g.target_id,'owner:resolveEntitlement') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackEntitlementGrant' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-006.v1','TrackEntitlementGrant',g.target_id,'owner:consumeMeteredEntitlement') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackEntitlementGrant' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-015.v1','TrackEntitlementGrant',g.target_id,'owner:returnDecisionResult') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackEntitlementGrant' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-031.v1','TrackEntitlementGrant',g.target_id,'owner:appendDomainLifecycleEvent') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackEntitlementGrant' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-043.v1','TrackEntitlementGrant',g.target_id,'owner:resolveNotificationRecipients') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackEntitlementGrant' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-053.v1','TrackEntitlementGrant',g.target_id,'owner:transitionLifecycleState') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackEntitlementGrant' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-060.v1','TrackEntitlementGrant',g.target_id,'owner:deduplicateProviderEvent') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackEntitlementGrant' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-061.v1','TrackEntitlementGrant',g.target_id,'owner:translateProviderStatus') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackEntitlementGrant' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-062.v1','TrackEntitlementGrant',g.target_id,'owner:reconcileProviderState') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackEntitlementGrant' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-063.v1','TrackEntitlementGrant',g.target_id,'owner:captureProviderSnapshot') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackEntitlementGrant' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-064.v1','TrackEntitlementGrant',g.target_id,'owner:authorizeExternalProviderConnection') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackEntitlementGrant' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-070.v1','TrackEntitlementGrant',g.target_id,'owner:deleteProviderResource') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackEntitlementGrant' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-080.v1','TrackEntitlementGrant',g.target_id,'owner:manageVersionedRules') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackEntitlementGrant' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-095.v1','TrackEntitlementGrant',g.target_id,'owner:executePrivacyInstruction') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackEntitlementGrant' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-096.v1','TrackEntitlementGrant',g.target_id,'owner:enumerateSubjectData') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackEntitlementGrant' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-097.v1','TrackEntitlementGrant',g.target_id,'owner:evaluateRetentionRequirement') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackEntitlementGrant' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-098.v1','TrackEntitlementGrant',g.target_id,'owner:anonymizePersonalFields') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackEntitlementGrant' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-109.v1','TrackEntitlementGrant',g.target_id,'owner:snapshotExternalDecision') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackEntitlementGrant' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-119.v1','TrackEntitlementGrant',g.target_id,'owner:applyTemporaryFeatureGrant') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackEntitlementGrant' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-123.v1','TrackEntitlementGrant',g.target_id,'owner:validateOwnedTargetReference') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackUsageEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-003.v1','TrackUsageEvent',g.target_id,'owner:queryOwnerFacts') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackUsageEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-005.v1','TrackUsageEvent',g.target_id,'owner:resolveEntitlement') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackUsageEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-006.v1','TrackUsageEvent',g.target_id,'owner:consumeMeteredEntitlement') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackUsageEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-015.v1','TrackUsageEvent',g.target_id,'owner:returnDecisionResult') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackUsageEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-031.v1','TrackUsageEvent',g.target_id,'owner:appendDomainLifecycleEvent') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackUsageEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-043.v1','TrackUsageEvent',g.target_id,'owner:resolveNotificationRecipients') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackUsageEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-053.v1','TrackUsageEvent',g.target_id,'owner:transitionLifecycleState') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackUsageEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-060.v1','TrackUsageEvent',g.target_id,'owner:deduplicateProviderEvent') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackUsageEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-061.v1','TrackUsageEvent',g.target_id,'owner:translateProviderStatus') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackUsageEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-062.v1','TrackUsageEvent',g.target_id,'owner:reconcileProviderState') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackUsageEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-063.v1','TrackUsageEvent',g.target_id,'owner:captureProviderSnapshot') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackUsageEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-064.v1','TrackUsageEvent',g.target_id,'owner:authorizeExternalProviderConnection') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackUsageEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-070.v1','TrackUsageEvent',g.target_id,'owner:deleteProviderResource') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackUsageEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-080.v1','TrackUsageEvent',g.target_id,'owner:manageVersionedRules') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackUsageEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-095.v1','TrackUsageEvent',g.target_id,'owner:executePrivacyInstruction') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackUsageEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-096.v1','TrackUsageEvent',g.target_id,'owner:enumerateSubjectData') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackUsageEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-097.v1','TrackUsageEvent',g.target_id,'owner:evaluateRetentionRequirement') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackUsageEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-098.v1','TrackUsageEvent',g.target_id,'owner:anonymizePersonalFields') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackUsageEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-109.v1','TrackUsageEvent',g.target_id,'owner:snapshotExternalDecision') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackUsageEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-119.v1','TrackUsageEvent',g.target_id,'owner:applyTemporaryFeatureGrant') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackUsageEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-123.v1','TrackUsageEvent',g.target_id,'owner:validateOwnedTargetReference') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackUsageCounter' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-003.v1','TrackUsageCounter',g.target_id,'owner:queryOwnerFacts') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackUsageCounter' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-005.v1','TrackUsageCounter',g.target_id,'owner:resolveEntitlement') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackUsageCounter' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-006.v1','TrackUsageCounter',g.target_id,'owner:consumeMeteredEntitlement') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackUsageCounter' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-015.v1','TrackUsageCounter',g.target_id,'owner:returnDecisionResult') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackUsageCounter' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-031.v1','TrackUsageCounter',g.target_id,'owner:appendDomainLifecycleEvent') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackUsageCounter' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-043.v1','TrackUsageCounter',g.target_id,'owner:resolveNotificationRecipients') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackUsageCounter' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-053.v1','TrackUsageCounter',g.target_id,'owner:transitionLifecycleState') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackUsageCounter' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-060.v1','TrackUsageCounter',g.target_id,'owner:deduplicateProviderEvent') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackUsageCounter' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-061.v1','TrackUsageCounter',g.target_id,'owner:translateProviderStatus') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackUsageCounter' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-062.v1','TrackUsageCounter',g.target_id,'owner:reconcileProviderState') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackUsageCounter' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-063.v1','TrackUsageCounter',g.target_id,'owner:captureProviderSnapshot') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackUsageCounter' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-064.v1','TrackUsageCounter',g.target_id,'owner:authorizeExternalProviderConnection') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackUsageCounter' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-070.v1','TrackUsageCounter',g.target_id,'owner:deleteProviderResource') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackUsageCounter' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-080.v1','TrackUsageCounter',g.target_id,'owner:manageVersionedRules') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackUsageCounter' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-095.v1','TrackUsageCounter',g.target_id,'owner:executePrivacyInstruction') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackUsageCounter' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-096.v1','TrackUsageCounter',g.target_id,'owner:enumerateSubjectData') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackUsageCounter' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-097.v1','TrackUsageCounter',g.target_id,'owner:evaluateRetentionRequirement') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackUsageCounter' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-098.v1','TrackUsageCounter',g.target_id,'owner:anonymizePersonalFields') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackUsageCounter' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-109.v1','TrackUsageCounter',g.target_id,'owner:snapshotExternalDecision') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackUsageCounter' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-119.v1','TrackUsageCounter',g.target_id,'owner:applyTemporaryFeatureGrant') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackUsageCounter' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-123.v1','TrackUsageCounter',g.target_id,'owner:validateOwnedTargetReference') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackSubscriptionEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-003.v1','TrackSubscriptionEvent',g.target_id,'owner:queryOwnerFacts') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackSubscriptionEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-005.v1','TrackSubscriptionEvent',g.target_id,'owner:resolveEntitlement') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackSubscriptionEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-006.v1','TrackSubscriptionEvent',g.target_id,'owner:consumeMeteredEntitlement') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackSubscriptionEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-015.v1','TrackSubscriptionEvent',g.target_id,'owner:returnDecisionResult') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackSubscriptionEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-031.v1','TrackSubscriptionEvent',g.target_id,'owner:appendDomainLifecycleEvent') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackSubscriptionEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-043.v1','TrackSubscriptionEvent',g.target_id,'owner:resolveNotificationRecipients') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackSubscriptionEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-053.v1','TrackSubscriptionEvent',g.target_id,'owner:transitionLifecycleState') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackSubscriptionEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-060.v1','TrackSubscriptionEvent',g.target_id,'owner:deduplicateProviderEvent') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackSubscriptionEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-061.v1','TrackSubscriptionEvent',g.target_id,'owner:translateProviderStatus') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackSubscriptionEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-062.v1','TrackSubscriptionEvent',g.target_id,'owner:reconcileProviderState') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackSubscriptionEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-063.v1','TrackSubscriptionEvent',g.target_id,'owner:captureProviderSnapshot') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackSubscriptionEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-064.v1','TrackSubscriptionEvent',g.target_id,'owner:authorizeExternalProviderConnection') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackSubscriptionEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-070.v1','TrackSubscriptionEvent',g.target_id,'owner:deleteProviderResource') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackSubscriptionEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-080.v1','TrackSubscriptionEvent',g.target_id,'owner:manageVersionedRules') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackSubscriptionEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-095.v1','TrackSubscriptionEvent',g.target_id,'owner:executePrivacyInstruction') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackSubscriptionEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-096.v1','TrackSubscriptionEvent',g.target_id,'owner:enumerateSubjectData') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackSubscriptionEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-097.v1','TrackSubscriptionEvent',g.target_id,'owner:evaluateRetentionRequirement') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackSubscriptionEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-098.v1','TrackSubscriptionEvent',g.target_id,'owner:anonymizePersonalFields') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackSubscriptionEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-109.v1','TrackSubscriptionEvent',g.target_id,'owner:snapshotExternalDecision') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT','UPDATE']::text[]) AND (model_name='TrackSubscriptionEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-119.v1','TrackSubscriptionEvent',g.target_id,'owner:applyTemporaryFeatureGrant') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='TrackSubscriptionEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('track_subscription_entitlement','SH-123.v1','TrackSubscriptionEvent',g.target_id,'owner:validateOwnedTargetReference') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='CustomerProfile' OR model_name='CustomerProfileLifecycleEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('customer_buyer_profile','SH-004.v1','CustomerProfile',g.target_id,'resolve') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT']::text[]) AND (model_name='CustomerProfile' OR model_name='CustomerProfileLifecycleEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('customer_buyer_profile','SH-004.v1','CustomerProfile',g.target_id,'provision') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT']::text[]) AND (model_name='CustomerProfile' OR model_name='CustomerProfileLifecycleEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('customer_buyer_profile','SH-114.v1','CustomerProfile',g.target_id,'provision') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','UPDATE']::text[]) AND (model_name='CustomerProfile' OR model_name='CustomerProfileLifecycleEvent' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('customer_buyer_profile','updateCustomerProfileIdentity.v1','CustomerProfile',g.target_id,'profile_update') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='ConsentContentRevision' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('consent_disclosure','SH-009.v1','ConsentContentRevision',g.target_id,'owner:resolveActiveConsentVersion') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='ConsentPresentation' OR (verb='SELECT' AND model_name='ConsentContentRevision' AND 'ConsentPresentation/'||g.target_id||'/contentRevision/'||row_key=ANY(g.allowed_fields)) OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('consent_disclosure','SH-010.v1','ConsentPresentation',g.target_id,'owner:presentStandaloneConsent') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT']::text[]) AND (model_name='ConsentContentRevision' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('consent_disclosure','publishConsentVersion.v1','ConsentContentRevision',g.target_id,'consent.publish_version') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT']::text[]) AND (model_name='ConsentPresentation' OR (verb='SELECT' AND model_name='ConsentContentRevision' AND 'ConsentPresentation/'||g.target_id||'/contentRevision/'||row_key=ANY(g.allowed_fields)) OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('consent_disclosure','recordConsentPresentation.v1','ConsentPresentation',g.target_id,'consent.record_presentation') THEN RETURN true; END IF;
IF verb=ANY(ARRAY['SELECT','INSERT']::text[]) AND (model_name='ConsentDisposition' OR (verb='SELECT' AND model_name='ConsentPresentation' AND 'ConsentDisposition/'||g.target_id||'/presentation/'||row_key=ANY(g.allowed_fields)) OR (verb='SELECT' AND model_name='ConsentLog' AND 'ConsentDisposition/'||g.target_id||'/proof/'||row_key=ANY(g.allowed_fields)) OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('consent_disclosure','recordConsentDisposition.v1','ConsentDisposition',g.target_id,'consent.record_disposition') THEN RETURN true; END IF;
IF model_name IN ('RuntimeWorkItem','RuntimeAttempt','RuntimeOutboxMessage','RuntimeCommandReceipt','RuntimeEffectReceipt','RuntimeInboxReceipt','OwnerMutationEvidence','TrackPlan','TrackEntitlementDefinition','TrackPlanEntitlement','TrackSubscription','TrackEntitlementGrant','TrackBaseSelection','TrackSubscriptionEvent','TrackEnrollmentReceipt') AND platform_private.context_allows('track_subscription_entitlement','assignDefaultFreeTrack.v1','RuntimeWorkItem',g.target_id,'default_free_enrollment') THEN RETURN true; END IF;
IF model_name='RuntimeWorkItem' AND platform_private.context_allows('platform_integration_owner','runtime.claim_work.v1','RuntimeWorkItem',row_key,'work.claim') THEN RETURN true; END IF;
IF model_name='RuntimeWorkItem' AND platform_private.context_allows('platform_integration_owner','runtime.renew_work.v1','RuntimeWorkItem',row_key,'work.renew') THEN RETURN true; END IF;
IF model_name='RuntimeWorkItem' AND platform_private.context_allows('platform_integration_owner','runtime.schedule_work.v1','RuntimeWorkItem',row_key,'work.schedule') THEN RETURN true; END IF;
IF model_name IN ('RuntimeReservation','RuntimeEffectReceipt','RuntimeCommandReceipt') AND platform_private.context_allows(g.owner_module_id,'runtime.reservation.v1','RuntimeReservation',g.target_id,'reservation') THEN RETURN true; END IF;
RETURN false; END;
$wa$;

CREATE FUNCTION platform_private.row_allowed(owner_id text, model_name text, row_key text, verb text, field_names text[], row_revision text DEFAULT NULL, row_transaction text DEFAULT NULL) RETURNS boolean
LANGUAGE plpgsql VOLATILE SECURITY DEFINER
SET search_path = pg_catalog
AS $wa$
DECLARE g platform.database_action_grant; f text; authorized_revision text:=row_revision;
BEGIN
 g:=platform_private.bound_grant(true);
 IF g.id IS NULL OR verb NOT IN ('SELECT','INSERT','UPDATE') THEN RETURN false; END IF;
 IF NOT platform_private.protected_scope(model_name,row_key,verb) THEN RETURN false; END IF;
 IF g.owner_module_id<>owner_id AND NOT (owner_id='platform_integration_owner'
  AND model_name IN ('RuntimeWorkItem','RuntimeAttempt'))
  AND NOT (session_user::text='wa_worker' AND g.owner_module_id='track_subscription_entitlement' AND model_name='RuntimeOutboxMessage') THEN RETURN false; END IF;
 -- SQL transport convention: issuer-authorized finite model/key/verb/field tokens.
 -- No wildcard. Every role-visible SELECT column must be authorized together.
 FOREACH f IN ARRAY field_names LOOP
  IF NOT COALESCE(model_name||'/'||row_key||'/'||verb||'/'||f = ANY(g.allowed_fields),false) THEN RETURN false; END IF;
 END LOOP;
 IF row_revision IS NOT NULL AND row_transaction=pg_current_xact_id()::text AND row_revision::bigint>0
  AND NOT COALESCE(model_name||'/'||row_key||'/revision/'||row_revision=ANY(g.allowed_fields),false)
  AND COALESCE(model_name||'/'||row_key||'/revision/'||(row_revision::bigint-1)::text=ANY(g.allowed_fields),false)
 THEN authorized_revision:=(row_revision::bigint-1)::text; END IF;
 IF row_revision IS NOT NULL AND NOT COALESCE
  (model_name||'/'||row_key||'/revision/'||authorized_revision = ANY(g.allowed_fields),false) THEN RETURN false; END IF;
 IF row_revision IS NOT NULL AND g.target_kind=model_name AND g.target_id=row_key
  AND g.source_generation::text<>authorized_revision THEN RETURN false; END IF;
 RETURN true;
END;
$wa$;

CREATE FUNCTION platform_private.context_subject_owner(subject_user_id uuid, source_owner text) RETURNS boolean
LANGUAGE plpgsql VOLATILE SECURITY DEFINER
SET search_path = pg_catalog
AS $wa$
DECLARE g platform.database_action_grant;
BEGIN
 g:=platform_private.bound_grant(true);
 RETURN COALESCE(g.principal_user_id=subject_user_id AND g.owner_module_id=source_owner,false);
END;
$wa$;

CREATE FUNCTION platform_private.command_context_allows(source_owner text, operation_name text, subject_scope text) RETURNS boolean
LANGUAGE plpgsql VOLATILE SECURITY DEFINER
SET search_path = pg_catalog
AS $wa$
DECLARE g platform.database_action_grant;
BEGIN
 g:=platform_private.bound_grant(true);
 IF g.id IS NULL OR g.owner_module_id<>source_owner THEN RETURN false; END IF;
 IF session_user::text='wa_worker' AND g.action='assignDefaultFreeTrack.v1' THEN RETURN operation_name=g.action; END IF;
 RETURN operation_name=g.action AND subject_scope=g.target_kind||':'||g.target_id;
END;
$wa$;

CREATE FUNCTION platform_private.global_context_registered(action_owner text, action_name text, context_owner text, context_kind text) RETURNS boolean
LANGUAGE sql IMMUTABLE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
SELECT false;
$wa$;

CREATE FUNCTION platform_private.context_subject(subject_user_id uuid) RETURNS boolean
LANGUAGE plpgsql VOLATILE SECURITY DEFINER
SET search_path = pg_catalog
AS $wa$
DECLARE g platform.database_action_grant;
BEGIN
 g:=platform_private.bound_grant(true);
 RETURN COALESCE(g.principal_user_id=subject_user_id AND g.owner_module_id='consent_disclosure',false);
END;
$wa$;

CREATE FUNCTION platform_private.grant_guard() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'grant delete denied' USING ERRCODE='42501'; END IF;
 IF TG_OP='UPDATE' THEN
  IF (to_jsonb(NEW)-ARRAY['revoked_at','mutation_transaction_id']) IS DISTINCT FROM
     (to_jsonb(OLD)-ARRAY['revoked_at','mutation_transaction_id']) OR OLD.revoked_at IS NOT NULL
     OR NEW.revoked_at IS NULL THEN RAISE EXCEPTION 'immutable grant'; END IF;
  PERFORM pg_advisory_xact_lock(hashtextextended('grant:'||OLD.token_hash::text,0));
  NEW.revoked_at:=clock_timestamp();
 ELSE
  IF NEW.issuer_service<>session_user::text OR NEW.database_login_role NOT IN ('wa_app_runtime','wa_worker')
   OR (NEW.principal_user_id IS NULL)=(NEW.service_principal IS NULL)
   OR NEW.backend_pid<=0 OR NEW.transaction_id !~ '^[0-9]+$'
   OR NEW.token_hash !~ '^[0-9a-f]{64}$' OR NEW.expires_at<=clock_timestamp()
   OR NEW.security_generation<0 OR NEW.source_generation<0 OR cardinality(NEW.allowed_fields)=0
   OR array_position(NEW.allowed_fields,NULL) IS NOT NULL OR array_ndims(NEW.allowed_fields)<>1
   OR NEW.revoked_at IS NOT NULL OR NEW.policy_version='' OR NEW.action='' OR NEW.purpose=''
   OR NEW.target_kind='' OR NEW.target_id='' THEN RAISE EXCEPTION 'invalid grant'; END IF;
  NEW.created_at:=clock_timestamp();
 END IF;
 NEW.mutation_transaction_id:=pg_current_xact_id()::text;
 RETURN NEW;
END;
$wa$;

CREATE TRIGGER grant_guard BEFORE INSERT OR UPDATE OR DELETE ON platform.database_action_grant FOR EACH ROW EXECUTE FUNCTION platform_private.grant_guard();

-- SQL-01/02: ConsentLog
ALTER TABLE "app"."consent_logs" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "app"."consent_logs" FORCE ROW LEVEL SECURITY;

GRANT INSERT ("id","user_id","type","version","accepted_at","ip_hash","user_agent","acceptance_key","fingerprint","action_owner","action","context_kind","context_id","context_owner","presentation_hash","content_revision_id","presentation_id") ON "app"."consent_logs" TO wa_app_runtime;

GRANT SELECT ("id","user_id","type","version","accepted_at","ip_hash","user_agent","created_at","acceptance_key","fingerprint","action_owner","action","context_kind","context_id","context_owner","presentation_hash","content_revision_id","presentation_id","mutation_transaction_id") ON "app"."consent_logs" TO wa_app_runtime;

-- SQL-01/02: PrivacyRequest
ALTER TABLE "app"."privacy_requests" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "app"."privacy_requests" FORCE ROW LEVEL SECURITY;

GRANT INSERT ("id","user_id","type","status","requested_at","verified_at","due_at","completed_at","rejection_reason","admin_note","updated_at","revision","privacy_generation","instruction_generation") ON "app"."privacy_requests" TO wa_app_runtime;

GRANT SELECT ("id","user_id","type","status","requested_at","verified_at","due_at","completed_at","rejection_reason","admin_note","created_at","updated_at","revision","privacy_generation","instruction_generation","mutation_transaction_id") ON "app"."privacy_requests" TO wa_app_runtime;

GRANT UPDATE ("type","status","requested_at","verified_at","due_at","completed_at","rejection_reason","admin_note","updated_at","revision","privacy_generation","instruction_generation") ON "app"."privacy_requests" TO wa_app_runtime;

-- SQL-01/02: AgeGateAttempt
ALTER TABLE "app"."age_gate_attempts" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "app"."age_gate_attempts" FORCE ROW LEVEL SECURITY;

GRANT INSERT ("id","user_id","ip_hash","device_hash","region","result","birth_year","age_band","blocked_until") ON "app"."age_gate_attempts" TO wa_app_runtime;

GRANT SELECT ("id","user_id","ip_hash","device_hash","region","result","birth_year","age_band","blocked_until","created_at","mutation_transaction_id") ON "app"."age_gate_attempts" TO wa_app_runtime;

-- SQL-01/02: AgeGateBlock
ALTER TABLE "app"."age_gate_blocks" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "app"."age_gate_blocks" FORCE ROW LEVEL SECURITY;

GRANT INSERT ("id","ip_hash","device_hash","reason","blocked_until") ON "app"."age_gate_blocks" TO wa_app_runtime;

GRANT SELECT ("id","ip_hash","device_hash","reason","blocked_until","created_at","mutation_transaction_id") ON "app"."age_gate_blocks" TO wa_app_runtime;

-- SQL-01/02: AccessAuditLog
ALTER TABLE "app"."access_audit_logs" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "app"."access_audit_logs" FORCE ROW LEVEL SECURITY;

GRANT INSERT ("id","actor_user_id","target_type","target_id","action","sensitivity","access_decision","request_id","ip_hash","user_agent","previous_hash","entry_hash") ON "app"."access_audit_logs" TO wa_app_runtime;

GRANT SELECT ("id","actor_user_id","target_type","target_id","action","sensitivity","access_decision","request_id","ip_hash","user_agent","previous_hash","entry_hash","created_at","mutation_transaction_id") ON "app"."access_audit_logs" TO wa_app_runtime;

-- SQL-01/02: User
ALTER TABLE "app"."users" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "app"."users" FORCE ROW LEVEL SECURITY;

GRANT INSERT ("id","email","handle","display_name","avatar_url","bio","city","state","country","is_public","updated_at","privacy_erased_at","privacy_erasure_status","revision","privacy_generation") ON "app"."users" TO wa_app_runtime;

GRANT SELECT ("id","email","handle","display_name","avatar_url","bio","city","state","country","is_public","created_at","updated_at","privacy_erased_at","privacy_erasure_status","revision","privacy_generation","mutation_transaction_id") ON "app"."users" TO wa_app_runtime;

GRANT UPDATE ("email","handle","display_name","avatar_url","bio","city","state","country","is_public","updated_at","privacy_erased_at","privacy_erasure_status","revision","privacy_generation") ON "app"."users" TO wa_app_runtime;

-- SQL-01/02: UserRole
ALTER TABLE "app"."user_roles" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "app"."user_roles" FORCE ROW LEVEL SECURITY;

GRANT INSERT ("user_id","role","revision") ON "app"."user_roles" TO wa_app_runtime;

GRANT SELECT ("user_id","role","created_at","revision","mutation_transaction_id") ON "app"."user_roles" TO wa_app_runtime;

GRANT UPDATE ("revision") ON "app"."user_roles" TO wa_app_runtime;

-- SQL-01/02: ProfessionalProfile
ALTER TABLE "app"."professional_profiles" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "app"."professional_profiles" FORCE ROW LEVEL SECURITY;

GRANT SELECT ("id","user_id","slug","headline","bio","website_url","city","state","country","status","rating_average","rating_count","stripe_account_id","stripe_ready","onboarding_complete_at","default_currency","created_at","updated_at","suspended_for_moderation_at","trust_score","verified_at","verification_expires_at","revision","privacy_generation","mutation_transaction_id") ON "app"."professional_profiles" TO wa_app_runtime;

-- SQL-01/02: CustomerProfile
ALTER TABLE "app"."customer_profiles" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "app"."customer_profiles" FORCE ROW LEVEL SECURITY;

GRANT INSERT ("id","user_id","status","display_name","avatar_media_id","city","state","country","updated_at","archived_at","revision","privacy_generation") ON "app"."customer_profiles" TO wa_app_runtime;

GRANT SELECT ("id","user_id","status","display_name","avatar_media_id","city","state","country","created_at","updated_at","archived_at","revision","privacy_generation","mutation_transaction_id") ON "app"."customer_profiles" TO wa_app_runtime;

GRANT UPDATE ("status","display_name","avatar_media_id","city","state","country","updated_at","archived_at","revision","privacy_generation") ON "app"."customer_profiles" TO wa_app_runtime;

-- SQL-01/02: CandidateProfile
ALTER TABLE "app"."candidate_profiles" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "app"."candidate_profiles" FORCE ROW LEVEL SECURITY;

GRANT SELECT ("id","user_id","headline","portfolio_url","availability","city","state","country","status","is_visible","created_at","updated_at","trust_score","verified_at","verification_expires_at","revision","privacy_generation","discovery_preference_revision","discovery_enabled_at","mutation_transaction_id") ON "app"."candidate_profiles" TO wa_app_runtime;

-- SQL-01/02: AuditEvent
ALTER TABLE "app"."audit_events" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "app"."audit_events" FORCE ROW LEVEL SECURITY;

GRANT INSERT ("id","actor_user_id","entity_type","entity_id","action","metadata") ON "app"."audit_events" TO wa_app_runtime;

GRANT SELECT ("id","actor_user_id","entity_type","entity_id","action","metadata","created_at","mutation_transaction_id") ON "app"."audit_events" TO wa_app_runtime;

-- SQL-01/02: UserSecurityProfile
ALTER TABLE "app"."user_security_profiles" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "app"."user_security_profiles" FORCE ROW LEVEL SECURITY;

GRANT INSERT ("id","user_id","security_tier","phone_number_encrypted","phone_number_hash","phone_verified_at","phone_last_changed_at","passkeys_enabled","sms_mfa_enabled","backup_password_configured","sensitive_action_mfa_required","last_step_up_at","last_sensitive_action_at","locked_until","lock_reason","updated_at","revision","security_generation") ON "app"."user_security_profiles" TO wa_app_runtime;

GRANT SELECT ("id","user_id","security_tier","phone_number_encrypted","phone_number_hash","phone_verified_at","phone_last_changed_at","passkeys_enabled","sms_mfa_enabled","backup_password_configured","sensitive_action_mfa_required","last_step_up_at","last_sensitive_action_at","locked_until","lock_reason","created_at","updated_at","revision","security_generation","mutation_transaction_id") ON "app"."user_security_profiles" TO wa_app_runtime;

GRANT UPDATE ("security_tier","phone_number_encrypted","phone_number_hash","phone_verified_at","phone_last_changed_at","passkeys_enabled","sms_mfa_enabled","backup_password_configured","sensitive_action_mfa_required","last_step_up_at","last_sensitive_action_at","locked_until","lock_reason","updated_at","revision","security_generation") ON "app"."user_security_profiles" TO wa_app_runtime;

-- SQL-01/02: AuthProviderAccount
ALTER TABLE "app"."auth_provider_accounts" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "app"."auth_provider_accounts" FORCE ROW LEVEL SECURITY;

GRANT INSERT ("id","user_id","security_profile_id","provider_type","provider_user_id","provider_account_id","email","email_verified_at","status","linked_at","last_used_at","revoked_at","updated_at","revision") ON "app"."auth_provider_accounts" TO wa_app_runtime;

GRANT SELECT ("id","user_id","security_profile_id","provider_type","provider_user_id","provider_account_id","email","email_verified_at","status","linked_at","last_used_at","revoked_at","created_at","updated_at","revision","mutation_transaction_id") ON "app"."auth_provider_accounts" TO wa_app_runtime;

GRANT UPDATE ("provider_type","email","email_verified_at","status","linked_at","last_used_at","revoked_at","updated_at","revision") ON "app"."auth_provider_accounts" TO wa_app_runtime;

-- SQL-01/02: TrackPlan
ALTER TABLE "app"."track_plans" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "app"."track_plans" FORCE ROW LEVEL SECURITY;

GRANT INSERT ("id","track","key","name","status","billing_model","monthly_price_cents","currency","description","display_order","metadata","updated_at","revision","version","content_hash") ON "app"."track_plans" TO wa_app_runtime;

GRANT SELECT ("id","track","key","name","status","billing_model","monthly_price_cents","currency","description","display_order","metadata","created_at","updated_at","revision","version","content_hash","mutation_transaction_id") ON "app"."track_plans" TO wa_app_runtime;

GRANT UPDATE ("track","key","name","status","billing_model","monthly_price_cents","currency","description","display_order","metadata","updated_at","revision","version","content_hash") ON "app"."track_plans" TO wa_app_runtime;

GRANT SELECT ("id","track","key","status","billing_model","version","content_hash","revision") ON "app"."track_plans" TO wa_worker;

-- SQL-01/02: TrackEntitlementDefinition
ALTER TABLE "app"."track_entitlement_definitions" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "app"."track_entitlement_definitions" FORCE ROW LEVEL SECURITY;

GRANT INSERT ("id","key","label","description","value_type","track","is_active","updated_at","revision") ON "app"."track_entitlement_definitions" TO wa_app_runtime;

GRANT SELECT ("id","key","label","description","value_type","track","is_active","created_at","updated_at","revision","mutation_transaction_id") ON "app"."track_entitlement_definitions" TO wa_app_runtime;

GRANT UPDATE ("key","label","description","value_type","track","is_active","updated_at","revision") ON "app"."track_entitlement_definitions" TO wa_app_runtime;

GRANT SELECT ("id","key","value_type","track","is_active","revision") ON "app"."track_entitlement_definitions" TO wa_worker;

-- SQL-01/02: TrackPlanEntitlement
ALTER TABLE "app"."track_plan_entitlements" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "app"."track_plan_entitlements" FORCE ROW LEVEL SECURITY;

GRANT INSERT ("id","plan_id","entitlement_id","value_type","boolean_value","int_value","decimal_value","string_value","json_value","usage_period","updated_at","revision") ON "app"."track_plan_entitlements" TO wa_app_runtime;

GRANT SELECT ("id","plan_id","entitlement_id","value_type","boolean_value","int_value","decimal_value","string_value","json_value","usage_period","created_at","updated_at","revision","mutation_transaction_id") ON "app"."track_plan_entitlements" TO wa_app_runtime;

GRANT UPDATE ("value_type","boolean_value","int_value","decimal_value","string_value","json_value","usage_period","updated_at","revision") ON "app"."track_plan_entitlements" TO wa_app_runtime;

GRANT SELECT ("id","plan_id","entitlement_id","value_type","boolean_value","int_value","decimal_value","string_value","usage_period","revision") ON "app"."track_plan_entitlements" TO wa_worker;

-- SQL-01/02: TrackSubscription
ALTER TABLE "app"."track_subscriptions" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "app"."track_subscriptions" FORCE ROW LEVEL SECURITY;

GRANT INSERT ("id","user_id","plan_id","track","customer_profile_id","candidate_profile_id","professional_profile_id","status","provider","provider_customer_id","provider_subscription_id","provider_price_id","current_period_start","current_period_end","trial_ends_at","cancelled_at","ended_at","updated_at","revision") ON "app"."track_subscriptions" TO wa_app_runtime;

GRANT SELECT ("id","user_id","plan_id","track","customer_profile_id","candidate_profile_id","professional_profile_id","status","provider","provider_customer_id","provider_subscription_id","provider_price_id","current_period_start","current_period_end","trial_ends_at","cancelled_at","ended_at","created_at","updated_at","revision","mutation_transaction_id") ON "app"."track_subscriptions" TO wa_app_runtime;

GRANT UPDATE ("track","status","provider","current_period_start","current_period_end","trial_ends_at","cancelled_at","ended_at","updated_at","revision") ON "app"."track_subscriptions" TO wa_app_runtime;

GRANT INSERT ("id","user_id","plan_id","track","customer_profile_id","candidate_profile_id","professional_profile_id","status","provider") ON "app"."track_subscriptions" TO wa_worker;

GRANT SELECT ("id","user_id","plan_id","track","customer_profile_id","candidate_profile_id","professional_profile_id","status","provider","current_period_start","current_period_end","ended_at","revision") ON "app"."track_subscriptions" TO wa_worker;

-- SQL-01/02: TrackEntitlementGrant
ALTER TABLE "app"."track_entitlement_grants" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "app"."track_entitlement_grants" FORCE ROW LEVEL SECURITY;

GRANT INSERT ("id","user_id","subscription_id","entitlement_id","track","customer_profile_id","candidate_profile_id","professional_profile_id","status","value_type","boolean_value","int_value","decimal_value","string_value","json_value","starts_at","expires_at","revoked_at","revoke_reason","source_plan_id","source_event_id","updated_at","revision") ON "app"."track_entitlement_grants" TO wa_app_runtime;

GRANT SELECT ("id","user_id","subscription_id","entitlement_id","track","customer_profile_id","candidate_profile_id","professional_profile_id","status","value_type","boolean_value","int_value","decimal_value","string_value","json_value","starts_at","expires_at","revoked_at","revoke_reason","source_plan_id","source_event_id","created_at","updated_at","revision","mutation_transaction_id") ON "app"."track_entitlement_grants" TO wa_app_runtime;

GRANT UPDATE ("track","status","value_type","boolean_value","int_value","decimal_value","string_value","json_value","starts_at","expires_at","revoked_at","revoke_reason","updated_at","revision") ON "app"."track_entitlement_grants" TO wa_app_runtime;

GRANT INSERT ("id","user_id","subscription_id","entitlement_id","track","customer_profile_id","candidate_profile_id","professional_profile_id","status","value_type","boolean_value","int_value","decimal_value","string_value","starts_at","source_plan_id","source_event_id") ON "app"."track_entitlement_grants" TO wa_worker;

GRANT SELECT ("id","user_id","subscription_id","entitlement_id","track","customer_profile_id","candidate_profile_id","professional_profile_id","status","value_type","boolean_value","int_value","decimal_value","string_value","starts_at","expires_at","revoked_at","source_plan_id","source_event_id","revision") ON "app"."track_entitlement_grants" TO wa_worker;

-- SQL-01/02: TrackUsageEvent
ALTER TABLE "app"."track_usage_events" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "app"."track_usage_events" FORCE ROW LEVEL SECURITY;

GRANT INSERT ("id","user_id","subscription_id","entitlement_grant_id","entitlement_id","track","type","customer_profile_id","candidate_profile_id","professional_profile_id","target_type","target_id","quantity","occurred_at","metadata","semantic_effect_key","source_revision","source_owner","source_id","accepted_at","period_start","period_end","effect_receipt_id") ON "app"."track_usage_events" TO wa_app_runtime;

GRANT SELECT ("id","user_id","subscription_id","entitlement_grant_id","entitlement_id","track","type","customer_profile_id","candidate_profile_id","professional_profile_id","target_type","target_id","quantity","occurred_at","metadata","semantic_effect_key","source_revision","source_owner","source_id","accepted_at","period_start","period_end","effect_receipt_id","mutation_transaction_id") ON "app"."track_usage_events" TO wa_app_runtime;

-- SQL-01/02: TrackUsageCounter
ALTER TABLE "app"."track_usage_counters" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "app"."track_usage_counters" FORCE ROW LEVEL SECURITY;

GRANT INSERT ("id","user_id","subscription_id","entitlement_grant_id","entitlement_id","track","period","customer_profile_id","candidate_profile_id","professional_profile_id","period_start","period_end","used_quantity","limit_quantity","updated_at","revision","source_revision") ON "app"."track_usage_counters" TO wa_app_runtime;

GRANT SELECT ("id","user_id","subscription_id","entitlement_grant_id","entitlement_id","track","period","customer_profile_id","candidate_profile_id","professional_profile_id","period_start","period_end","used_quantity","limit_quantity","updated_at","created_at","revision","source_revision","mutation_transaction_id") ON "app"."track_usage_counters" TO wa_app_runtime;

GRANT UPDATE ("track","period","period_start","period_end","used_quantity","limit_quantity","updated_at","revision","source_revision") ON "app"."track_usage_counters" TO wa_app_runtime;

-- SQL-01/02: TrackSubscriptionEvent
ALTER TABLE "app"."track_subscription_events" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "app"."track_subscription_events" FORCE ROW LEVEL SECURITY;

GRANT INSERT ("id","subscription_id","plan_id","user_id","name","from_status","to_status","provider","provider_event_id","metadata") ON "app"."track_subscription_events" TO wa_app_runtime;

GRANT SELECT ("id","subscription_id","plan_id","user_id","name","from_status","to_status","provider","provider_event_id","metadata","created_at","mutation_transaction_id") ON "app"."track_subscription_events" TO wa_app_runtime;

GRANT INSERT ("id","subscription_id","plan_id","user_id","name","from_status","to_status","provider") ON "app"."track_subscription_events" TO wa_worker;

-- SQL-01/02: ConsentContentRevision
ALTER TABLE "app"."consent_content_revision" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "app"."consent_content_revision" FORCE ROW LEVEL SECURITY;

GRANT INSERT ("id","type","version","locale","jurisdiction_scope","content_text","content_hash","review_state","legal_approval_ref","effective_from","effective_until") ON "app"."consent_content_revision" TO wa_app_runtime;

GRANT SELECT ("id","type","version","locale","jurisdiction_scope","content_text","content_hash","review_state","legal_approval_ref","effective_from","effective_until","created_at","mutation_transaction_id") ON "app"."consent_content_revision" TO wa_app_runtime;

-- SQL-01/02: ConsentPresentation
ALTER TABLE "app"."consent_presentation" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "app"."consent_presentation" FORCE ROW LEVEL SECURITY;

GRANT INSERT ("id","content_revision_id","user_id","action_owner","action","render_version","rendered_text","rendered_hash","context_owner","context_kind","context_id") ON "app"."consent_presentation" TO wa_app_runtime;

GRANT SELECT ("id","content_revision_id","user_id","action_owner","action","render_version","rendered_text","rendered_hash","context_owner","context_kind","context_id","created_at","mutation_transaction_id") ON "app"."consent_presentation" TO wa_app_runtime;

-- SQL-01/02: ConsentDisposition
ALTER TABLE "app"."consent_disposition" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "app"."consent_disposition" FORCE ROW LEVEL SECURITY;

GRANT INSERT ("id","proof_id","user_id","presentation_id","kind","semantic_key","fingerprint") ON "app"."consent_disposition" TO wa_app_runtime;

GRANT SELECT ("id","proof_id","user_id","presentation_id","kind","semantic_key","fingerprint","created_at","mutation_transaction_id") ON "app"."consent_disposition" TO wa_app_runtime;

-- SQL-01/02: RuntimeCommandReceipt
ALTER TABLE "platform"."runtime_command_receipt" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "platform"."runtime_command_receipt" FORCE ROW LEVEL SECURITY;

GRANT INSERT ("id","owner_module_id","operation","subject_scope","semantic_key","fingerprint","state","source_revision","result_schema_id","result_schema_version","result_digest","result_body") ON "platform"."runtime_command_receipt" TO wa_app_runtime;

GRANT SELECT ("id","owner_module_id","operation","subject_scope","semantic_key","fingerprint","state","source_revision","result_schema_id","result_schema_version","result_digest","result_body","created_at","mutation_transaction_id") ON "platform"."runtime_command_receipt" TO wa_app_runtime;

GRANT UPDATE ("operation","subject_scope","semantic_key","fingerprint","state","source_revision","result_schema_version","result_digest","result_body") ON "platform"."runtime_command_receipt" TO wa_app_runtime;

GRANT INSERT ("id","owner_module_id","operation","subject_scope","semantic_key","fingerprint","state","source_revision","result_schema_id","result_schema_version","result_digest","result_body") ON "platform"."runtime_command_receipt" TO wa_worker;

GRANT SELECT ("id","owner_module_id","operation","subject_scope","semantic_key","fingerprint","state","source_revision","result_schema_id","result_schema_version","result_digest","result_body","created_at","mutation_transaction_id") ON "platform"."runtime_command_receipt" TO wa_worker;

GRANT UPDATE ("id","owner_module_id","operation","subject_scope","semantic_key","fingerprint","state","source_revision","result_schema_id","result_schema_version","result_digest","result_body","created_at","mutation_transaction_id") ON "platform"."runtime_command_receipt" TO wa_worker;

-- SQL-01/02: RuntimeOutboxMessage
ALTER TABLE "platform"."runtime_outbox_message" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "platform"."runtime_outbox_message" FORCE ROW LEVEL SECURITY;

GRANT INSERT ("id","command_receipt_id","kind","producer_owner","aggregate_kind","aggregate_id","source_revision","source_generation","ordinal","name","schema_version","payload_schema_id","payload_hash","payload","correlation_id","causation_id","correction_of_id","occurred_at","effective_at") ON "platform"."runtime_outbox_message" TO wa_app_runtime;

GRANT SELECT ("id","command_receipt_id","kind","producer_owner","aggregate_kind","aggregate_id","source_revision","source_generation","ordinal","name","schema_version","payload_schema_id","payload_hash","payload","correlation_id","causation_id","correction_of_id","occurred_at","effective_at","created_at","mutation_transaction_id") ON "platform"."runtime_outbox_message" TO wa_app_runtime;

GRANT INSERT ("id","command_receipt_id","kind","producer_owner","aggregate_kind","aggregate_id","source_revision","source_generation","ordinal","name","schema_version","payload_schema_id","payload_hash","payload","correlation_id","causation_id","correction_of_id","occurred_at","effective_at") ON "platform"."runtime_outbox_message" TO wa_worker;

GRANT SELECT ("id","command_receipt_id","kind","producer_owner","aggregate_kind","aggregate_id","source_revision","source_generation","ordinal","name","schema_version","payload_schema_id","payload_hash","payload","correlation_id","causation_id","correction_of_id","occurred_at","effective_at","created_at","mutation_transaction_id") ON "platform"."runtime_outbox_message" TO wa_worker;

-- SQL-01/02: RuntimeEffectReceipt
ALTER TABLE "platform"."runtime_effect_receipt" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "platform"."runtime_effect_receipt" FORCE ROW LEVEL SECURITY;

GRANT INSERT ("id","command_receipt_id","owner_module_id","operation","subject_scope","semantic_effect_key","fingerprint","state","source_revision","fence","result_schema_id","result_hash","committed_at") ON "platform"."runtime_effect_receipt" TO wa_app_runtime;

GRANT SELECT ("id","command_receipt_id","owner_module_id","operation","subject_scope","semantic_effect_key","fingerprint","state","source_revision","fence","result_schema_id","result_hash","committed_at","created_at","mutation_transaction_id") ON "platform"."runtime_effect_receipt" TO wa_app_runtime;

GRANT INSERT ("id","command_receipt_id","owner_module_id","operation","subject_scope","semantic_effect_key","fingerprint","state","source_revision","fence","result_schema_id","result_hash","committed_at") ON "platform"."runtime_effect_receipt" TO wa_worker;

GRANT SELECT ("id","command_receipt_id","owner_module_id","operation","subject_scope","semantic_effect_key","fingerprint","state","source_revision","fence","result_schema_id","result_hash","committed_at","created_at","mutation_transaction_id") ON "platform"."runtime_effect_receipt" TO wa_worker;

-- SQL-01/02: RuntimeWorkItem
ALTER TABLE "platform"."runtime_work_item" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "platform"."runtime_work_item" FORCE ROW LEVEL SECURITY;

GRANT INSERT ("id","outbox_message_id","handler_name","semantic_work_key","state","fence","lease_token_hash","lease_expires_at","attempt_count","next_attempt_at","effect_receipt_id") ON "platform"."runtime_work_item" TO wa_app_runtime;

GRANT SELECT ("id","outbox_message_id","handler_name","semantic_work_key","state","fence","lease_token_hash","lease_expires_at","attempt_count","next_attempt_at","effect_receipt_id","created_at","mutation_transaction_id") ON "platform"."runtime_work_item" TO wa_app_runtime;

GRANT UPDATE ("handler_name","semantic_work_key","state","fence","lease_token_hash","lease_expires_at","attempt_count","next_attempt_at") ON "platform"."runtime_work_item" TO wa_app_runtime;

GRANT INSERT ("id","outbox_message_id","handler_name","semantic_work_key","state","fence","lease_token_hash","lease_expires_at","attempt_count","next_attempt_at","effect_receipt_id") ON "platform"."runtime_work_item" TO wa_worker;

GRANT SELECT ("id","outbox_message_id","handler_name","semantic_work_key","state","fence","lease_token_hash","lease_expires_at","attempt_count","next_attempt_at","effect_receipt_id","created_at","mutation_transaction_id") ON "platform"."runtime_work_item" TO wa_worker;

GRANT UPDATE ("id","outbox_message_id","handler_name","semantic_work_key","state","fence","lease_token_hash","lease_expires_at","attempt_count","next_attempt_at","effect_receipt_id","created_at","mutation_transaction_id") ON "platform"."runtime_work_item" TO wa_worker;

-- SQL-01/02: RuntimeAttempt
ALTER TABLE "platform"."runtime_attempt" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "platform"."runtime_attempt" FORCE ROW LEVEL SECURITY;

GRANT INSERT ("id","work_item_id","attempt_number","fence","worker_id","result","reason_code","started_at","finished_at") ON "platform"."runtime_attempt" TO wa_app_runtime;

GRANT SELECT ("id","work_item_id","attempt_number","fence","worker_id","result","reason_code","started_at","finished_at","created_at","mutation_transaction_id") ON "platform"."runtime_attempt" TO wa_app_runtime;

GRANT INSERT ("id","work_item_id","attempt_number","fence","worker_id","result","reason_code","started_at","finished_at") ON "platform"."runtime_attempt" TO wa_worker;

GRANT SELECT ("id","work_item_id","attempt_number","fence","worker_id","result","reason_code","started_at","finished_at","created_at","mutation_transaction_id") ON "platform"."runtime_attempt" TO wa_worker;

-- SQL-01/02: RuntimeInboxReceipt
ALTER TABLE "platform"."runtime_inbox_receipt" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "platform"."runtime_inbox_receipt" FORCE ROW LEVEL SECURITY;

GRANT INSERT ("id","outbox_message_id","consumer_owner","handler_name","payload_hash","effect_receipt_id") ON "platform"."runtime_inbox_receipt" TO wa_app_runtime;

GRANT SELECT ("id","outbox_message_id","consumer_owner","handler_name","payload_hash","effect_receipt_id","created_at","mutation_transaction_id") ON "platform"."runtime_inbox_receipt" TO wa_app_runtime;

GRANT INSERT ("id","outbox_message_id","consumer_owner","handler_name","payload_hash","effect_receipt_id") ON "platform"."runtime_inbox_receipt" TO wa_worker;

GRANT SELECT ("id","outbox_message_id","consumer_owner","handler_name","payload_hash","effect_receipt_id","created_at","mutation_transaction_id") ON "platform"."runtime_inbox_receipt" TO wa_worker;

-- SQL-01/02: RuntimeReservation
ALTER TABLE "platform"."runtime_reservation" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "platform"."runtime_reservation" FORCE ROW LEVEL SECURITY;

GRANT INSERT ("id","command_receipt_id","owner_module_id","resource_kind","resource_key","semantic_key","quantity","state","fence","effect_receipt_id","expires_at") ON "platform"."runtime_reservation" TO wa_app_runtime;

GRANT SELECT ("id","command_receipt_id","owner_module_id","resource_kind","resource_key","semantic_key","quantity","state","fence","effect_receipt_id","expires_at","created_at","mutation_transaction_id") ON "platform"."runtime_reservation" TO wa_app_runtime;

GRANT UPDATE ("resource_kind","resource_key","semantic_key","quantity","state","fence","expires_at") ON "platform"."runtime_reservation" TO wa_app_runtime;

GRANT INSERT ("id","command_receipt_id","owner_module_id","resource_kind","resource_key","semantic_key","quantity","state","fence","effect_receipt_id","expires_at") ON "platform"."runtime_reservation" TO wa_worker;

GRANT SELECT ("id","command_receipt_id","owner_module_id","resource_kind","resource_key","semantic_key","quantity","state","fence","effect_receipt_id","expires_at","created_at","mutation_transaction_id") ON "platform"."runtime_reservation" TO wa_worker;

GRANT UPDATE ("id","command_receipt_id","owner_module_id","resource_kind","resource_key","semantic_key","quantity","state","fence","effect_receipt_id","expires_at","created_at","mutation_transaction_id") ON "platform"."runtime_reservation" TO wa_worker;

-- SQL-01/02: OwnerMutationEvidence
ALTER TABLE "platform"."owner_mutation_evidence" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "platform"."owner_mutation_evidence" FORCE ROW LEVEL SECURITY;

GRANT INSERT ("id","command_receipt_id","owner_module_id","aggregate_kind","aggregate_id","previous_revision","committed_revision","action","decision_ref","evidence_schema_id","evidence_schema_version","evidence_digest","evidence_body") ON "platform"."owner_mutation_evidence" TO wa_app_runtime;

GRANT SELECT ("id","command_receipt_id","owner_module_id","aggregate_kind","aggregate_id","previous_revision","committed_revision","action","decision_ref","evidence_schema_id","evidence_schema_version","evidence_digest","created_at","evidence_body","mutation_transaction_id") ON "platform"."owner_mutation_evidence" TO wa_app_runtime;

GRANT INSERT ("id","command_receipt_id","owner_module_id","aggregate_kind","aggregate_id","previous_revision","committed_revision","action","decision_ref","evidence_schema_id","evidence_schema_version","evidence_digest","evidence_body") ON "platform"."owner_mutation_evidence" TO wa_worker;

GRANT SELECT ("id","command_receipt_id","owner_module_id","aggregate_kind","aggregate_id","previous_revision","committed_revision","action","decision_ref","evidence_schema_id","evidence_schema_version","evidence_digest","created_at","evidence_body","mutation_transaction_id") ON "platform"."owner_mutation_evidence" TO wa_worker;

-- SQL-01/02: CustomerProfileLifecycleEvent
ALTER TABLE "app"."customer_profile_lifecycle_event" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "app"."customer_profile_lifecycle_event" FORCE ROW LEVEL SECURITY;

GRANT INSERT ("id","customer_profile_id","command_receipt_id","source_revision","from_status","to_status","name","actor_user_id") ON "app"."customer_profile_lifecycle_event" TO wa_app_runtime;

GRANT SELECT ("id","customer_profile_id","command_receipt_id","source_revision","from_status","to_status","name","actor_user_id","created_at","mutation_transaction_id") ON "app"."customer_profile_lifecycle_event" TO wa_app_runtime;

-- SQL-01/02: TrackBaseSelection
ALTER TABLE "app"."track_base_selection" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "app"."track_base_selection" FORCE ROW LEVEL SECURITY;

GRANT INSERT ("id","user_id","track","customer_profile_id","candidate_profile_id","professional_profile_id","subscription_id","revision","source_generation") ON "app"."track_base_selection" TO wa_app_runtime;

GRANT SELECT ("id","user_id","track","customer_profile_id","candidate_profile_id","professional_profile_id","subscription_id","revision","source_generation","created_at","mutation_transaction_id") ON "app"."track_base_selection" TO wa_app_runtime;

GRANT UPDATE ("track","revision","source_generation") ON "app"."track_base_selection" TO wa_app_runtime;

GRANT INSERT ("id","user_id","track","customer_profile_id","candidate_profile_id","professional_profile_id","subscription_id","source_generation") ON "app"."track_base_selection" TO wa_worker;

GRANT SELECT ("id","user_id","track","customer_profile_id","candidate_profile_id","professional_profile_id","subscription_id","revision","source_generation") ON "app"."track_base_selection" TO wa_worker;

GRANT UPDATE ("subscription_id","revision","source_generation") ON "app"."track_base_selection" TO wa_worker;

-- SQL-01/02: TrackEnrollmentReceipt
ALTER TABLE "app"."track_enrollment_receipt" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "app"."track_enrollment_receipt" FORCE ROW LEVEL SECURITY;

GRANT INSERT ("id","user_id","track","profile_id","source_owner","source_creation_revision","selection_id","selection_revision","semantic_key","fingerprint","result_code","effect_receipt_id") ON "app"."track_enrollment_receipt" TO wa_app_runtime;

GRANT SELECT ("id","user_id","track","profile_id","source_owner","source_creation_revision","selection_id","selection_revision","semantic_key","fingerprint","result_code","effect_receipt_id","created_at","mutation_transaction_id") ON "app"."track_enrollment_receipt" TO wa_app_runtime;

GRANT INSERT ("id","user_id","track","profile_id","source_owner","source_creation_revision","selection_id","selection_revision","semantic_key","fingerprint","result_code","effect_receipt_id") ON "app"."track_enrollment_receipt" TO wa_worker;

GRANT SELECT ("id","user_id","track","profile_id","source_owner","source_creation_revision","selection_id","selection_revision","semantic_key","fingerprint","result_code","effect_receipt_id") ON "app"."track_enrollment_receipt" TO wa_worker;

-- SQL-01/02: TrackUsageReservation
ALTER TABLE "app"."track_usage_reservation" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "app"."track_usage_reservation" FORCE ROW LEVEL SECURITY;

GRANT INSERT ("id","user_id","entitlement_id","period_start","period_end","quantity","semantic_key","reservation_id","accepted_source_owner","accepted_source_id","accepted_at","revision") ON "app"."track_usage_reservation" TO wa_app_runtime;

GRANT SELECT ("id","user_id","entitlement_id","period_start","period_end","quantity","semantic_key","reservation_id","accepted_source_owner","accepted_source_id","accepted_at","created_at","revision","mutation_transaction_id") ON "app"."track_usage_reservation" TO wa_app_runtime;

GRANT UPDATE ("period_start","period_end","quantity","semantic_key","accepted_source_owner","accepted_at","revision") ON "app"."track_usage_reservation" TO wa_app_runtime;

-- SQL-01/02: PrivacyTargetInstruction
ALTER TABLE "app"."privacy_target_instruction" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "app"."privacy_target_instruction" FORCE ROW LEVEL SECURITY;

GRANT INSERT ("id","privacy_request_id","owner_module_id","target_kind","source_id","source_revision","action","generation","field_map_version","executor_version","descriptor_hash") ON "app"."privacy_target_instruction" TO wa_app_runtime;

GRANT SELECT ("id","privacy_request_id","owner_module_id","target_kind","source_id","source_revision","action","generation","field_map_version","executor_version","descriptor_hash","created_at","mutation_transaction_id") ON "app"."privacy_target_instruction" TO wa_app_runtime;

-- SQL-01/02: PrivacyOwnerReceipt
ALTER TABLE "app"."privacy_owner_receipt" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "app"."privacy_owner_receipt" FORCE ROW LEVEL SECURITY;

GRANT INSERT ("id","instruction_id","generation","disposition","execution_receipt_ref","legal_basis_ref","artifact_digest","artifact_version","result_schema_version") ON "app"."privacy_owner_receipt" TO wa_app_runtime;

GRANT SELECT ("id","instruction_id","generation","disposition","execution_receipt_ref","legal_basis_ref","artifact_digest","artifact_version","result_schema_version","created_at","mutation_transaction_id") ON "app"."privacy_owner_receipt" TO wa_app_runtime;

-- SQL-01/02: PrivacyRestoreMarker
ALTER TABLE "app"."privacy_restore_marker" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "app"."privacy_restore_marker" FORCE ROW LEVEL SECURITY;

GRANT INSERT ("id","owner_module_id","target_kind","source_id","generation","action","source_receipt_id","restore_point_ref","applied_at","revision") ON "app"."privacy_restore_marker" TO wa_app_runtime;

GRANT SELECT ("id","owner_module_id","target_kind","source_id","generation","action","source_receipt_id","restore_point_ref","applied_at","created_at","revision","mutation_transaction_id") ON "app"."privacy_restore_marker" TO wa_app_runtime;

GRANT UPDATE ("target_kind","generation","action","restore_point_ref","applied_at","revision") ON "app"."privacy_restore_marker" TO wa_app_runtime;

GRANT SELECT ("id","user_id","status","archived_at","revision","privacy_generation") ON app.customer_profiles TO wa_customer_verifier;

CREATE POLICY "leaf_wa_customer_verifier" ON app.customer_profiles FOR SELECT TO wa_customer_verifier USING (true);

GRANT SELECT ("customer_profile_id","source_revision","command_receipt_id","actor_user_id","from_status","to_status") ON app.customer_profile_lifecycle_event TO wa_customer_verifier;

CREATE POLICY "leaf_wa_customer_verifier" ON app.customer_profile_lifecycle_event FOR SELECT TO wa_customer_verifier USING (true);

GRANT USAGE ON TYPE "app"."profile_status" TO wa_customer_verifier;

GRANT SELECT ("id","outbox_message_id","handler_name","semantic_work_key","state","fence","lease_token_hash","lease_expires_at","effect_receipt_id","mutation_transaction_id") ON platform.runtime_work_item TO wa_track_verifier;

CREATE POLICY "leaf_wa_track_verifier" ON platform.runtime_work_item FOR SELECT TO wa_track_verifier USING (true);

GRANT SELECT ("id","command_receipt_id","kind","name","producer_owner","aggregate_kind","aggregate_id","source_revision","source_generation","payload","payload_hash") ON platform.runtime_outbox_message TO wa_track_verifier;

CREATE POLICY "leaf_wa_track_verifier" ON platform.runtime_outbox_message FOR SELECT TO wa_track_verifier USING (true);

GRANT SELECT ("id","owner_module_id","operation","subject_scope","semantic_key","fingerprint","state","mutation_transaction_id") ON platform.runtime_command_receipt TO wa_track_verifier;

CREATE POLICY "leaf_wa_track_verifier" ON platform.runtime_command_receipt FOR SELECT TO wa_track_verifier USING (true);

GRANT SELECT ("id","owner_module_id","operation","command_receipt_id","subject_scope","semantic_effect_key","fingerprint","fence","state","mutation_transaction_id") ON platform.runtime_effect_receipt TO wa_track_verifier;

CREATE POLICY "leaf_wa_track_verifier" ON platform.runtime_effect_receipt FOR SELECT TO wa_track_verifier USING (true);

GRANT SELECT ("effect_receipt_id","outbox_message_id","handler_name","consumer_owner","payload_hash","mutation_transaction_id") ON platform.runtime_inbox_receipt TO wa_track_verifier;

CREATE POLICY "leaf_wa_track_verifier" ON platform.runtime_inbox_receipt FOR SELECT TO wa_track_verifier USING (true);

GRANT SELECT ("id","track","status","billing_model","revision","version","content_hash") ON app.track_plans TO wa_track_verifier;

CREATE POLICY "leaf_wa_track_verifier" ON app.track_plans FOR SELECT TO wa_track_verifier USING (true);

GRANT SELECT ("id","user_id","plan_id","track","customer_profile_id","status","provider","ended_at","current_period_end","mutation_transaction_id","revision","candidate_profile_id","professional_profile_id") ON app.track_subscriptions TO wa_track_verifier;

CREATE POLICY "leaf_wa_track_verifier" ON app.track_subscriptions FOR SELECT TO wa_track_verifier USING (true);

GRANT SELECT ("id","user_id","track","customer_profile_id","subscription_id","revision","mutation_transaction_id","source_generation","candidate_profile_id","professional_profile_id") ON app.track_base_selection TO wa_track_verifier;

CREATE POLICY "leaf_wa_track_verifier" ON app.track_base_selection FOR SELECT TO wa_track_verifier USING (true);

GRANT SELECT ("selection_id","selection_revision","effect_receipt_id","mutation_transaction_id") ON app.track_enrollment_receipt TO wa_track_verifier;

CREATE POLICY "leaf_wa_track_verifier" ON app.track_enrollment_receipt FOR SELECT TO wa_track_verifier USING (true);

GRANT SELECT ("subscription_id","user_id","plan_id","to_status","from_status","mutation_transaction_id") ON app.track_subscription_events TO wa_track_verifier;

CREATE POLICY "leaf_wa_track_verifier" ON app.track_subscription_events FOR SELECT TO wa_track_verifier USING (true);

GRANT SELECT ("id","is_active","track","value_type") ON app.track_entitlement_definitions TO wa_track_verifier;

CREATE POLICY "leaf_wa_track_verifier" ON app.track_entitlement_definitions FOR SELECT TO wa_track_verifier USING (true);

GRANT SELECT ("plan_id","entitlement_id","value_type","boolean_value","int_value","decimal_value","string_value") ON app.track_plan_entitlements TO wa_track_verifier;

CREATE POLICY "leaf_wa_track_verifier" ON app.track_plan_entitlements FOR SELECT TO wa_track_verifier USING (true);

GRANT SELECT ("id","user_id","track","customer_profile_id","candidate_profile_id","professional_profile_id","status","value_type","revision","mutation_transaction_id") ON app.track_entitlement_grants TO wa_track_verifier;

CREATE POLICY "leaf_wa_track_verifier" ON app.track_entitlement_grants FOR SELECT TO wa_track_verifier USING (true);

GRANT USAGE ON TYPE "app"."account_track" TO wa_track_verifier;

GRANT USAGE ON TYPE "platform"."runtime_message_kind" TO wa_track_verifier;

GRANT USAGE ON TYPE "platform"."runtime_receipt_state" TO wa_track_verifier;

GRANT USAGE ON TYPE "platform"."runtime_work_state" TO wa_track_verifier;

GRANT USAGE ON TYPE "app"."track_billing_model" TO wa_track_verifier;

GRANT USAGE ON TYPE "app"."track_billing_provider" TO wa_track_verifier;

GRANT USAGE ON TYPE "app"."track_entitlement_grant_status" TO wa_track_verifier;

GRANT USAGE ON TYPE "app"."track_entitlement_value_type" TO wa_track_verifier;

GRANT USAGE ON TYPE "app"."track_plan_status" TO wa_track_verifier;

GRANT USAGE ON TYPE "app"."track_subscription_status" TO wa_track_verifier;

-- DRAFT-02: fixed Boolean ports. Read maxima are emitted from the separate
-- foundation-sql-verifier-access.json register, never granted to the worker.
CREATE FUNCTION platform_private.lease_secret_matches(expected_hash text) RETURNS boolean
LANGUAGE sql VOLATILE SECURITY INVOKER SET search_path=pg_catalog AS $wa$
 SELECT CASE WHEN current_setting('wa.lease_secret',true) ~ '^[0-9a-f]{64}$'
  THEN encode(sha256(decode(current_setting('wa.lease_secret',true),'hex')),'hex')=expected_hash
  ELSE false END;
$wa$;

CREATE FUNCTION platform_private.customer_current_for_track(customer_id uuid, user_id uuid, creation_revision bigint, privacy_generation bigint, creation_receipt uuid) RETURNS boolean
LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog AS $wa$
DECLARE g platform.database_action_grant; c record;
BEGIN
 g:=platform_private.bound_grant(true);
 IF g.id IS NULL OR session_user::text<>'wa_worker' OR g.service_principal IS NULL
  OR NOT platform_private.context_allows('track_subscription_entitlement','assignDefaultFreeTrack.v1','RuntimeWorkItem',g.target_id,'default_free_enrollment')
 THEN RETURN false; END IF;
 PERFORM pg_advisory_xact_lock_shared(hashtextextended('source:CustomerProfile:'||customer_id::text,0));
 SELECT p.id,p.user_id,p.status,p.archived_at,p.revision,p.privacy_generation INTO c FROM app.customer_profiles p WHERE p.id=customer_id;
 RETURN COALESCE(c.id IS NOT NULL AND c.user_id=user_id AND c.status='active' AND c.archived_at IS NULL
  AND c.privacy_generation=privacy_generation AND creation_revision=0
  AND 'CustomerProfile/'||customer_id::text||'/revision/'||c.revision::text=ANY(g.allowed_fields)
  AND EXISTS(SELECT 1 FROM app.customer_profile_lifecycle_event h WHERE h.customer_profile_id=customer_id
   AND h.source_revision=creation_revision AND h.command_receipt_id=creation_receipt
   AND h.actor_user_id=user_id AND h.from_status IS NULL AND h.to_status='active'),false);
END $wa$;

CREATE FUNCTION platform_private.worker_lease_valid(work_id uuid, effect_id uuid DEFAULT NULL, allow_completed boolean DEFAULT false) RETURNS boolean
LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog AS $wa$
DECLARE g platform.database_action_grant; w record;
BEGIN
 g:=platform_private.bound_grant(true);
 IF g.id IS NULL OR session_user::text<>'wa_worker' OR g.service_principal IS NULL
  OR NOT platform_private.context_allows('track_subscription_entitlement','assignDefaultFreeTrack.v1','RuntimeWorkItem',work_id::text,'default_free_enrollment')
 THEN RETURN false; END IF;
 SELECT j.id,j.handler_name,j.state,j.fence,j.lease_token_hash,j.lease_expires_at,j.effect_receipt_id,j.mutation_transaction_id INTO w
  FROM platform.runtime_work_item j WHERE j.id=work_id;
 RETURN COALESCE(w.id IS NOT NULL AND w.handler_name='assignDefaultFreeTrack.v1'
  AND (w.state='leased' OR (allow_completed AND w.state='completed' AND w.mutation_transaction_id=pg_current_xact_id()::text))
  AND w.fence=g.source_generation AND w.fence::text=current_setting('wa.fence',true)
  AND w.lease_expires_at>clock_timestamp() AND platform_private.lease_secret_matches(w.lease_token_hash::text)
  AND (effect_id IS NULL OR w.effect_receipt_id=effect_id),false);
END $wa$;

CREATE FUNCTION platform_private.worker_effect_matches(work_id uuid, effect_id uuid, require_link boolean DEFAULT true) RETURNS boolean
LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog AS $wa$
DECLARE g platform.database_action_grant; w record; e record; c record; o record;
BEGIN
 g:=platform_private.bound_grant(true);
 IF g.id IS NULL OR NOT platform_private.worker_lease_valid(work_id,NULL,true) THEN RETURN false; END IF;
 SELECT j.id,j.outbox_message_id,j.effect_receipt_id,j.handler_name,j.semantic_work_key,j.fence INTO w FROM platform.runtime_work_item j WHERE j.id=work_id;
 SELECT m.id,m.aggregate_id,m.payload_hash FROM platform.runtime_outbox_message m WHERE m.id=w.outbox_message_id INTO o;
 SELECT r.id,r.command_receipt_id,r.owner_module_id,r.operation,r.subject_scope,r.semantic_effect_key,r.fingerprint,r.fence,r.state,r.mutation_transaction_id INTO e
  FROM platform.runtime_effect_receipt r WHERE r.id=effect_id;
 SELECT r.id,r.owner_module_id,r.operation,r.subject_scope,r.semantic_key,r.fingerprint,r.state,r.mutation_transaction_id INTO c
  FROM platform.runtime_command_receipt r WHERE r.id=e.command_receipt_id;
 RETURN COALESCE((NOT require_link OR w.effect_receipt_id=e.id) AND e.id IS NOT NULL
  AND 'RuntimeWorkItem/'||w.id::text||'/effect/'||e.id::text=ANY(g.allowed_fields)
  AND 'RuntimeWorkItem/'||w.id::text||'/command/'||c.id::text=ANY(g.allowed_fields)
  AND e.owner_module_id='track_subscription_entitlement' AND c.owner_module_id=e.owner_module_id
  AND e.operation=w.handler_name AND c.operation=e.operation AND e.state='committed' AND c.state='committed'
  AND e.subject_scope='CustomerProfile:'||o.aggregate_id AND c.subject_scope=e.subject_scope
  AND e.semantic_effect_key=w.semantic_work_key AND c.semantic_key=e.semantic_effect_key
  AND e.fingerprint=o.payload_hash AND c.fingerprint=e.fingerprint AND e.fence<=w.fence
  AND e.mutation_transaction_id=c.mutation_transaction_id
  AND EXISTS(SELECT 1 FROM platform.runtime_inbox_receipt i WHERE i.outbox_message_id=o.id
   AND i.effect_receipt_id=e.id AND i.consumer_owner=e.owner_module_id AND i.handler_name=e.operation
   AND i.payload_hash=o.payload_hash AND i.mutation_transaction_id=e.mutation_transaction_id),false);
END $wa$;

CREATE FUNCTION platform_private.worker_track_allowed(model_name text, row_value jsonb, verb text) RETURNS boolean
LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog AS $wa$
DECLARE g platform.database_action_grant; w record; o record; p record; s record;
 u uuid; customer uuid; expected_effect text; scope text; row_id uuid; expected_command text;
BEGIN
 g:=platform_private.bound_grant(true);
 IF g.id IS NULL OR session_user::text<>'wa_worker' OR g.service_principal IS NULL OR verb NOT IN ('SELECT','INSERT','UPDATE') THEN RETURN false; END IF;
 -- Claims inspect/update only their exact queued job. They cannot create effects.
 IF model_name='RuntimeWorkItem' AND g.action IN ('runtime.claim_work.v1','runtime.renew_work.v1') THEN
  RETURN platform_private.context_allows('platform_integration_owner',g.action,'RuntimeWorkItem',row_value->>'id',
   CASE WHEN g.action='runtime.claim_work.v1' THEN 'work.claim' ELSE 'work.renew' END);
 END IF;
 IF NOT platform_private.worker_lease_valid(g.target_id::uuid,NULL,true) THEN RETURN false; END IF;
 SELECT j.id,j.outbox_message_id,j.semantic_work_key,j.effect_receipt_id,j.fence INTO w FROM platform.runtime_work_item j WHERE j.id=g.target_id::uuid;
 SELECT m.id,m.command_receipt_id,m.kind,m.name,m.producer_owner,m.aggregate_kind,m.aggregate_id,m.source_revision,m.source_generation,m.payload,m.payload_hash INTO o
  FROM platform.runtime_outbox_message m WHERE m.id=w.outbox_message_id;
 IF o.id IS NULL OR o.kind<>'command' OR o.name<>'assignDefaultFreeTrack.v1'
  OR o.producer_owner<>'customer_buyer_profile' OR o.aggregate_kind<>'CustomerProfile'
  OR o.source_revision<>0 OR o.payload->>'sourceCreationReceipt'<>o.command_receipt_id::text
 THEN RETURN false; END IF;
 u:=(o.payload->>'userId')::uuid;customer:=o.aggregate_id::uuid;
 IF NOT platform_private.customer_current_for_track(customer,u,o.source_revision,o.source_generation,o.command_receipt_id) THEN RETURN false; END IF;
 scope:='CustomerProfile:'||customer::text;
 expected_effect:='customer_buyer_profile/'||customer::text||'/default-free-enrollment/v1';
 IF w.semantic_work_key<>expected_effect THEN RETURN false; END IF;
 IF model_name='RuntimeWorkItem' THEN
  RETURN COALESCE(row_value->>'id'=w.id::text AND verb IN ('SELECT','UPDATE'),false);
 ELSIF model_name='RuntimeOutboxMessage' THEN RETURN verb='SELECT' AND row_value->>'id'=o.id::text;
 ELSIF model_name='RuntimeAttempt' THEN
  RETURN COALESCE(row_value->>'work_item_id'=w.id::text AND (row_value->>'fence')::bigint=w.fence
   AND row_value->>'worker_id'=g.service_principal AND verb IN ('SELECT','INSERT'),false);
 ELSIF model_name='RuntimeCommandReceipt' THEN
  RETURN COALESCE(('RuntimeWorkItem/'||w.id::text||'/command/'||(row_value->>'id'))=ANY(g.allowed_fields)
   AND row_value->>'owner_module_id'='track_subscription_entitlement' AND row_value->>'operation'='assignDefaultFreeTrack.v1'
   AND row_value->>'subject_scope'=scope AND row_value->>'semantic_key'=expected_effect AND row_value->>'fingerprint'=o.payload_hash::text,false);
 ELSIF model_name='RuntimeEffectReceipt' THEN
  RETURN COALESCE(('RuntimeWorkItem/'||w.id::text||'/effect/'||(row_value->>'id'))=ANY(g.allowed_fields)
   AND ('RuntimeWorkItem/'||w.id::text||'/command/'||(row_value->>'command_receipt_id'))=ANY(g.allowed_fields)
   AND row_value->>'owner_module_id'='track_subscription_entitlement' AND row_value->>'operation'='assignDefaultFreeTrack.v1'
   AND row_value->>'subject_scope'=scope AND row_value->>'semantic_effect_key'=expected_effect
   AND row_value->>'fingerprint'=o.payload_hash::text
   AND ((row_value->>'fence')::bigint=w.fence OR
    (verb='SELECT' AND platform_private.worker_effect_matches(w.id,(row_value->>'id')::uuid,true))),false);
 ELSIF model_name='RuntimeInboxReceipt' THEN
  RETURN COALESCE(row_value->>'outbox_message_id'=o.id::text AND row_value->>'consumer_owner'='track_subscription_entitlement'
   AND row_value->>'handler_name'='assignDefaultFreeTrack.v1' AND row_value->>'payload_hash'=o.payload_hash::text
   AND ('RuntimeWorkItem/'||w.id::text||'/effect/'||(row_value->>'effect_receipt_id'))=ANY(g.allowed_fields),false);
 ELSIF model_name='OwnerMutationEvidence' THEN
  RETURN COALESCE(row_value->>'owner_module_id'='track_subscription_entitlement'
   AND row_value->>'aggregate_kind' IN ('TrackSubscription','TrackEntitlementGrant','TrackBaseSelection','TrackSubscriptionEvent','TrackEnrollmentReceipt')
   AND row_value->'evidence_body'->'committed'->>'userId'=u::text,false);
 END IF;
 IF NOT model_name LIKE 'Track%' THEN RETURN false; END IF;
 -- Only a current, explicitly approved catalog revision may create Free access.
 IF model_name='TrackPlan' THEN row_id:=(row_value->>'id')::uuid;
 ELSE
  SELECT b.plan_id INTO row_id FROM app.track_base_selection a JOIN app.track_subscriptions b ON b.id=a.subscription_id
   WHERE a.user_id=u AND a.track='customer' AND a.customer_profile_id=customer;
  IF verb='INSERT' AND model_name='TrackSubscription' THEN row_id:=(row_value->>'plan_id')::uuid;
  ELSIF model_name='TrackPlanEntitlement' THEN row_id:=(row_value->>'plan_id')::uuid;
  ELSIF model_name='TrackEntitlementGrant' AND verb='INSERT' THEN row_id:=(row_value->>'source_plan_id')::uuid;
  END IF;
 END IF;
 IF row_id IS NOT NULL THEN
  PERFORM pg_advisory_xact_lock_shared(hashtextextended('source:TrackPlan:'||row_id::text,0));
  SELECT x.id,x.track,x.status,x.billing_model,x.version,x.content_hash,x.revision INTO p FROM app.track_plans x WHERE x.id=row_id;
 END IF;
 IF model_name IN ('TrackPlan','TrackPlanEntitlement','TrackEntitlementDefinition') THEN
  IF verb<>'SELECT' THEN RETURN false; END IF;
  IF model_name='TrackEntitlementDefinition' THEN
   RETURN EXISTS(SELECT 1 FROM app.track_plan_entitlements b JOIN app.track_plans q ON q.id=b.plan_id
    WHERE b.entitlement_id=(row_value->>'id')::uuid AND q.track='customer'
     AND 'TrackPlan/'||q.id::text||'/revision/'||q.revision::text=ANY(g.allowed_fields)
     AND 'TrackPlan/'||q.id::text||'/version/'||q.version=ANY(g.allowed_fields)
     AND 'TrackPlan/'||q.id::text||'/contentHash/'||q.content_hash::text=ANY(g.allowed_fields)
     AND q.status='active' AND q.billing_model='free');
  END IF;
  RETURN COALESCE(p.id IS NOT NULL AND p.track='customer'
   AND 'TrackPlan/'||p.id::text||'/revision/'||p.revision::text=ANY(g.allowed_fields)
   AND 'TrackPlan/'||p.id::text||'/version/'||p.version=ANY(g.allowed_fields)
   AND 'TrackPlan/'||p.id::text||'/contentHash/'||p.content_hash::text=ANY(g.allowed_fields),false);
 END IF;
 IF model_name='TrackEnrollmentReceipt' THEN
  RETURN COALESCE(row_value->>'user_id'=u::text AND row_value->>'profile_id'=customer::text
   AND row_value->>'source_owner'='customer_buyer_profile' AND row_value->>'track'='customer'
   AND row_value->>'source_creation_revision'=o.source_revision::text AND row_value->>'semantic_key'=expected_effect
   AND ('RuntimeWorkItem/'||w.id::text||'/effect/'||(row_value->>'effect_receipt_id'))=ANY(g.allowed_fields),false);
 END IF;
 IF row_value->>'user_id' IS DISTINCT FROM u::text THEN RETURN false; END IF;
 IF model_name='TrackSubscriptionEvent' THEN
  RETURN verb='INSERT' AND row_value->>'from_status' IS NULL AND row_value->>'provider'='none';
 END IF;
 IF row_value->>'track' IS DISTINCT FROM 'customer' OR row_value->>'customer_profile_id' IS DISTINCT FROM customer::text
  OR row_value->>'candidate_profile_id' IS NOT NULL OR row_value->>'professional_profile_id' IS NOT NULL THEN RETURN false; END IF;
 IF model_name='TrackSubscription' THEN
  IF verb='SELECT' THEN RETURN EXISTS(SELECT 1 FROM app.track_base_selection b WHERE b.user_id=u AND b.track='customer' AND b.subscription_id=(row_value->>'id')::uuid)
    OR EXISTS(SELECT 1 FROM app.track_subscriptions a WHERE a.id=(row_value->>'id')::uuid AND a.mutation_transaction_id=pg_current_xact_id()::text); END IF;
  IF verb<>'INSERT' OR p.id IS NULL OR p.status<>'active' OR p.billing_model<>'free' OR p.track<>'customer'
   OR row_value->>'provider'<>'none' OR row_value->>'status'<>'active'
   OR NOT ('TrackPlan/'||p.id::text||'/revision/'||p.revision::text=ANY(g.allowed_fields))
   OR NOT ('TrackPlan/'||p.id::text||'/version/'||p.version=ANY(g.allowed_fields))
   OR NOT ('TrackPlan/'||p.id::text||'/contentHash/'||p.content_hash::text=ANY(g.allowed_fields)) THEN RETURN false; END IF;
  PERFORM pg_advisory_xact_lock(hashtextextended('track:'||u::text||':customer',0));
  RETURN NOT EXISTS(SELECT 1 FROM app.track_base_selection b JOIN app.track_subscriptions a ON a.id=b.subscription_id
   WHERE b.user_id=u AND b.track='customer' AND a.status IN ('active','trialing') AND a.ended_at IS NULL
    AND (a.current_period_end IS NULL OR a.current_period_end>clock_timestamp()));
 END IF;
 RETURN model_name IN ('TrackBaseSelection','TrackEntitlementGrant') AND verb IN ('SELECT','INSERT','UPDATE');
END $wa$;

CREATE FUNCTION platform_private.track_atomic_valid(table_name text, n jsonb, prior_value jsonb) RETURNS boolean
LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog AS $wa$
DECLARE g platform.database_action_grant; s record; old_s record; p record; sel record; e record; o record; w record;
BEGIN
 g:=platform_private.bound_grant(true);
 IF g.id IS NULL OR NOT platform_private.worker_lease_valid(g.target_id::uuid,NULL,true) THEN RETURN false; END IF;
 SELECT j.id,j.outbox_message_id,j.effect_receipt_id,j.fence INTO w FROM platform.runtime_work_item j WHERE j.id=g.target_id::uuid;
 SELECT m.id,m.command_receipt_id,m.aggregate_id,m.source_revision,m.source_generation,m.payload_hash,m.payload INTO o FROM platform.runtime_outbox_message m WHERE m.id=w.outbox_message_id;
 IF NOT platform_private.customer_current_for_track(o.aggregate_id::uuid,(o.payload->>'userId')::uuid,o.source_revision,o.source_generation,o.command_receipt_id) THEN RETURN false; END IF;
 IF table_name='track_base_selection' THEN
  SELECT a.id,a.user_id,a.plan_id,a.track,a.customer_profile_id,a.status,a.provider,a.mutation_transaction_id INTO s FROM app.track_subscriptions a WHERE a.id=(n->>'subscription_id')::uuid;
  SELECT q.id,q.status,q.billing_model,q.revision,q.version,q.content_hash INTO p FROM app.track_plans q WHERE q.id=s.plan_id;
  IF s.mutation_transaction_id IS DISTINCT FROM n->>'mutation_transaction_id' OR p.status<>'active' OR p.billing_model<>'free'
   OR s.provider<>'none' OR s.status<>'active' OR s.customer_profile_id::text IS DISTINCT FROM n->>'customer_profile_id'
   OR NOT ('TrackPlan/'||p.id::text||'/revision/'||p.revision::text=ANY(g.allowed_fields))
   OR NOT ('TrackPlan/'||p.id::text||'/version/'||p.version=ANY(g.allowed_fields))
   OR NOT ('TrackPlan/'||p.id::text||'/contentHash/'||p.content_hash::text=ANY(g.allowed_fields)) THEN RETURN false; END IF;
  IF prior_value IS NOT NULL THEN
   SELECT a.status,a.ended_at,a.current_period_end INTO old_s FROM app.track_subscriptions a WHERE a.id=(prior_value->>'subscription_id')::uuid;
   IF old_s.status IN ('active','trialing') AND old_s.ended_at IS NULL AND (old_s.current_period_end IS NULL OR old_s.current_period_end>clock_timestamp()) THEN RETURN false; END IF;
  END IF;
  RETURN EXISTS(SELECT 1 FROM app.track_enrollment_receipt r WHERE r.selection_id=(n->>'id')::uuid AND r.selection_revision=(n->>'revision')::bigint
   AND r.effect_receipt_id=w.effect_receipt_id AND r.mutation_transaction_id=n->>'mutation_transaction_id');
 ELSIF table_name='track_subscriptions' THEN
  RETURN EXISTS(SELECT 1 FROM app.track_base_selection b WHERE b.subscription_id=(n->>'id')::uuid AND b.mutation_transaction_id=n->>'mutation_transaction_id')
   AND EXISTS(SELECT 1 FROM app.track_subscription_events h WHERE h.subscription_id=(n->>'id')::uuid AND h.user_id::text=n->>'user_id'
    AND h.plan_id::text=n->>'plan_id' AND h.to_status::text=n->>'status' AND h.from_status IS NULL AND h.mutation_transaction_id=n->>'mutation_transaction_id');
 ELSIF table_name='track_entitlement_grants' THEN
  SELECT a.id,a.plan_id,a.mutation_transaction_id INTO s FROM app.track_subscriptions a WHERE a.id=(n->>'subscription_id')::uuid;
  RETURN COALESCE(s.mutation_transaction_id=n->>'mutation_transaction_id' AND s.plan_id::text=n->>'source_plan_id'
   AND EXISTS(SELECT 1 FROM app.track_plan_entitlements b JOIN app.track_entitlement_definitions d ON d.id=b.entitlement_id
    WHERE b.plan_id=s.plan_id AND b.entitlement_id=(n->>'entitlement_id')::uuid AND d.is_active AND (d.track IS NULL OR d.track='customer')
     AND d.value_type::text=n->>'value_type' AND b.value_type::text=n->>'value_type'
     AND COALESCE(to_jsonb(b.boolean_value),'null'::jsonb) IS NOT DISTINCT FROM n->'boolean_value' AND COALESCE(to_jsonb(b.int_value),'null'::jsonb) IS NOT DISTINCT FROM n->'int_value'
     AND COALESCE(to_jsonb(b.decimal_value),'null'::jsonb) IS NOT DISTINCT FROM n->'decimal_value' AND COALESCE(to_jsonb(b.string_value),'null'::jsonb) IS NOT DISTINCT FROM n->'string_value'),false);
 ELSIF table_name='track_subscription_events' THEN
  SELECT a.id,a.user_id,a.plan_id,a.status,a.mutation_transaction_id INTO s FROM app.track_subscriptions a WHERE a.id=(n->>'subscription_id')::uuid;
  RETURN COALESCE(s.mutation_transaction_id=n->>'mutation_transaction_id' AND s.user_id::text=n->>'user_id' AND s.plan_id::text=n->>'plan_id'
   AND n->>'from_status' IS NULL AND n->>'to_status'=s.status::text AND n->>'provider'='none',false);
 ELSIF table_name='track_enrollment_receipt' THEN
  SELECT b.id,b.user_id,b.track,b.customer_profile_id,b.revision INTO sel FROM app.track_base_selection b WHERE b.id=(n->>'selection_id')::uuid;
  SELECT r.id,r.owner_module_id,r.operation,r.command_receipt_id,r.subject_scope,r.semantic_effect_key,r.fingerprint,r.fence,r.state,r.mutation_transaction_id INTO e
   FROM platform.runtime_effect_receipt r WHERE r.id=(n->>'effect_receipt_id')::uuid;
  RETURN COALESCE(n->>'track'='customer' AND n->>'source_owner'='customer_buyer_profile'
   AND sel.user_id::text=n->>'user_id' AND sel.customer_profile_id::text=n->>'profile_id'
   AND n->>'profile_id'=o.aggregate_id AND n->>'source_creation_revision'=o.source_revision::text
   AND sel.revision::text=n->>'selection_revision' AND e.state='committed' AND e.fence=w.fence AND e.id=w.effect_receipt_id
   AND e.owner_module_id='track_subscription_entitlement' AND e.operation='assignDefaultFreeTrack.v1'
   AND e.subject_scope='CustomerProfile:'||o.aggregate_id AND e.semantic_effect_key=n->>'semantic_key'
   AND e.fingerprint=o.payload_hash AND e.mutation_transaction_id=n->>'mutation_transaction_id'
   AND EXISTS(SELECT 1 FROM platform.runtime_inbox_receipt i WHERE i.effect_receipt_id=e.id AND i.outbox_message_id=o.id
    AND i.handler_name='assignDefaultFreeTrack.v1' AND i.consumer_owner='track_subscription_entitlement'
    AND i.payload_hash=o.payload_hash AND i.mutation_transaction_id=e.mutation_transaction_id),false);
 END IF;
 RETURN false;
END $wa$;

CREATE POLICY "p_app_runtime_insert" ON "app"."consent_logs" FOR INSERT TO wa_app_runtime WITH CHECK (platform_private.row_allowed('consent_disclosure','ConsentLog',"id"::text,'INSERT',ARRAY['id','userId','type','version','acceptedAt','ipHash','userAgent','acceptanceKey','fingerprint','actionOwner','action','contextKind','contextId','contextOwner','presentationHash','contentRevisionId','presentationId']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_select" ON "app"."consent_logs" FOR SELECT TO wa_app_runtime USING (platform_private.row_allowed('consent_disclosure','ConsentLog',"id"::text,'SELECT',ARRAY['id','userId','type','version','acceptedAt','ipHash','userAgent','createdAt','acceptanceKey','fingerprint','actionOwner','action','contextKind','contextId','contextOwner','presentationHash','contentRevisionId','presentationId','mutationTransactionId']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_insert" ON "app"."privacy_requests" FOR INSERT TO wa_app_runtime WITH CHECK (platform_private.row_allowed('privacy_data_erasure','PrivacyRequest',"id"::text,'INSERT',ARRAY['id','userId','type','status','requestedAt','verifiedAt','dueAt','completedAt','rejectionReason','adminNote','updatedAt','revision','privacyGeneration','instructionGeneration']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_select" ON "app"."privacy_requests" FOR SELECT TO wa_app_runtime USING (platform_private.row_allowed('privacy_data_erasure','PrivacyRequest',"id"::text,'SELECT',ARRAY['id','userId','type','status','requestedAt','verifiedAt','dueAt','completedAt','rejectionReason','adminNote','createdAt','updatedAt','revision','privacyGeneration','instructionGeneration','mutationTransactionId']::text[],"revision"::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_update" ON "app"."privacy_requests" FOR UPDATE TO wa_app_runtime USING (platform_private.row_allowed('privacy_data_erasure','PrivacyRequest',"id"::text,'UPDATE',ARRAY['@row']::text[],NULL::text,"mutation_transaction_id"::text)) WITH CHECK (platform_private.row_allowed('privacy_data_erasure','PrivacyRequest',"id"::text,'UPDATE',ARRAY['@row']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_insert" ON "app"."age_gate_attempts" FOR INSERT TO wa_app_runtime WITH CHECK (platform_private.row_allowed('identity_access','AgeGateAttempt',"id"::text,'INSERT',ARRAY['id','userId','ipHash','deviceHash','region','result','birthYear','ageBand','blockedUntil']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_select" ON "app"."age_gate_attempts" FOR SELECT TO wa_app_runtime USING (platform_private.row_allowed('identity_access','AgeGateAttempt',"id"::text,'SELECT',ARRAY['id','userId','ipHash','deviceHash','region','result','birthYear','ageBand','blockedUntil','createdAt','mutationTransactionId']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_insert" ON "app"."age_gate_blocks" FOR INSERT TO wa_app_runtime WITH CHECK (platform_private.row_allowed('identity_access','AgeGateBlock',"id"::text,'INSERT',ARRAY['id','ipHash','deviceHash','reason','blockedUntil']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_select" ON "app"."age_gate_blocks" FOR SELECT TO wa_app_runtime USING (platform_private.row_allowed('identity_access','AgeGateBlock',"id"::text,'SELECT',ARRAY['id','ipHash','deviceHash','reason','blockedUntil','createdAt','mutationTransactionId']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_insert" ON "app"."access_audit_logs" FOR INSERT TO wa_app_runtime WITH CHECK (platform_private.row_allowed('audit_event_ledger','AccessAuditLog',"id"::text,'INSERT',ARRAY['id','actorUserId','targetType','targetId','action','sensitivity','accessDecision','requestId','ipHash','userAgent','previousHash','entryHash']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_select" ON "app"."access_audit_logs" FOR SELECT TO wa_app_runtime USING (platform_private.row_allowed('audit_event_ledger','AccessAuditLog',"id"::text,'SELECT',ARRAY['id','actorUserId','targetType','targetId','action','sensitivity','accessDecision','requestId','ipHash','userAgent','previousHash','entryHash','createdAt','mutationTransactionId']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_insert" ON "app"."users" FOR INSERT TO wa_app_runtime WITH CHECK (platform_private.row_allowed('identity_access','User',"id"::text,'INSERT',ARRAY['id','email','handle','displayName','avatarUrl','bio','city','state','country','isPublic','updatedAt','privacyErasedAt','privacyErasureStatus','revision','privacyGeneration']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_select" ON "app"."users" FOR SELECT TO wa_app_runtime USING (platform_private.row_allowed('identity_access','User',"id"::text,'SELECT',ARRAY['id','email','handle','displayName','avatarUrl','bio','city','state','country','isPublic','createdAt','updatedAt','privacyErasedAt','privacyErasureStatus','revision','privacyGeneration','mutationTransactionId']::text[],"revision"::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_update" ON "app"."users" FOR UPDATE TO wa_app_runtime USING (platform_private.row_allowed('identity_access','User',"id"::text,'UPDATE',ARRAY['@row']::text[],NULL::text,"mutation_transaction_id"::text)) WITH CHECK (platform_private.row_allowed('identity_access','User',"id"::text,'UPDATE',ARRAY['@row']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_insert" ON "app"."user_roles" FOR INSERT TO wa_app_runtime WITH CHECK (platform_private.row_allowed('identity_access','UserRole',"user_id"::text || ':' || "role"::text,'INSERT',ARRAY['userId','role','revision']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_select" ON "app"."user_roles" FOR SELECT TO wa_app_runtime USING (platform_private.row_allowed('identity_access','UserRole',"user_id"::text || ':' || "role"::text,'SELECT',ARRAY['userId','role','createdAt','revision','mutationTransactionId']::text[],"revision"::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_update" ON "app"."user_roles" FOR UPDATE TO wa_app_runtime USING (platform_private.row_allowed('identity_access','UserRole',"user_id"::text || ':' || "role"::text,'UPDATE',ARRAY['@row']::text[],NULL::text,"mutation_transaction_id"::text)) WITH CHECK (platform_private.row_allowed('identity_access','UserRole',"user_id"::text || ':' || "role"::text,'UPDATE',ARRAY['@row']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_select" ON "app"."professional_profiles" FOR SELECT TO wa_app_runtime USING (platform_private.row_allowed('professional_eligibility','ProfessionalProfile',"id"::text,'SELECT',ARRAY['id','userId','slug','headline','bio','websiteUrl','city','state','country','status','ratingAverage','ratingCount','stripeAccountId','stripeReady','onboardingCompleteAt','defaultCurrency','createdAt','updatedAt','suspendedForModerationAt','trustScore','verifiedAt','verificationExpiresAt','revision','privacyGeneration','mutationTransactionId']::text[],"revision"::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_insert" ON "app"."customer_profiles" FOR INSERT TO wa_app_runtime WITH CHECK (platform_private.row_allowed('customer_buyer_profile','CustomerProfile',"id"::text,'INSERT',ARRAY['id','userId','status','displayName','avatarMediaId','city','state','country','updatedAt','archivedAt','revision','privacyGeneration']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_select" ON "app"."customer_profiles" FOR SELECT TO wa_app_runtime USING (platform_private.row_allowed('customer_buyer_profile','CustomerProfile',"id"::text,'SELECT',ARRAY['id','userId','status','displayName','avatarMediaId','city','state','country','createdAt','updatedAt','archivedAt','revision','privacyGeneration','mutationTransactionId']::text[],"revision"::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_update" ON "app"."customer_profiles" FOR UPDATE TO wa_app_runtime USING (platform_private.row_allowed('customer_buyer_profile','CustomerProfile',"id"::text,'UPDATE',ARRAY['@row']::text[],NULL::text,"mutation_transaction_id"::text)) WITH CHECK (platform_private.row_allowed('customer_buyer_profile','CustomerProfile',"id"::text,'UPDATE',ARRAY['@row']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_select" ON "app"."candidate_profiles" FOR SELECT TO wa_app_runtime USING (platform_private.row_allowed('candidate_application_resume_privacy','CandidateProfile',"id"::text,'SELECT',ARRAY['id','userId','headline','portfolioUrl','availability','city','state','country','status','isVisible','createdAt','updatedAt','trustScore','verifiedAt','verificationExpiresAt','revision','privacyGeneration','discoveryPreferenceRevision','discoveryEnabledAt','mutationTransactionId']::text[],"revision"::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_insert" ON "app"."audit_events" FOR INSERT TO wa_app_runtime WITH CHECK (platform_private.row_allowed('audit_event_ledger','AuditEvent',"id"::text,'INSERT',ARRAY['id','actorUserId','entityType','entityId','action','metadata']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_select" ON "app"."audit_events" FOR SELECT TO wa_app_runtime USING (platform_private.row_allowed('audit_event_ledger','AuditEvent',"id"::text,'SELECT',ARRAY['id','actorUserId','entityType','entityId','action','metadata','createdAt','mutationTransactionId']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_insert" ON "app"."user_security_profiles" FOR INSERT TO wa_app_runtime WITH CHECK (platform_private.row_allowed('identity_access','UserSecurityProfile',"id"::text,'INSERT',ARRAY['id','userId','securityTier','phoneNumberEncrypted','phoneNumberHash','phoneVerifiedAt','phoneLastChangedAt','passkeysEnabled','smsMfaEnabled','backupPasswordConfigured','sensitiveActionMfaRequired','lastStepUpAt','lastSensitiveActionAt','lockedUntil','lockReason','updatedAt','revision','securityGeneration']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_select" ON "app"."user_security_profiles" FOR SELECT TO wa_app_runtime USING (platform_private.row_allowed('identity_access','UserSecurityProfile',"id"::text,'SELECT',ARRAY['id','userId','securityTier','phoneNumberEncrypted','phoneNumberHash','phoneVerifiedAt','phoneLastChangedAt','passkeysEnabled','smsMfaEnabled','backupPasswordConfigured','sensitiveActionMfaRequired','lastStepUpAt','lastSensitiveActionAt','lockedUntil','lockReason','createdAt','updatedAt','revision','securityGeneration','mutationTransactionId']::text[],"revision"::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_update" ON "app"."user_security_profiles" FOR UPDATE TO wa_app_runtime USING (platform_private.row_allowed('identity_access','UserSecurityProfile',"id"::text,'UPDATE',ARRAY['@row']::text[],NULL::text,"mutation_transaction_id"::text)) WITH CHECK (platform_private.row_allowed('identity_access','UserSecurityProfile',"id"::text,'UPDATE',ARRAY['@row']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_insert" ON "app"."auth_provider_accounts" FOR INSERT TO wa_app_runtime WITH CHECK (platform_private.row_allowed('identity_access','AuthProviderAccount',"id"::text,'INSERT',ARRAY['id','userId','securityProfileId','providerType','providerUserId','providerAccountId','email','emailVerifiedAt','status','linkedAt','lastUsedAt','revokedAt','updatedAt','revision']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_select" ON "app"."auth_provider_accounts" FOR SELECT TO wa_app_runtime USING (platform_private.row_allowed('identity_access','AuthProviderAccount',"id"::text,'SELECT',ARRAY['id','userId','securityProfileId','providerType','providerUserId','providerAccountId','email','emailVerifiedAt','status','linkedAt','lastUsedAt','revokedAt','createdAt','updatedAt','revision','mutationTransactionId']::text[],"revision"::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_update" ON "app"."auth_provider_accounts" FOR UPDATE TO wa_app_runtime USING (platform_private.row_allowed('identity_access','AuthProviderAccount',"id"::text,'UPDATE',ARRAY['@row']::text[],NULL::text,"mutation_transaction_id"::text)) WITH CHECK (platform_private.row_allowed('identity_access','AuthProviderAccount',"id"::text,'UPDATE',ARRAY['@row']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_insert" ON "app"."track_plans" FOR INSERT TO wa_app_runtime WITH CHECK (platform_private.row_allowed('track_subscription_entitlement','TrackPlan',"id"::text,'INSERT',ARRAY['id','track','key','name','status','billingModel','monthlyPriceCents','currency','description','displayOrder','metadata','updatedAt','revision','version','contentHash']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_select" ON "app"."track_plans" FOR SELECT TO wa_app_runtime USING (platform_private.row_allowed('track_subscription_entitlement','TrackPlan',"id"::text,'SELECT',ARRAY['id','track','key','name','status','billingModel','monthlyPriceCents','currency','description','displayOrder','metadata','createdAt','updatedAt','revision','version','contentHash','mutationTransactionId']::text[],"revision"::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_update" ON "app"."track_plans" FOR UPDATE TO wa_app_runtime USING (platform_private.row_allowed('track_subscription_entitlement','TrackPlan',"id"::text,'UPDATE',ARRAY['@row']::text[],NULL::text,"mutation_transaction_id"::text)) WITH CHECK (platform_private.row_allowed('track_subscription_entitlement','TrackPlan',"id"::text,'UPDATE',ARRAY['@row']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_worker_select" ON "app"."track_plans" FOR SELECT TO wa_worker USING (platform_private.row_allowed('track_subscription_entitlement','TrackPlan',"id"::text,'SELECT',ARRAY['id','track','key','status','billingModel','version','contentHash','revision']::text[],"revision"::text,"mutation_transaction_id"::text) AND platform_private.worker_track_allowed('TrackPlan',jsonb_build_object('id',"id",'track',"track",'key',"key",'status',"status",'billing_model',"billing_model",'revision',"revision",'version',"version",'content_hash',"content_hash"),'SELECT'));

CREATE POLICY "p_app_runtime_insert" ON "app"."track_entitlement_definitions" FOR INSERT TO wa_app_runtime WITH CHECK (platform_private.row_allowed('track_subscription_entitlement','TrackEntitlementDefinition',"id"::text,'INSERT',ARRAY['id','key','label','description','valueType','track','isActive','updatedAt','revision']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_select" ON "app"."track_entitlement_definitions" FOR SELECT TO wa_app_runtime USING (platform_private.row_allowed('track_subscription_entitlement','TrackEntitlementDefinition',"id"::text,'SELECT',ARRAY['id','key','label','description','valueType','track','isActive','createdAt','updatedAt','revision','mutationTransactionId']::text[],"revision"::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_update" ON "app"."track_entitlement_definitions" FOR UPDATE TO wa_app_runtime USING (platform_private.row_allowed('track_subscription_entitlement','TrackEntitlementDefinition',"id"::text,'UPDATE',ARRAY['@row']::text[],NULL::text,"mutation_transaction_id"::text)) WITH CHECK (platform_private.row_allowed('track_subscription_entitlement','TrackEntitlementDefinition',"id"::text,'UPDATE',ARRAY['@row']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_worker_select" ON "app"."track_entitlement_definitions" FOR SELECT TO wa_worker USING (platform_private.row_allowed('track_subscription_entitlement','TrackEntitlementDefinition',"id"::text,'SELECT',ARRAY['id','key','valueType','track','isActive','revision']::text[],"revision"::text,"mutation_transaction_id"::text) AND platform_private.worker_track_allowed('TrackEntitlementDefinition',jsonb_build_object('id',"id",'key',"key",'value_type',"value_type",'track',"track",'is_active',"is_active",'revision',"revision"),'SELECT'));

CREATE POLICY "p_app_runtime_insert" ON "app"."track_plan_entitlements" FOR INSERT TO wa_app_runtime WITH CHECK (platform_private.row_allowed('track_subscription_entitlement','TrackPlanEntitlement',"id"::text,'INSERT',ARRAY['id','planId','entitlementId','valueType','booleanValue','intValue','decimalValue','stringValue','jsonValue','usagePeriod','updatedAt','revision']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_select" ON "app"."track_plan_entitlements" FOR SELECT TO wa_app_runtime USING (platform_private.row_allowed('track_subscription_entitlement','TrackPlanEntitlement',"id"::text,'SELECT',ARRAY['id','planId','entitlementId','valueType','booleanValue','intValue','decimalValue','stringValue','jsonValue','usagePeriod','createdAt','updatedAt','revision','mutationTransactionId']::text[],"revision"::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_update" ON "app"."track_plan_entitlements" FOR UPDATE TO wa_app_runtime USING (platform_private.row_allowed('track_subscription_entitlement','TrackPlanEntitlement',"id"::text,'UPDATE',ARRAY['@row']::text[],NULL::text,"mutation_transaction_id"::text)) WITH CHECK (platform_private.row_allowed('track_subscription_entitlement','TrackPlanEntitlement',"id"::text,'UPDATE',ARRAY['@row']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_worker_select" ON "app"."track_plan_entitlements" FOR SELECT TO wa_worker USING (platform_private.row_allowed('track_subscription_entitlement','TrackPlanEntitlement',"id"::text,'SELECT',ARRAY['id','planId','entitlementId','valueType','booleanValue','intValue','decimalValue','stringValue','usagePeriod','revision']::text[],"revision"::text,"mutation_transaction_id"::text) AND platform_private.worker_track_allowed('TrackPlanEntitlement',jsonb_build_object('id',"id",'plan_id',"plan_id",'entitlement_id',"entitlement_id",'value_type',"value_type",'boolean_value',"boolean_value",'int_value',"int_value",'decimal_value',"decimal_value",'string_value',"string_value",'usage_period',"usage_period",'revision',"revision"),'SELECT'));

CREATE POLICY "p_app_runtime_insert" ON "app"."track_subscriptions" FOR INSERT TO wa_app_runtime WITH CHECK (platform_private.row_allowed('track_subscription_entitlement','TrackSubscription',"id"::text,'INSERT',ARRAY['id','userId','planId','track','customerProfileId','candidateProfileId','professionalProfileId','status','provider','providerCustomerId','providerSubscriptionId','providerPriceId','currentPeriodStart','currentPeriodEnd','trialEndsAt','cancelledAt','endedAt','updatedAt','revision']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_select" ON "app"."track_subscriptions" FOR SELECT TO wa_app_runtime USING (platform_private.row_allowed('track_subscription_entitlement','TrackSubscription',"id"::text,'SELECT',ARRAY['id','userId','planId','track','customerProfileId','candidateProfileId','professionalProfileId','status','provider','providerCustomerId','providerSubscriptionId','providerPriceId','currentPeriodStart','currentPeriodEnd','trialEndsAt','cancelledAt','endedAt','createdAt','updatedAt','revision','mutationTransactionId']::text[],"revision"::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_update" ON "app"."track_subscriptions" FOR UPDATE TO wa_app_runtime USING (platform_private.row_allowed('track_subscription_entitlement','TrackSubscription',"id"::text,'UPDATE',ARRAY['@row']::text[],NULL::text,"mutation_transaction_id"::text)) WITH CHECK (platform_private.row_allowed('track_subscription_entitlement','TrackSubscription',"id"::text,'UPDATE',ARRAY['@row']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_worker_insert" ON "app"."track_subscriptions" FOR INSERT TO wa_worker WITH CHECK (platform_private.row_allowed('track_subscription_entitlement','TrackSubscription',"id"::text,'INSERT',ARRAY['id','userId','planId','track','customerProfileId','candidateProfileId','professionalProfileId','status','provider']::text[],NULL::text,"mutation_transaction_id"::text) AND platform_private.worker_track_allowed('TrackSubscription',jsonb_build_object('id',"id",'user_id',"user_id",'plan_id',"plan_id",'track',"track",'customer_profile_id',"customer_profile_id",'candidate_profile_id',"candidate_profile_id",'professional_profile_id',"professional_profile_id",'status',"status",'provider',"provider",'current_period_start',"current_period_start",'current_period_end',"current_period_end",'ended_at',"ended_at",'revision',"revision"),'INSERT'));

CREATE POLICY "p_worker_select" ON "app"."track_subscriptions" FOR SELECT TO wa_worker USING (platform_private.row_allowed('track_subscription_entitlement','TrackSubscription',"id"::text,'SELECT',ARRAY['id','userId','planId','track','customerProfileId','candidateProfileId','professionalProfileId','status','provider','currentPeriodStart','currentPeriodEnd','endedAt','revision']::text[],"revision"::text,"mutation_transaction_id"::text) AND platform_private.worker_track_allowed('TrackSubscription',jsonb_build_object('id',"id",'user_id',"user_id",'plan_id',"plan_id",'track',"track",'customer_profile_id',"customer_profile_id",'candidate_profile_id',"candidate_profile_id",'professional_profile_id',"professional_profile_id",'status',"status",'provider',"provider",'current_period_start',"current_period_start",'current_period_end',"current_period_end",'ended_at',"ended_at",'revision',"revision"),'SELECT'));

CREATE POLICY "p_app_runtime_insert" ON "app"."track_entitlement_grants" FOR INSERT TO wa_app_runtime WITH CHECK (platform_private.row_allowed('track_subscription_entitlement','TrackEntitlementGrant',"id"::text,'INSERT',ARRAY['id','userId','subscriptionId','entitlementId','track','customerProfileId','candidateProfileId','professionalProfileId','status','valueType','booleanValue','intValue','decimalValue','stringValue','jsonValue','startsAt','expiresAt','revokedAt','revokeReason','sourcePlanId','sourceEventId','updatedAt','revision']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_select" ON "app"."track_entitlement_grants" FOR SELECT TO wa_app_runtime USING (platform_private.row_allowed('track_subscription_entitlement','TrackEntitlementGrant',"id"::text,'SELECT',ARRAY['id','userId','subscriptionId','entitlementId','track','customerProfileId','candidateProfileId','professionalProfileId','status','valueType','booleanValue','intValue','decimalValue','stringValue','jsonValue','startsAt','expiresAt','revokedAt','revokeReason','sourcePlanId','sourceEventId','createdAt','updatedAt','revision','mutationTransactionId']::text[],"revision"::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_update" ON "app"."track_entitlement_grants" FOR UPDATE TO wa_app_runtime USING (platform_private.row_allowed('track_subscription_entitlement','TrackEntitlementGrant',"id"::text,'UPDATE',ARRAY['@row']::text[],NULL::text,"mutation_transaction_id"::text)) WITH CHECK (platform_private.row_allowed('track_subscription_entitlement','TrackEntitlementGrant',"id"::text,'UPDATE',ARRAY['@row']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_worker_insert" ON "app"."track_entitlement_grants" FOR INSERT TO wa_worker WITH CHECK (platform_private.row_allowed('track_subscription_entitlement','TrackEntitlementGrant',"id"::text,'INSERT',ARRAY['id','userId','subscriptionId','entitlementId','track','customerProfileId','candidateProfileId','professionalProfileId','status','valueType','booleanValue','intValue','decimalValue','stringValue','startsAt','sourcePlanId','sourceEventId']::text[],NULL::text,"mutation_transaction_id"::text) AND platform_private.worker_track_allowed('TrackEntitlementGrant',jsonb_build_object('id',"id",'user_id',"user_id",'subscription_id',"subscription_id",'entitlement_id',"entitlement_id",'track',"track",'customer_profile_id',"customer_profile_id",'candidate_profile_id',"candidate_profile_id",'professional_profile_id',"professional_profile_id",'status',"status",'value_type',"value_type",'boolean_value',"boolean_value",'int_value',"int_value",'decimal_value',"decimal_value",'string_value',"string_value",'starts_at',"starts_at",'expires_at',"expires_at",'revoked_at',"revoked_at",'source_plan_id',"source_plan_id",'source_event_id',"source_event_id",'revision',"revision"),'INSERT'));

CREATE POLICY "p_worker_select" ON "app"."track_entitlement_grants" FOR SELECT TO wa_worker USING (platform_private.row_allowed('track_subscription_entitlement','TrackEntitlementGrant',"id"::text,'SELECT',ARRAY['id','userId','subscriptionId','entitlementId','track','customerProfileId','candidateProfileId','professionalProfileId','status','valueType','booleanValue','intValue','decimalValue','stringValue','startsAt','expiresAt','revokedAt','sourcePlanId','sourceEventId','revision']::text[],"revision"::text,"mutation_transaction_id"::text) AND platform_private.worker_track_allowed('TrackEntitlementGrant',jsonb_build_object('id',"id",'user_id',"user_id",'subscription_id',"subscription_id",'entitlement_id',"entitlement_id",'track',"track",'customer_profile_id',"customer_profile_id",'candidate_profile_id',"candidate_profile_id",'professional_profile_id',"professional_profile_id",'status',"status",'value_type',"value_type",'boolean_value',"boolean_value",'int_value',"int_value",'decimal_value',"decimal_value",'string_value',"string_value",'starts_at',"starts_at",'expires_at',"expires_at",'revoked_at',"revoked_at",'source_plan_id',"source_plan_id",'source_event_id',"source_event_id",'revision',"revision"),'SELECT'));

CREATE POLICY "p_app_runtime_insert" ON "app"."track_usage_events" FOR INSERT TO wa_app_runtime WITH CHECK (platform_private.row_allowed('track_subscription_entitlement','TrackUsageEvent',"id"::text,'INSERT',ARRAY['id','userId','subscriptionId','entitlementGrantId','entitlementId','track','type','customerProfileId','candidateProfileId','professionalProfileId','targetType','targetId','quantity','occurredAt','metadata','semanticEffectKey','sourceRevision','sourceOwner','sourceId','acceptedAt','periodStart','periodEnd','effectReceiptId']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_select" ON "app"."track_usage_events" FOR SELECT TO wa_app_runtime USING (platform_private.row_allowed('track_subscription_entitlement','TrackUsageEvent',"id"::text,'SELECT',ARRAY['id','userId','subscriptionId','entitlementGrantId','entitlementId','track','type','customerProfileId','candidateProfileId','professionalProfileId','targetType','targetId','quantity','occurredAt','metadata','semanticEffectKey','sourceRevision','sourceOwner','sourceId','acceptedAt','periodStart','periodEnd','effectReceiptId','mutationTransactionId']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_insert" ON "app"."track_usage_counters" FOR INSERT TO wa_app_runtime WITH CHECK (platform_private.row_allowed('track_subscription_entitlement','TrackUsageCounter',"id"::text,'INSERT',ARRAY['id','userId','subscriptionId','entitlementGrantId','entitlementId','track','period','customerProfileId','candidateProfileId','professionalProfileId','periodStart','periodEnd','usedQuantity','limitQuantity','updatedAt','revision','sourceRevision']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_select" ON "app"."track_usage_counters" FOR SELECT TO wa_app_runtime USING (platform_private.row_allowed('track_subscription_entitlement','TrackUsageCounter',"id"::text,'SELECT',ARRAY['id','userId','subscriptionId','entitlementGrantId','entitlementId','track','period','customerProfileId','candidateProfileId','professionalProfileId','periodStart','periodEnd','usedQuantity','limitQuantity','updatedAt','createdAt','revision','sourceRevision','mutationTransactionId']::text[],"revision"::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_update" ON "app"."track_usage_counters" FOR UPDATE TO wa_app_runtime USING (platform_private.row_allowed('track_subscription_entitlement','TrackUsageCounter',"id"::text,'UPDATE',ARRAY['@row']::text[],NULL::text,"mutation_transaction_id"::text)) WITH CHECK (platform_private.row_allowed('track_subscription_entitlement','TrackUsageCounter',"id"::text,'UPDATE',ARRAY['@row']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_insert" ON "app"."track_subscription_events" FOR INSERT TO wa_app_runtime WITH CHECK (platform_private.row_allowed('track_subscription_entitlement','TrackSubscriptionEvent',"id"::text,'INSERT',ARRAY['id','subscriptionId','planId','userId','name','fromStatus','toStatus','provider','providerEventId','metadata']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_select" ON "app"."track_subscription_events" FOR SELECT TO wa_app_runtime USING (platform_private.row_allowed('track_subscription_entitlement','TrackSubscriptionEvent',"id"::text,'SELECT',ARRAY['id','subscriptionId','planId','userId','name','fromStatus','toStatus','provider','providerEventId','metadata','createdAt','mutationTransactionId']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_worker_insert" ON "app"."track_subscription_events" FOR INSERT TO wa_worker WITH CHECK (platform_private.row_allowed('track_subscription_entitlement','TrackSubscriptionEvent',"id"::text,'INSERT',ARRAY['id','subscriptionId','planId','userId','name','fromStatus','toStatus','provider']::text[],NULL::text,"mutation_transaction_id"::text) AND platform_private.worker_track_allowed('TrackSubscriptionEvent',jsonb_build_object('id',"id",'subscription_id',"subscription_id",'plan_id',"plan_id",'user_id',"user_id",'name',"name",'from_status',"from_status",'to_status',"to_status",'provider',"provider"),'INSERT'));

CREATE POLICY "p_app_runtime_insert" ON "app"."consent_content_revision" FOR INSERT TO wa_app_runtime WITH CHECK (platform_private.row_allowed('consent_disclosure','ConsentContentRevision',"id"::text,'INSERT',ARRAY['id','type','version','locale','jurisdictionScope','contentText','contentHash','reviewState','legalApprovalRef','effectiveFrom','effectiveUntil']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_select" ON "app"."consent_content_revision" FOR SELECT TO wa_app_runtime USING (platform_private.row_allowed('consent_disclosure','ConsentContentRevision',"id"::text,'SELECT',ARRAY['id','type','version','locale','jurisdictionScope','contentText','contentHash','reviewState','legalApprovalRef','effectiveFrom','effectiveUntil','createdAt','mutationTransactionId']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_insert" ON "app"."consent_presentation" FOR INSERT TO wa_app_runtime WITH CHECK (platform_private.row_allowed('consent_disclosure','ConsentPresentation',"id"::text,'INSERT',ARRAY['id','contentRevisionId','userId','actionOwner','action','renderVersion','renderedText','renderedHash','contextOwner','contextKind','contextId']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_select" ON "app"."consent_presentation" FOR SELECT TO wa_app_runtime USING (platform_private.row_allowed('consent_disclosure','ConsentPresentation',"id"::text,'SELECT',ARRAY['id','contentRevisionId','userId','actionOwner','action','renderVersion','renderedText','renderedHash','contextOwner','contextKind','contextId','createdAt','mutationTransactionId']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_insert" ON "app"."consent_disposition" FOR INSERT TO wa_app_runtime WITH CHECK (platform_private.row_allowed('consent_disclosure','ConsentDisposition',"id"::text,'INSERT',ARRAY['id','proofId','userId','presentationId','kind','semanticKey','fingerprint']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_select" ON "app"."consent_disposition" FOR SELECT TO wa_app_runtime USING (platform_private.row_allowed('consent_disclosure','ConsentDisposition',"id"::text,'SELECT',ARRAY['id','proofId','userId','presentationId','kind','semanticKey','fingerprint','createdAt','mutationTransactionId']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_insert" ON "platform"."runtime_command_receipt" FOR INSERT TO wa_app_runtime WITH CHECK (platform_private.row_allowed("owner_module_id",'RuntimeCommandReceipt',"id"::text,'INSERT',ARRAY['id','ownerModuleId','operation','subjectScope','semanticKey','fingerprint','state','sourceRevision','resultSchemaId','resultSchemaVersion','resultDigest','resultBody']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_select" ON "platform"."runtime_command_receipt" FOR SELECT TO wa_app_runtime USING (platform_private.row_allowed("owner_module_id",'RuntimeCommandReceipt',"id"::text,'SELECT',ARRAY['id','ownerModuleId','operation','subjectScope','semanticKey','fingerprint','state','sourceRevision','resultSchemaId','resultSchemaVersion','resultDigest','resultBody','createdAt','mutationTransactionId']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_update" ON "platform"."runtime_command_receipt" FOR UPDATE TO wa_app_runtime USING (platform_private.row_allowed("owner_module_id",'RuntimeCommandReceipt',"id"::text,'UPDATE',ARRAY['@row']::text[],NULL::text,"mutation_transaction_id"::text)) WITH CHECK (platform_private.row_allowed("owner_module_id",'RuntimeCommandReceipt',"id"::text,'UPDATE',ARRAY['@row']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_worker_insert" ON "platform"."runtime_command_receipt" FOR INSERT TO wa_worker WITH CHECK (platform_private.row_allowed("owner_module_id",'RuntimeCommandReceipt',"id"::text,'INSERT',ARRAY['id','ownerModuleId','operation','subjectScope','semanticKey','fingerprint','state','sourceRevision','resultSchemaId','resultSchemaVersion','resultDigest','resultBody']::text[],NULL::text,"mutation_transaction_id"::text) AND platform_private.worker_track_allowed('RuntimeCommandReceipt',jsonb_build_object('id',"id",'owner_module_id',"owner_module_id",'operation',"operation",'subject_scope',"subject_scope",'semantic_key',"semantic_key",'fingerprint',"fingerprint",'state',"state",'source_revision',"source_revision",'result_schema_id',"result_schema_id",'result_schema_version',"result_schema_version",'result_digest',"result_digest",'result_body',"result_body",'created_at',"created_at",'mutation_transaction_id',"mutation_transaction_id"),'INSERT'));

CREATE POLICY "p_worker_select" ON "platform"."runtime_command_receipt" FOR SELECT TO wa_worker USING (platform_private.row_allowed("owner_module_id",'RuntimeCommandReceipt',"id"::text,'SELECT',ARRAY['id','ownerModuleId','operation','subjectScope','semanticKey','fingerprint','state','sourceRevision','resultSchemaId','resultSchemaVersion','resultDigest','resultBody','createdAt','mutationTransactionId']::text[],NULL::text,"mutation_transaction_id"::text) AND platform_private.worker_track_allowed('RuntimeCommandReceipt',jsonb_build_object('id',"id",'owner_module_id',"owner_module_id",'operation',"operation",'subject_scope',"subject_scope",'semantic_key',"semantic_key",'fingerprint',"fingerprint",'state',"state",'source_revision',"source_revision",'result_schema_id',"result_schema_id",'result_schema_version',"result_schema_version",'result_digest',"result_digest",'result_body',"result_body",'created_at',"created_at",'mutation_transaction_id',"mutation_transaction_id"),'SELECT'));

CREATE POLICY "p_worker_update" ON "platform"."runtime_command_receipt" FOR UPDATE TO wa_worker USING (platform_private.row_allowed("owner_module_id",'RuntimeCommandReceipt',"id"::text,'UPDATE',ARRAY['@row']::text[],NULL::text,"mutation_transaction_id"::text) AND platform_private.worker_track_allowed('RuntimeCommandReceipt',jsonb_build_object('id',"id",'owner_module_id',"owner_module_id",'operation',"operation",'subject_scope',"subject_scope",'semantic_key',"semantic_key",'fingerprint',"fingerprint",'state',"state",'source_revision',"source_revision",'result_schema_id',"result_schema_id",'result_schema_version',"result_schema_version",'result_digest',"result_digest",'result_body',"result_body",'created_at',"created_at",'mutation_transaction_id',"mutation_transaction_id"),'UPDATE')) WITH CHECK (platform_private.row_allowed("owner_module_id",'RuntimeCommandReceipt',"id"::text,'UPDATE',ARRAY['@row']::text[],NULL::text,"mutation_transaction_id"::text) AND platform_private.worker_track_allowed('RuntimeCommandReceipt',jsonb_build_object('id',"id",'owner_module_id',"owner_module_id",'operation',"operation",'subject_scope',"subject_scope",'semantic_key',"semantic_key",'fingerprint',"fingerprint",'state',"state",'source_revision',"source_revision",'result_schema_id',"result_schema_id",'result_schema_version',"result_schema_version",'result_digest',"result_digest",'result_body',"result_body",'created_at',"created_at",'mutation_transaction_id',"mutation_transaction_id"),'UPDATE'));

CREATE POLICY "p_app_runtime_insert" ON "platform"."runtime_outbox_message" FOR INSERT TO wa_app_runtime WITH CHECK (platform_private.row_allowed("producer_owner",'RuntimeOutboxMessage',"id"::text,'INSERT',ARRAY['id','commandReceiptId','kind','producerOwner','aggregateKind','aggregateId','sourceRevision','sourceGeneration','ordinal','name','schemaVersion','payloadSchemaId','payloadHash','payload','correlationId','causationId','correctionOfId','occurredAt','effectiveAt']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_select" ON "platform"."runtime_outbox_message" FOR SELECT TO wa_app_runtime USING (platform_private.row_allowed("producer_owner",'RuntimeOutboxMessage',"id"::text,'SELECT',ARRAY['id','commandReceiptId','kind','producerOwner','aggregateKind','aggregateId','sourceRevision','sourceGeneration','ordinal','name','schemaVersion','payloadSchemaId','payloadHash','payload','correlationId','causationId','correctionOfId','occurredAt','effectiveAt','createdAt','mutationTransactionId']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_worker_insert" ON "platform"."runtime_outbox_message" FOR INSERT TO wa_worker WITH CHECK (platform_private.row_allowed("producer_owner",'RuntimeOutboxMessage',"id"::text,'INSERT',ARRAY['id','commandReceiptId','kind','producerOwner','aggregateKind','aggregateId','sourceRevision','sourceGeneration','ordinal','name','schemaVersion','payloadSchemaId','payloadHash','payload','correlationId','causationId','correctionOfId','occurredAt','effectiveAt']::text[],NULL::text,"mutation_transaction_id"::text) AND platform_private.worker_track_allowed('RuntimeOutboxMessage',jsonb_build_object('id',"id",'command_receipt_id',"command_receipt_id",'kind',"kind",'producer_owner',"producer_owner",'aggregate_kind',"aggregate_kind",'aggregate_id',"aggregate_id",'source_revision',"source_revision",'source_generation',"source_generation",'ordinal',"ordinal",'name',"name",'schema_version',"schema_version",'payload_schema_id',"payload_schema_id",'payload_hash',"payload_hash",'payload',"payload",'correlation_id',"correlation_id",'causation_id',"causation_id",'correction_of_id',"correction_of_id",'occurred_at',"occurred_at",'effective_at',"effective_at",'created_at',"created_at",'mutation_transaction_id',"mutation_transaction_id"),'INSERT'));

CREATE POLICY "p_worker_select" ON "platform"."runtime_outbox_message" FOR SELECT TO wa_worker USING (platform_private.row_allowed("producer_owner",'RuntimeOutboxMessage',"id"::text,'SELECT',ARRAY['id','commandReceiptId','kind','producerOwner','aggregateKind','aggregateId','sourceRevision','sourceGeneration','ordinal','name','schemaVersion','payloadSchemaId','payloadHash','payload','correlationId','causationId','correctionOfId','occurredAt','effectiveAt','createdAt','mutationTransactionId']::text[],NULL::text,"mutation_transaction_id"::text) AND platform_private.worker_track_allowed('RuntimeOutboxMessage',jsonb_build_object('id',"id",'command_receipt_id',"command_receipt_id",'kind',"kind",'producer_owner',"producer_owner",'aggregate_kind',"aggregate_kind",'aggregate_id',"aggregate_id",'source_revision',"source_revision",'source_generation',"source_generation",'ordinal',"ordinal",'name',"name",'schema_version',"schema_version",'payload_schema_id',"payload_schema_id",'payload_hash',"payload_hash",'payload',"payload",'correlation_id',"correlation_id",'causation_id',"causation_id",'correction_of_id',"correction_of_id",'occurred_at',"occurred_at",'effective_at',"effective_at",'created_at',"created_at",'mutation_transaction_id',"mutation_transaction_id"),'SELECT'));

CREATE POLICY "p_app_runtime_insert" ON "platform"."runtime_effect_receipt" FOR INSERT TO wa_app_runtime WITH CHECK (platform_private.row_allowed("owner_module_id",'RuntimeEffectReceipt',"id"::text,'INSERT',ARRAY['id','commandReceiptId','ownerModuleId','operation','subjectScope','semanticEffectKey','fingerprint','state','sourceRevision','fence','resultSchemaId','resultHash','committedAt']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_select" ON "platform"."runtime_effect_receipt" FOR SELECT TO wa_app_runtime USING (platform_private.row_allowed("owner_module_id",'RuntimeEffectReceipt',"id"::text,'SELECT',ARRAY['id','commandReceiptId','ownerModuleId','operation','subjectScope','semanticEffectKey','fingerprint','state','sourceRevision','fence','resultSchemaId','resultHash','committedAt','createdAt','mutationTransactionId']::text[],"fence"::text,"mutation_transaction_id"::text));

CREATE POLICY "p_worker_insert" ON "platform"."runtime_effect_receipt" FOR INSERT TO wa_worker WITH CHECK (platform_private.row_allowed("owner_module_id",'RuntimeEffectReceipt',"id"::text,'INSERT',ARRAY['id','commandReceiptId','ownerModuleId','operation','subjectScope','semanticEffectKey','fingerprint','state','sourceRevision','fence','resultSchemaId','resultHash','committedAt']::text[],NULL::text,"mutation_transaction_id"::text) AND platform_private.worker_track_allowed('RuntimeEffectReceipt',jsonb_build_object('id',"id",'command_receipt_id',"command_receipt_id",'owner_module_id',"owner_module_id",'operation',"operation",'subject_scope',"subject_scope",'semantic_effect_key',"semantic_effect_key",'fingerprint',"fingerprint",'state',"state",'source_revision',"source_revision",'fence',"fence",'result_schema_id',"result_schema_id",'result_hash',"result_hash",'committed_at',"committed_at",'created_at',"created_at",'mutation_transaction_id',"mutation_transaction_id"),'INSERT'));

CREATE POLICY "p_worker_select" ON "platform"."runtime_effect_receipt" FOR SELECT TO wa_worker USING (platform_private.row_allowed("owner_module_id",'RuntimeEffectReceipt',"id"::text,'SELECT',ARRAY['id','commandReceiptId','ownerModuleId','operation','subjectScope','semanticEffectKey','fingerprint','state','sourceRevision','fence','resultSchemaId','resultHash','committedAt','createdAt','mutationTransactionId']::text[],"fence"::text,"mutation_transaction_id"::text) AND platform_private.worker_track_allowed('RuntimeEffectReceipt',jsonb_build_object('id',"id",'command_receipt_id',"command_receipt_id",'owner_module_id',"owner_module_id",'operation',"operation",'subject_scope',"subject_scope",'semantic_effect_key',"semantic_effect_key",'fingerprint',"fingerprint",'state',"state",'source_revision',"source_revision",'fence',"fence",'result_schema_id',"result_schema_id",'result_hash',"result_hash",'committed_at',"committed_at",'created_at',"created_at",'mutation_transaction_id',"mutation_transaction_id"),'SELECT'));

CREATE POLICY "p_app_runtime_insert" ON "platform"."runtime_work_item" FOR INSERT TO wa_app_runtime WITH CHECK (platform_private.row_allowed('platform_integration_owner','RuntimeWorkItem',"id"::text,'INSERT',ARRAY['id','outboxMessageId','handlerName','semanticWorkKey','state','fence','leaseTokenHash','leaseExpiresAt','attemptCount','nextAttemptAt','effectReceiptId']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_select" ON "platform"."runtime_work_item" FOR SELECT TO wa_app_runtime USING (platform_private.row_allowed('platform_integration_owner','RuntimeWorkItem',"id"::text,'SELECT',ARRAY['id','outboxMessageId','handlerName','semanticWorkKey','state','fence','leaseTokenHash','leaseExpiresAt','attemptCount','nextAttemptAt','effectReceiptId','createdAt','mutationTransactionId']::text[],"fence"::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_update" ON "platform"."runtime_work_item" FOR UPDATE TO wa_app_runtime USING (platform_private.row_allowed('platform_integration_owner','RuntimeWorkItem',"id"::text,'UPDATE',ARRAY['@row']::text[],NULL::text,"mutation_transaction_id"::text)) WITH CHECK (platform_private.row_allowed('platform_integration_owner','RuntimeWorkItem',"id"::text,'UPDATE',ARRAY['@row']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_worker_insert" ON "platform"."runtime_work_item" FOR INSERT TO wa_worker WITH CHECK (platform_private.row_allowed('platform_integration_owner','RuntimeWorkItem',"id"::text,'INSERT',ARRAY['id','outboxMessageId','handlerName','semanticWorkKey','state','fence','leaseTokenHash','leaseExpiresAt','attemptCount','nextAttemptAt','effectReceiptId']::text[],NULL::text,"mutation_transaction_id"::text) AND platform_private.worker_track_allowed('RuntimeWorkItem',jsonb_build_object('id',"id",'outbox_message_id',"outbox_message_id",'handler_name',"handler_name",'semantic_work_key',"semantic_work_key",'state',"state",'fence',"fence",'lease_token_hash',"lease_token_hash",'lease_expires_at',"lease_expires_at",'attempt_count',"attempt_count",'next_attempt_at',"next_attempt_at",'effect_receipt_id',"effect_receipt_id",'created_at',"created_at",'mutation_transaction_id',"mutation_transaction_id"),'INSERT'));

CREATE POLICY "p_worker_select" ON "platform"."runtime_work_item" FOR SELECT TO wa_worker USING (platform_private.row_allowed('platform_integration_owner','RuntimeWorkItem',"id"::text,'SELECT',ARRAY['id','outboxMessageId','handlerName','semanticWorkKey','state','fence','leaseTokenHash','leaseExpiresAt','attemptCount','nextAttemptAt','effectReceiptId','createdAt','mutationTransactionId']::text[],"fence"::text,"mutation_transaction_id"::text) AND platform_private.worker_track_allowed('RuntimeWorkItem',jsonb_build_object('id',"id",'outbox_message_id',"outbox_message_id",'handler_name',"handler_name",'semantic_work_key',"semantic_work_key",'state',"state",'fence',"fence",'lease_token_hash',"lease_token_hash",'lease_expires_at',"lease_expires_at",'attempt_count',"attempt_count",'next_attempt_at',"next_attempt_at",'effect_receipt_id',"effect_receipt_id",'created_at',"created_at",'mutation_transaction_id',"mutation_transaction_id"),'SELECT'));

CREATE POLICY "p_worker_update" ON "platform"."runtime_work_item" FOR UPDATE TO wa_worker USING (platform_private.row_allowed('platform_integration_owner','RuntimeWorkItem',"id"::text,'UPDATE',ARRAY['@row']::text[],NULL::text,"mutation_transaction_id"::text) AND platform_private.worker_track_allowed('RuntimeWorkItem',jsonb_build_object('id',"id",'outbox_message_id',"outbox_message_id",'handler_name',"handler_name",'semantic_work_key',"semantic_work_key",'state',"state",'fence',"fence",'lease_token_hash',"lease_token_hash",'lease_expires_at',"lease_expires_at",'attempt_count',"attempt_count",'next_attempt_at',"next_attempt_at",'effect_receipt_id',"effect_receipt_id",'created_at',"created_at",'mutation_transaction_id',"mutation_transaction_id"),'UPDATE')) WITH CHECK (platform_private.row_allowed('platform_integration_owner','RuntimeWorkItem',"id"::text,'UPDATE',ARRAY['@row']::text[],NULL::text,"mutation_transaction_id"::text) AND platform_private.worker_track_allowed('RuntimeWorkItem',jsonb_build_object('id',"id",'outbox_message_id',"outbox_message_id",'handler_name',"handler_name",'semantic_work_key',"semantic_work_key",'state',"state",'fence',"fence",'lease_token_hash',"lease_token_hash",'lease_expires_at',"lease_expires_at",'attempt_count',"attempt_count",'next_attempt_at',"next_attempt_at",'effect_receipt_id',"effect_receipt_id",'created_at',"created_at",'mutation_transaction_id',"mutation_transaction_id"),'UPDATE'));

CREATE POLICY "p_app_runtime_insert" ON "platform"."runtime_attempt" FOR INSERT TO wa_app_runtime WITH CHECK (platform_private.row_allowed('platform_integration_owner','RuntimeAttempt',"id"::text,'INSERT',ARRAY['id','workItemId','attemptNumber','fence','workerId','result','reasonCode','startedAt','finishedAt']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_select" ON "platform"."runtime_attempt" FOR SELECT TO wa_app_runtime USING (platform_private.row_allowed('platform_integration_owner','RuntimeAttempt',"id"::text,'SELECT',ARRAY['id','workItemId','attemptNumber','fence','workerId','result','reasonCode','startedAt','finishedAt','createdAt','mutationTransactionId']::text[],"fence"::text,"mutation_transaction_id"::text));

CREATE POLICY "p_worker_insert" ON "platform"."runtime_attempt" FOR INSERT TO wa_worker WITH CHECK (platform_private.row_allowed('platform_integration_owner','RuntimeAttempt',"id"::text,'INSERT',ARRAY['id','workItemId','attemptNumber','fence','workerId','result','reasonCode','startedAt','finishedAt']::text[],NULL::text,"mutation_transaction_id"::text) AND platform_private.worker_track_allowed('RuntimeAttempt',jsonb_build_object('id',"id",'work_item_id',"work_item_id",'attempt_number',"attempt_number",'fence',"fence",'worker_id',"worker_id",'result',"result",'reason_code',"reason_code",'started_at',"started_at",'finished_at',"finished_at",'created_at',"created_at",'mutation_transaction_id',"mutation_transaction_id"),'INSERT'));

CREATE POLICY "p_worker_select" ON "platform"."runtime_attempt" FOR SELECT TO wa_worker USING (platform_private.row_allowed('platform_integration_owner','RuntimeAttempt',"id"::text,'SELECT',ARRAY['id','workItemId','attemptNumber','fence','workerId','result','reasonCode','startedAt','finishedAt','createdAt','mutationTransactionId']::text[],"fence"::text,"mutation_transaction_id"::text) AND platform_private.worker_track_allowed('RuntimeAttempt',jsonb_build_object('id',"id",'work_item_id',"work_item_id",'attempt_number',"attempt_number",'fence',"fence",'worker_id',"worker_id",'result',"result",'reason_code',"reason_code",'started_at',"started_at",'finished_at',"finished_at",'created_at',"created_at",'mutation_transaction_id',"mutation_transaction_id"),'SELECT'));

CREATE POLICY "p_app_runtime_insert" ON "platform"."runtime_inbox_receipt" FOR INSERT TO wa_app_runtime WITH CHECK (platform_private.row_allowed("consumer_owner",'RuntimeInboxReceipt',"id"::text,'INSERT',ARRAY['id','outboxMessageId','consumerOwner','handlerName','payloadHash','effectReceiptId']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_select" ON "platform"."runtime_inbox_receipt" FOR SELECT TO wa_app_runtime USING (platform_private.row_allowed("consumer_owner",'RuntimeInboxReceipt',"id"::text,'SELECT',ARRAY['id','outboxMessageId','consumerOwner','handlerName','payloadHash','effectReceiptId','createdAt','mutationTransactionId']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_worker_insert" ON "platform"."runtime_inbox_receipt" FOR INSERT TO wa_worker WITH CHECK (platform_private.row_allowed("consumer_owner",'RuntimeInboxReceipt',"id"::text,'INSERT',ARRAY['id','outboxMessageId','consumerOwner','handlerName','payloadHash','effectReceiptId']::text[],NULL::text,"mutation_transaction_id"::text) AND platform_private.worker_track_allowed('RuntimeInboxReceipt',jsonb_build_object('id',"id",'outbox_message_id',"outbox_message_id",'consumer_owner',"consumer_owner",'handler_name',"handler_name",'payload_hash',"payload_hash",'effect_receipt_id',"effect_receipt_id",'created_at',"created_at",'mutation_transaction_id',"mutation_transaction_id"),'INSERT'));

CREATE POLICY "p_worker_select" ON "platform"."runtime_inbox_receipt" FOR SELECT TO wa_worker USING (platform_private.row_allowed("consumer_owner",'RuntimeInboxReceipt',"id"::text,'SELECT',ARRAY['id','outboxMessageId','consumerOwner','handlerName','payloadHash','effectReceiptId','createdAt','mutationTransactionId']::text[],NULL::text,"mutation_transaction_id"::text) AND platform_private.worker_track_allowed('RuntimeInboxReceipt',jsonb_build_object('id',"id",'outbox_message_id',"outbox_message_id",'consumer_owner',"consumer_owner",'handler_name',"handler_name",'payload_hash',"payload_hash",'effect_receipt_id',"effect_receipt_id",'created_at',"created_at",'mutation_transaction_id',"mutation_transaction_id"),'SELECT'));

CREATE POLICY "p_app_runtime_insert" ON "platform"."runtime_reservation" FOR INSERT TO wa_app_runtime WITH CHECK (platform_private.row_allowed("owner_module_id",'RuntimeReservation',"id"::text,'INSERT',ARRAY['id','commandReceiptId','ownerModuleId','resourceKind','resourceKey','semanticKey','quantity','state','fence','effectReceiptId','expiresAt']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_select" ON "platform"."runtime_reservation" FOR SELECT TO wa_app_runtime USING (platform_private.row_allowed("owner_module_id",'RuntimeReservation',"id"::text,'SELECT',ARRAY['id','commandReceiptId','ownerModuleId','resourceKind','resourceKey','semanticKey','quantity','state','fence','effectReceiptId','expiresAt','createdAt','mutationTransactionId']::text[],"fence"::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_update" ON "platform"."runtime_reservation" FOR UPDATE TO wa_app_runtime USING (platform_private.row_allowed("owner_module_id",'RuntimeReservation',"id"::text,'UPDATE',ARRAY['@row']::text[],NULL::text,"mutation_transaction_id"::text)) WITH CHECK (platform_private.row_allowed("owner_module_id",'RuntimeReservation',"id"::text,'UPDATE',ARRAY['@row']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_worker_insert" ON "platform"."runtime_reservation" FOR INSERT TO wa_worker WITH CHECK (platform_private.row_allowed("owner_module_id",'RuntimeReservation',"id"::text,'INSERT',ARRAY['id','commandReceiptId','ownerModuleId','resourceKind','resourceKey','semanticKey','quantity','state','fence','effectReceiptId','expiresAt']::text[],NULL::text,"mutation_transaction_id"::text) AND platform_private.worker_track_allowed('RuntimeReservation',jsonb_build_object('id',"id",'command_receipt_id',"command_receipt_id",'owner_module_id',"owner_module_id",'resource_kind',"resource_kind",'resource_key',"resource_key",'semantic_key',"semantic_key",'quantity',"quantity",'state',"state",'fence',"fence",'effect_receipt_id',"effect_receipt_id",'expires_at',"expires_at",'created_at',"created_at",'mutation_transaction_id',"mutation_transaction_id"),'INSERT'));

CREATE POLICY "p_worker_select" ON "platform"."runtime_reservation" FOR SELECT TO wa_worker USING (platform_private.row_allowed("owner_module_id",'RuntimeReservation',"id"::text,'SELECT',ARRAY['id','commandReceiptId','ownerModuleId','resourceKind','resourceKey','semanticKey','quantity','state','fence','effectReceiptId','expiresAt','createdAt','mutationTransactionId']::text[],"fence"::text,"mutation_transaction_id"::text) AND platform_private.worker_track_allowed('RuntimeReservation',jsonb_build_object('id',"id",'command_receipt_id',"command_receipt_id",'owner_module_id',"owner_module_id",'resource_kind',"resource_kind",'resource_key',"resource_key",'semantic_key',"semantic_key",'quantity',"quantity",'state',"state",'fence',"fence",'effect_receipt_id',"effect_receipt_id",'expires_at',"expires_at",'created_at',"created_at",'mutation_transaction_id',"mutation_transaction_id"),'SELECT'));

CREATE POLICY "p_worker_update" ON "platform"."runtime_reservation" FOR UPDATE TO wa_worker USING (platform_private.row_allowed("owner_module_id",'RuntimeReservation',"id"::text,'UPDATE',ARRAY['@row']::text[],NULL::text,"mutation_transaction_id"::text) AND platform_private.worker_track_allowed('RuntimeReservation',jsonb_build_object('id',"id",'command_receipt_id',"command_receipt_id",'owner_module_id',"owner_module_id",'resource_kind',"resource_kind",'resource_key',"resource_key",'semantic_key',"semantic_key",'quantity',"quantity",'state',"state",'fence',"fence",'effect_receipt_id',"effect_receipt_id",'expires_at',"expires_at",'created_at',"created_at",'mutation_transaction_id',"mutation_transaction_id"),'UPDATE')) WITH CHECK (platform_private.row_allowed("owner_module_id",'RuntimeReservation',"id"::text,'UPDATE',ARRAY['@row']::text[],NULL::text,"mutation_transaction_id"::text) AND platform_private.worker_track_allowed('RuntimeReservation',jsonb_build_object('id',"id",'command_receipt_id',"command_receipt_id",'owner_module_id',"owner_module_id",'resource_kind',"resource_kind",'resource_key',"resource_key",'semantic_key',"semantic_key",'quantity',"quantity",'state',"state",'fence',"fence",'effect_receipt_id',"effect_receipt_id",'expires_at',"expires_at",'created_at',"created_at",'mutation_transaction_id',"mutation_transaction_id"),'UPDATE'));

CREATE POLICY "p_app_runtime_insert" ON "platform"."owner_mutation_evidence" FOR INSERT TO wa_app_runtime WITH CHECK (platform_private.row_allowed("owner_module_id",'OwnerMutationEvidence',"id"::text,'INSERT',ARRAY['id','commandReceiptId','ownerModuleId','aggregateKind','aggregateId','previousRevision','committedRevision','action','decisionRef','evidenceSchemaId','evidenceSchemaVersion','evidenceDigest','evidenceBody']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_select" ON "platform"."owner_mutation_evidence" FOR SELECT TO wa_app_runtime USING (platform_private.row_allowed("owner_module_id",'OwnerMutationEvidence',"id"::text,'SELECT',ARRAY['id','commandReceiptId','ownerModuleId','aggregateKind','aggregateId','previousRevision','committedRevision','action','decisionRef','evidenceSchemaId','evidenceSchemaVersion','evidenceDigest','createdAt','evidenceBody','mutationTransactionId']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_worker_insert" ON "platform"."owner_mutation_evidence" FOR INSERT TO wa_worker WITH CHECK (platform_private.row_allowed("owner_module_id",'OwnerMutationEvidence',"id"::text,'INSERT',ARRAY['id','commandReceiptId','ownerModuleId','aggregateKind','aggregateId','previousRevision','committedRevision','action','decisionRef','evidenceSchemaId','evidenceSchemaVersion','evidenceDigest','evidenceBody']::text[],NULL::text,"mutation_transaction_id"::text) AND platform_private.worker_track_allowed('OwnerMutationEvidence',jsonb_build_object('id',"id",'command_receipt_id',"command_receipt_id",'owner_module_id',"owner_module_id",'aggregate_kind',"aggregate_kind",'aggregate_id',"aggregate_id",'previous_revision',"previous_revision",'committed_revision',"committed_revision",'action',"action",'decision_ref',"decision_ref",'evidence_schema_id',"evidence_schema_id",'evidence_schema_version',"evidence_schema_version",'evidence_digest',"evidence_digest",'created_at',"created_at",'evidence_body',"evidence_body",'mutation_transaction_id',"mutation_transaction_id"),'INSERT'));

CREATE POLICY "p_worker_select" ON "platform"."owner_mutation_evidence" FOR SELECT TO wa_worker USING (platform_private.row_allowed("owner_module_id",'OwnerMutationEvidence',"id"::text,'SELECT',ARRAY['id','commandReceiptId','ownerModuleId','aggregateKind','aggregateId','previousRevision','committedRevision','action','decisionRef','evidenceSchemaId','evidenceSchemaVersion','evidenceDigest','createdAt','evidenceBody','mutationTransactionId']::text[],NULL::text,"mutation_transaction_id"::text) AND platform_private.worker_track_allowed('OwnerMutationEvidence',jsonb_build_object('id',"id",'command_receipt_id',"command_receipt_id",'owner_module_id',"owner_module_id",'aggregate_kind',"aggregate_kind",'aggregate_id',"aggregate_id",'previous_revision',"previous_revision",'committed_revision',"committed_revision",'action',"action",'decision_ref',"decision_ref",'evidence_schema_id',"evidence_schema_id",'evidence_schema_version',"evidence_schema_version",'evidence_digest',"evidence_digest",'created_at',"created_at",'evidence_body',"evidence_body",'mutation_transaction_id',"mutation_transaction_id"),'SELECT'));

CREATE POLICY "p_app_runtime_insert" ON "app"."customer_profile_lifecycle_event" FOR INSERT TO wa_app_runtime WITH CHECK (platform_private.row_allowed('customer_buyer_profile','CustomerProfileLifecycleEvent',"id"::text,'INSERT',ARRAY['id','customerProfileId','commandReceiptId','sourceRevision','fromStatus','toStatus','name','actorUserId']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_select" ON "app"."customer_profile_lifecycle_event" FOR SELECT TO wa_app_runtime USING (platform_private.row_allowed('customer_buyer_profile','CustomerProfileLifecycleEvent',"id"::text,'SELECT',ARRAY['id','customerProfileId','commandReceiptId','sourceRevision','fromStatus','toStatus','name','actorUserId','createdAt','mutationTransactionId']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_insert" ON "app"."track_base_selection" FOR INSERT TO wa_app_runtime WITH CHECK (platform_private.row_allowed('track_subscription_entitlement','TrackBaseSelection',"id"::text,'INSERT',ARRAY['id','userId','track','customerProfileId','candidateProfileId','professionalProfileId','subscriptionId','revision','sourceGeneration']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_select" ON "app"."track_base_selection" FOR SELECT TO wa_app_runtime USING (platform_private.row_allowed('track_subscription_entitlement','TrackBaseSelection',"id"::text,'SELECT',ARRAY['id','userId','track','customerProfileId','candidateProfileId','professionalProfileId','subscriptionId','revision','sourceGeneration','createdAt','mutationTransactionId']::text[],"revision"::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_update" ON "app"."track_base_selection" FOR UPDATE TO wa_app_runtime USING (platform_private.row_allowed('track_subscription_entitlement','TrackBaseSelection',"id"::text,'UPDATE',ARRAY['@row']::text[],NULL::text,"mutation_transaction_id"::text)) WITH CHECK (platform_private.row_allowed('track_subscription_entitlement','TrackBaseSelection',"id"::text,'UPDATE',ARRAY['@row']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_worker_insert" ON "app"."track_base_selection" FOR INSERT TO wa_worker WITH CHECK (platform_private.row_allowed('track_subscription_entitlement','TrackBaseSelection',"id"::text,'INSERT',ARRAY['id','userId','track','customerProfileId','candidateProfileId','professionalProfileId','subscriptionId','sourceGeneration']::text[],NULL::text,"mutation_transaction_id"::text) AND platform_private.worker_track_allowed('TrackBaseSelection',jsonb_build_object('id',"id",'user_id',"user_id",'track',"track",'customer_profile_id',"customer_profile_id",'candidate_profile_id',"candidate_profile_id",'professional_profile_id',"professional_profile_id",'subscription_id',"subscription_id",'revision',"revision",'source_generation',"source_generation"),'INSERT'));

CREATE POLICY "p_worker_select" ON "app"."track_base_selection" FOR SELECT TO wa_worker USING (platform_private.row_allowed('track_subscription_entitlement','TrackBaseSelection',"id"::text,'SELECT',ARRAY['id','userId','track','customerProfileId','candidateProfileId','professionalProfileId','subscriptionId','revision','sourceGeneration']::text[],"revision"::text,"mutation_transaction_id"::text) AND platform_private.worker_track_allowed('TrackBaseSelection',jsonb_build_object('id',"id",'user_id',"user_id",'track',"track",'customer_profile_id',"customer_profile_id",'candidate_profile_id',"candidate_profile_id",'professional_profile_id',"professional_profile_id",'subscription_id',"subscription_id",'revision',"revision",'source_generation',"source_generation"),'SELECT'));

CREATE POLICY "p_worker_update" ON "app"."track_base_selection" FOR UPDATE TO wa_worker USING (platform_private.row_allowed('track_subscription_entitlement','TrackBaseSelection',"id"::text,'UPDATE',ARRAY['@row']::text[],NULL::text,"mutation_transaction_id"::text) AND platform_private.worker_track_allowed('TrackBaseSelection',jsonb_build_object('id',"id",'user_id',"user_id",'track',"track",'customer_profile_id',"customer_profile_id",'candidate_profile_id',"candidate_profile_id",'professional_profile_id',"professional_profile_id",'subscription_id',"subscription_id",'revision',"revision",'source_generation',"source_generation"),'UPDATE')) WITH CHECK (platform_private.row_allowed('track_subscription_entitlement','TrackBaseSelection',"id"::text,'UPDATE',ARRAY['@row']::text[],NULL::text,"mutation_transaction_id"::text) AND platform_private.worker_track_allowed('TrackBaseSelection',jsonb_build_object('id',"id",'user_id',"user_id",'track',"track",'customer_profile_id',"customer_profile_id",'candidate_profile_id',"candidate_profile_id",'professional_profile_id',"professional_profile_id",'subscription_id',"subscription_id",'revision',"revision",'source_generation',"source_generation"),'UPDATE'));

CREATE POLICY "p_app_runtime_insert" ON "app"."track_enrollment_receipt" FOR INSERT TO wa_app_runtime WITH CHECK (platform_private.row_allowed('track_subscription_entitlement','TrackEnrollmentReceipt',"id"::text,'INSERT',ARRAY['id','userId','track','profileId','sourceOwner','sourceCreationRevision','selectionId','selectionRevision','semanticKey','fingerprint','resultCode','effectReceiptId']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_select" ON "app"."track_enrollment_receipt" FOR SELECT TO wa_app_runtime USING (platform_private.row_allowed('track_subscription_entitlement','TrackEnrollmentReceipt',"id"::text,'SELECT',ARRAY['id','userId','track','profileId','sourceOwner','sourceCreationRevision','selectionId','selectionRevision','semanticKey','fingerprint','resultCode','effectReceiptId','createdAt','mutationTransactionId']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_worker_insert" ON "app"."track_enrollment_receipt" FOR INSERT TO wa_worker WITH CHECK (platform_private.row_allowed('track_subscription_entitlement','TrackEnrollmentReceipt',"id"::text,'INSERT',ARRAY['id','userId','track','profileId','sourceOwner','sourceCreationRevision','selectionId','selectionRevision','semanticKey','fingerprint','resultCode','effectReceiptId']::text[],NULL::text,"mutation_transaction_id"::text) AND platform_private.worker_track_allowed('TrackEnrollmentReceipt',jsonb_build_object('id',"id",'user_id',"user_id",'track',"track",'profile_id',"profile_id",'source_owner',"source_owner",'source_creation_revision',"source_creation_revision",'selection_id',"selection_id",'selection_revision',"selection_revision",'semantic_key',"semantic_key",'fingerprint',"fingerprint",'result_code',"result_code",'effect_receipt_id',"effect_receipt_id"),'INSERT'));

CREATE POLICY "p_worker_select" ON "app"."track_enrollment_receipt" FOR SELECT TO wa_worker USING (platform_private.row_allowed('track_subscription_entitlement','TrackEnrollmentReceipt',"id"::text,'SELECT',ARRAY['id','userId','track','profileId','sourceOwner','sourceCreationRevision','selectionId','selectionRevision','semanticKey','fingerprint','resultCode','effectReceiptId']::text[],NULL::text,"mutation_transaction_id"::text) AND platform_private.worker_track_allowed('TrackEnrollmentReceipt',jsonb_build_object('id',"id",'user_id',"user_id",'track',"track",'profile_id',"profile_id",'source_owner',"source_owner",'source_creation_revision',"source_creation_revision",'selection_id',"selection_id",'selection_revision',"selection_revision",'semantic_key',"semantic_key",'fingerprint',"fingerprint",'result_code',"result_code",'effect_receipt_id',"effect_receipt_id"),'SELECT'));

CREATE POLICY "p_app_runtime_insert" ON "app"."track_usage_reservation" FOR INSERT TO wa_app_runtime WITH CHECK (platform_private.row_allowed('track_subscription_entitlement','TrackUsageReservation',"id"::text,'INSERT',ARRAY['id','userId','entitlementId','periodStart','periodEnd','quantity','semanticKey','reservationId','acceptedSourceOwner','acceptedSourceId','acceptedAt','revision']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_select" ON "app"."track_usage_reservation" FOR SELECT TO wa_app_runtime USING (platform_private.row_allowed('track_subscription_entitlement','TrackUsageReservation',"id"::text,'SELECT',ARRAY['id','userId','entitlementId','periodStart','periodEnd','quantity','semanticKey','reservationId','acceptedSourceOwner','acceptedSourceId','acceptedAt','createdAt','revision','mutationTransactionId']::text[],"revision"::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_update" ON "app"."track_usage_reservation" FOR UPDATE TO wa_app_runtime USING (platform_private.row_allowed('track_subscription_entitlement','TrackUsageReservation',"id"::text,'UPDATE',ARRAY['@row']::text[],NULL::text,"mutation_transaction_id"::text)) WITH CHECK (platform_private.row_allowed('track_subscription_entitlement','TrackUsageReservation',"id"::text,'UPDATE',ARRAY['@row']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_insert" ON "app"."privacy_target_instruction" FOR INSERT TO wa_app_runtime WITH CHECK (platform_private.row_allowed('privacy_data_erasure','PrivacyTargetInstruction',"id"::text,'INSERT',ARRAY['id','privacyRequestId','ownerModuleId','targetKind','sourceId','sourceRevision','action','generation','fieldMapVersion','executorVersion','descriptorHash']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_select" ON "app"."privacy_target_instruction" FOR SELECT TO wa_app_runtime USING (platform_private.row_allowed('privacy_data_erasure','PrivacyTargetInstruction',"id"::text,'SELECT',ARRAY['id','privacyRequestId','ownerModuleId','targetKind','sourceId','sourceRevision','action','generation','fieldMapVersion','executorVersion','descriptorHash','createdAt','mutationTransactionId']::text[],"generation"::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_insert" ON "app"."privacy_owner_receipt" FOR INSERT TO wa_app_runtime WITH CHECK (platform_private.row_allowed('privacy_data_erasure','PrivacyOwnerReceipt',"id"::text,'INSERT',ARRAY['id','instructionId','generation','disposition','executionReceiptRef','legalBasisRef','artifactDigest','artifactVersion','resultSchemaVersion']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_select" ON "app"."privacy_owner_receipt" FOR SELECT TO wa_app_runtime USING (platform_private.row_allowed('privacy_data_erasure','PrivacyOwnerReceipt',"id"::text,'SELECT',ARRAY['id','instructionId','generation','disposition','executionReceiptRef','legalBasisRef','artifactDigest','artifactVersion','resultSchemaVersion','createdAt','mutationTransactionId']::text[],"generation"::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_insert" ON "app"."privacy_restore_marker" FOR INSERT TO wa_app_runtime WITH CHECK (platform_private.row_allowed('privacy_data_erasure','PrivacyRestoreMarker',"id"::text,'INSERT',ARRAY['id','ownerModuleId','targetKind','sourceId','generation','action','sourceReceiptId','restorePointRef','appliedAt','revision']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_select" ON "app"."privacy_restore_marker" FOR SELECT TO wa_app_runtime USING (platform_private.row_allowed('privacy_data_erasure','PrivacyRestoreMarker',"id"::text,'SELECT',ARRAY['id','ownerModuleId','targetKind','sourceId','generation','action','sourceReceiptId','restorePointRef','appliedAt','createdAt','revision','mutationTransactionId']::text[],"revision"::text,"mutation_transaction_id"::text));

CREATE POLICY "p_app_runtime_update" ON "app"."privacy_restore_marker" FOR UPDATE TO wa_app_runtime USING (platform_private.row_allowed('privacy_data_erasure','PrivacyRestoreMarker',"id"::text,'UPDATE',ARRAY['@row']::text[],NULL::text,"mutation_transaction_id"::text)) WITH CHECK (platform_private.row_allowed('privacy_data_erasure','PrivacyRestoreMarker',"id"::text,'UPDATE',ARRAY['@row']::text[],NULL::text,"mutation_transaction_id"::text));

CREATE FUNCTION platform_private.guard_consentlog() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE n jsonb:=to_jsonb(NEW); o jsonb; changed text[];
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'direct deletion denied' USING ERRCODE='42501'; END IF;
 IF TG_OP='UPDATE' THEN
  o:=to_jsonb(OLD);
  RAISE EXCEPTION 'immutable evidence or receipt';
 ELSE
  NEW."created_at":=clock_timestamp();
 END IF;
 NEW.mutation_transaction_id:=pg_current_xact_id()::text;
 RETURN NEW;
END;
$wa$;

CREATE TRIGGER physical_guard BEFORE INSERT OR UPDATE OR DELETE ON "app"."consent_logs" FOR EACH ROW EXECUTE FUNCTION platform_private.guard_consentlog();

ALTER TABLE "app"."consent_logs" ADD CONSTRAINT "hash_fingerprint" CHECK ("fingerprint" ~ '^[0-9a-f]{64}$');

ALTER TABLE "app"."consent_logs" ADD CONSTRAINT "hash_presentation_hash" CHECK ("presentation_hash" ~ '^[0-9a-f]{64}$');

CREATE FUNCTION platform_private.guard_privacyrequest() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE n jsonb:=to_jsonb(NEW); o jsonb; changed text[];
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'direct deletion denied' USING ERRCODE='42501'; END IF;
 IF TG_OP='UPDATE' THEN
  o:=to_jsonb(OLD);
  IF NEW."created_at" IS DISTINCT FROM OLD."created_at" OR NEW."id" IS DISTINCT FROM OLD."id" OR NEW."mutation_transaction_id" IS DISTINCT FROM OLD."mutation_transaction_id" OR NEW."user_id" IS DISTINCT FROM OLD."user_id" THEN RAISE EXCEPTION 'immutable identity or ownership'; END IF;
  IF NEW.revision<>OLD.revision+1 THEN RAISE EXCEPTION 'CAS revision must increment once'; END IF;
  IF NEW."privacy_generation"<OLD."privacy_generation" THEN RAISE EXCEPTION 'generation/fence regression'; END IF;
  IF NEW."instruction_generation"<OLD."instruction_generation" THEN RAISE EXCEPTION 'generation/fence regression'; END IF;
  SELECT COALESCE(array_agg(key),ARRAY[]::text[]) INTO changed FROM jsonb_each(n) WHERE value IS DISTINCT FROM o->key AND key<>'mutation_transaction_id';

  IF NOT platform_private.row_allowed('privacy_data_erasure','PrivacyRequest',(n->>'id'),'UPDATE',array_remove(ARRAY[CASE WHEN 'id'=ANY(changed) THEN 'id' END,CASE WHEN 'user_id'=ANY(changed) THEN 'userId' END,CASE WHEN 'type'=ANY(changed) THEN 'type' END,CASE WHEN 'status'=ANY(changed) THEN 'status' END,CASE WHEN 'requested_at'=ANY(changed) THEN 'requestedAt' END,CASE WHEN 'verified_at'=ANY(changed) THEN 'verifiedAt' END,CASE WHEN 'due_at'=ANY(changed) THEN 'dueAt' END,CASE WHEN 'completed_at'=ANY(changed) THEN 'completedAt' END,CASE WHEN 'rejection_reason'=ANY(changed) THEN 'rejectionReason' END,CASE WHEN 'admin_note'=ANY(changed) THEN 'adminNote' END,CASE WHEN 'created_at'=ANY(changed) THEN 'createdAt' END,CASE WHEN 'updated_at'=ANY(changed) THEN 'updatedAt' END,CASE WHEN 'revision'=ANY(changed) THEN 'revision' END,CASE WHEN 'privacy_generation'=ANY(changed) THEN 'privacyGeneration' END,CASE WHEN 'instruction_generation'=ANY(changed) THEN 'instructionGeneration' END,CASE WHEN 'mutation_transaction_id'=ANY(changed) THEN 'mutationTransactionId' END]::text[],NULL),OLD."revision"::text) THEN RAISE EXCEPTION 'field or CAS scope denied' USING ERRCODE='42501'; END IF;
 ELSE
  IF NEW.revision<>0 THEN RAISE EXCEPTION 'initial revision must be zero'; END IF;
  NEW."created_at":=clock_timestamp();
 END IF;
 NEW."updated_at":=clock_timestamp();
 NEW.mutation_transaction_id:=pg_current_xact_id()::text;
 RETURN NEW;
END;
$wa$;

CREATE TRIGGER physical_guard BEFORE INSERT OR UPDATE OR DELETE ON "app"."privacy_requests" FOR EACH ROW EXECUTE FUNCTION platform_private.guard_privacyrequest();

ALTER TABLE "app"."privacy_requests" ADD CONSTRAINT "nonnegative_revision" CHECK ("revision" >= 0);

ALTER TABLE "app"."privacy_requests" ADD CONSTRAINT "nonnegative_privacy_generation" CHECK ("privacy_generation" >= 0);

ALTER TABLE "app"."privacy_requests" ADD CONSTRAINT "nonnegative_instruction_generation" CHECK ("instruction_generation" >= 0);

CREATE FUNCTION platform_private.guard_agegateattempt() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE n jsonb:=to_jsonb(NEW); o jsonb; changed text[];
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'direct deletion denied' USING ERRCODE='42501'; END IF;
 IF TG_OP='UPDATE' THEN
  o:=to_jsonb(OLD);
  RAISE EXCEPTION 'immutable evidence or receipt';
 ELSE
  NEW."created_at":=clock_timestamp();
 END IF;
 NEW.mutation_transaction_id:=pg_current_xact_id()::text;
 RETURN NEW;
END;
$wa$;

CREATE TRIGGER physical_guard BEFORE INSERT OR UPDATE OR DELETE ON "app"."age_gate_attempts" FOR EACH ROW EXECUTE FUNCTION platform_private.guard_agegateattempt();

CREATE FUNCTION platform_private.guard_agegateblock() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE n jsonb:=to_jsonb(NEW); o jsonb; changed text[];
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'direct deletion denied' USING ERRCODE='42501'; END IF;
 IF TG_OP='UPDATE' THEN
  o:=to_jsonb(OLD);
  RAISE EXCEPTION 'immutable evidence or receipt';
 ELSE
  NEW."created_at":=clock_timestamp();
 END IF;
 NEW.mutation_transaction_id:=pg_current_xact_id()::text;
 RETURN NEW;
END;
$wa$;

CREATE TRIGGER physical_guard BEFORE INSERT OR UPDATE OR DELETE ON "app"."age_gate_blocks" FOR EACH ROW EXECUTE FUNCTION platform_private.guard_agegateblock();

CREATE FUNCTION platform_private.guard_accessauditlog() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE n jsonb:=to_jsonb(NEW); o jsonb; changed text[];
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'direct deletion denied' USING ERRCODE='42501'; END IF;
 IF TG_OP='UPDATE' THEN
  o:=to_jsonb(OLD);
  RAISE EXCEPTION 'immutable evidence or receipt';
 ELSE
  NEW."created_at":=clock_timestamp();
 END IF;
 NEW.mutation_transaction_id:=pg_current_xact_id()::text;
 RETURN NEW;
END;
$wa$;

CREATE TRIGGER physical_guard BEFORE INSERT OR UPDATE OR DELETE ON "app"."access_audit_logs" FOR EACH ROW EXECUTE FUNCTION platform_private.guard_accessauditlog();

CREATE FUNCTION platform_private.guard_user() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE n jsonb:=to_jsonb(NEW); o jsonb; changed text[];
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'direct deletion denied' USING ERRCODE='42501'; END IF;
 IF TG_OP='UPDATE' THEN
  o:=to_jsonb(OLD);
  IF NEW."created_at" IS DISTINCT FROM OLD."created_at" OR NEW."id" IS DISTINCT FROM OLD."id" OR NEW."mutation_transaction_id" IS DISTINCT FROM OLD."mutation_transaction_id" THEN RAISE EXCEPTION 'immutable identity or ownership'; END IF;
  IF NEW.revision<>OLD.revision+1 THEN RAISE EXCEPTION 'CAS revision must increment once'; END IF;
  IF NEW."privacy_generation"<OLD."privacy_generation" THEN RAISE EXCEPTION 'generation/fence regression'; END IF;
  SELECT COALESCE(array_agg(key),ARRAY[]::text[]) INTO changed FROM jsonb_each(n) WHERE value IS DISTINCT FROM o->key AND key<>'mutation_transaction_id';

  IF NOT platform_private.row_allowed('identity_access','User',(n->>'id'),'UPDATE',array_remove(ARRAY[CASE WHEN 'id'=ANY(changed) THEN 'id' END,CASE WHEN 'email'=ANY(changed) THEN 'email' END,CASE WHEN 'handle'=ANY(changed) THEN 'handle' END,CASE WHEN 'display_name'=ANY(changed) THEN 'displayName' END,CASE WHEN 'avatar_url'=ANY(changed) THEN 'avatarUrl' END,CASE WHEN 'bio'=ANY(changed) THEN 'bio' END,CASE WHEN 'city'=ANY(changed) THEN 'city' END,CASE WHEN 'state'=ANY(changed) THEN 'state' END,CASE WHEN 'country'=ANY(changed) THEN 'country' END,CASE WHEN 'is_public'=ANY(changed) THEN 'isPublic' END,CASE WHEN 'created_at'=ANY(changed) THEN 'createdAt' END,CASE WHEN 'updated_at'=ANY(changed) THEN 'updatedAt' END,CASE WHEN 'privacy_erased_at'=ANY(changed) THEN 'privacyErasedAt' END,CASE WHEN 'privacy_erasure_status'=ANY(changed) THEN 'privacyErasureStatus' END,CASE WHEN 'revision'=ANY(changed) THEN 'revision' END,CASE WHEN 'privacy_generation'=ANY(changed) THEN 'privacyGeneration' END,CASE WHEN 'mutation_transaction_id'=ANY(changed) THEN 'mutationTransactionId' END]::text[],NULL),OLD."revision"::text) THEN RAISE EXCEPTION 'field or CAS scope denied' USING ERRCODE='42501'; END IF;
 ELSE
  IF NEW.revision<>0 THEN RAISE EXCEPTION 'initial revision must be zero'; END IF;
  NEW."created_at":=clock_timestamp();
 END IF;
 NEW."updated_at":=clock_timestamp();
 NEW.mutation_transaction_id:=pg_current_xact_id()::text;
 RETURN NEW;
END;
$wa$;

CREATE TRIGGER physical_guard BEFORE INSERT OR UPDATE OR DELETE ON "app"."users" FOR EACH ROW EXECUTE FUNCTION platform_private.guard_user();

ALTER TABLE "app"."users" ADD CONSTRAINT "nonnegative_revision" CHECK ("revision" >= 0);

ALTER TABLE "app"."users" ADD CONSTRAINT "nonnegative_privacy_generation" CHECK ("privacy_generation" >= 0);

CREATE FUNCTION platform_private.guard_userrole() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE n jsonb:=to_jsonb(NEW); o jsonb; changed text[];
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'direct deletion denied' USING ERRCODE='42501'; END IF;
 IF TG_OP='UPDATE' THEN
  o:=to_jsonb(OLD);
  IF NEW."created_at" IS DISTINCT FROM OLD."created_at" OR NEW."mutation_transaction_id" IS DISTINCT FROM OLD."mutation_transaction_id" OR NEW."role" IS DISTINCT FROM OLD."role" OR NEW."user_id" IS DISTINCT FROM OLD."user_id" THEN RAISE EXCEPTION 'immutable identity or ownership'; END IF;
  IF NEW.revision<>OLD.revision+1 THEN RAISE EXCEPTION 'CAS revision must increment once'; END IF;
  SELECT COALESCE(array_agg(key),ARRAY[]::text[]) INTO changed FROM jsonb_each(n) WHERE value IS DISTINCT FROM o->key AND key<>'mutation_transaction_id';

  IF NOT platform_private.row_allowed('identity_access','UserRole',(n->>'user_id') || ':' || (n->>'role'),'UPDATE',array_remove(ARRAY[CASE WHEN 'user_id'=ANY(changed) THEN 'userId' END,CASE WHEN 'role'=ANY(changed) THEN 'role' END,CASE WHEN 'created_at'=ANY(changed) THEN 'createdAt' END,CASE WHEN 'revision'=ANY(changed) THEN 'revision' END,CASE WHEN 'mutation_transaction_id'=ANY(changed) THEN 'mutationTransactionId' END]::text[],NULL),OLD."revision"::text) THEN RAISE EXCEPTION 'field or CAS scope denied' USING ERRCODE='42501'; END IF;
 ELSE
  IF NEW.revision<>0 THEN RAISE EXCEPTION 'initial revision must be zero'; END IF;
  NEW."created_at":=clock_timestamp();
 END IF;
 NEW.mutation_transaction_id:=pg_current_xact_id()::text;
 RETURN NEW;
END;
$wa$;

CREATE TRIGGER physical_guard BEFORE INSERT OR UPDATE OR DELETE ON "app"."user_roles" FOR EACH ROW EXECUTE FUNCTION platform_private.guard_userrole();

ALTER TABLE "app"."user_roles" ADD CONSTRAINT "nonnegative_revision" CHECK ("revision" >= 0);

CREATE FUNCTION platform_private.guard_professionalprofile() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE n jsonb:=to_jsonb(NEW); o jsonb; changed text[];
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'direct deletion denied' USING ERRCODE='42501'; END IF;
 IF TG_OP='UPDATE' THEN
  o:=to_jsonb(OLD);
  IF NEW."created_at" IS DISTINCT FROM OLD."created_at" OR NEW."id" IS DISTINCT FROM OLD."id" OR NEW."mutation_transaction_id" IS DISTINCT FROM OLD."mutation_transaction_id" OR NEW."stripe_account_id" IS DISTINCT FROM OLD."stripe_account_id" OR NEW."user_id" IS DISTINCT FROM OLD."user_id" THEN RAISE EXCEPTION 'immutable identity or ownership'; END IF;
  IF NEW.revision<>OLD.revision+1 THEN RAISE EXCEPTION 'CAS revision must increment once'; END IF;
  IF NEW."privacy_generation"<OLD."privacy_generation" THEN RAISE EXCEPTION 'generation/fence regression'; END IF;
  SELECT COALESCE(array_agg(key),ARRAY[]::text[]) INTO changed FROM jsonb_each(n) WHERE value IS DISTINCT FROM o->key AND key<>'mutation_transaction_id';

  IF NOT platform_private.row_allowed('professional_eligibility','ProfessionalProfile',(n->>'id'),'UPDATE',array_remove(ARRAY[CASE WHEN 'id'=ANY(changed) THEN 'id' END,CASE WHEN 'user_id'=ANY(changed) THEN 'userId' END,CASE WHEN 'slug'=ANY(changed) THEN 'slug' END,CASE WHEN 'headline'=ANY(changed) THEN 'headline' END,CASE WHEN 'bio'=ANY(changed) THEN 'bio' END,CASE WHEN 'website_url'=ANY(changed) THEN 'websiteUrl' END,CASE WHEN 'city'=ANY(changed) THEN 'city' END,CASE WHEN 'state'=ANY(changed) THEN 'state' END,CASE WHEN 'country'=ANY(changed) THEN 'country' END,CASE WHEN 'status'=ANY(changed) THEN 'status' END,CASE WHEN 'rating_average'=ANY(changed) THEN 'ratingAverage' END,CASE WHEN 'rating_count'=ANY(changed) THEN 'ratingCount' END,CASE WHEN 'stripe_account_id'=ANY(changed) THEN 'stripeAccountId' END,CASE WHEN 'stripe_ready'=ANY(changed) THEN 'stripeReady' END,CASE WHEN 'onboarding_complete_at'=ANY(changed) THEN 'onboardingCompleteAt' END,CASE WHEN 'default_currency'=ANY(changed) THEN 'defaultCurrency' END,CASE WHEN 'created_at'=ANY(changed) THEN 'createdAt' END,CASE WHEN 'updated_at'=ANY(changed) THEN 'updatedAt' END,CASE WHEN 'suspended_for_moderation_at'=ANY(changed) THEN 'suspendedForModerationAt' END,CASE WHEN 'trust_score'=ANY(changed) THEN 'trustScore' END,CASE WHEN 'verified_at'=ANY(changed) THEN 'verifiedAt' END,CASE WHEN 'verification_expires_at'=ANY(changed) THEN 'verificationExpiresAt' END,CASE WHEN 'revision'=ANY(changed) THEN 'revision' END,CASE WHEN 'privacy_generation'=ANY(changed) THEN 'privacyGeneration' END,CASE WHEN 'mutation_transaction_id'=ANY(changed) THEN 'mutationTransactionId' END]::text[],NULL),OLD."revision"::text) THEN RAISE EXCEPTION 'field or CAS scope denied' USING ERRCODE='42501'; END IF;
 ELSE
  IF NEW.revision<>0 THEN RAISE EXCEPTION 'initial revision must be zero'; END IF;
  NEW."created_at":=clock_timestamp();
 END IF;
 NEW."updated_at":=clock_timestamp();
 NEW.mutation_transaction_id:=pg_current_xact_id()::text;
 RETURN NEW;
END;
$wa$;

CREATE TRIGGER physical_guard BEFORE INSERT OR UPDATE OR DELETE ON "app"."professional_profiles" FOR EACH ROW EXECUTE FUNCTION platform_private.guard_professionalprofile();

ALTER TABLE "app"."professional_profiles" ADD CONSTRAINT "nonnegative_revision" CHECK ("revision" >= 0);

ALTER TABLE "app"."professional_profiles" ADD CONSTRAINT "nonnegative_privacy_generation" CHECK ("privacy_generation" >= 0);

CREATE FUNCTION platform_private.guard_customerprofile() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE n jsonb:=to_jsonb(NEW); o jsonb; changed text[];
BEGIN
 PERFORM pg_advisory_xact_lock(hashtextextended('source:CustomerProfile:'||NEW.id::text,0));
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'direct deletion denied' USING ERRCODE='42501'; END IF;
 IF TG_OP='UPDATE' THEN
  o:=to_jsonb(OLD);
  IF NEW."created_at" IS DISTINCT FROM OLD."created_at" OR NEW."id" IS DISTINCT FROM OLD."id" OR NEW."mutation_transaction_id" IS DISTINCT FROM OLD."mutation_transaction_id" OR NEW."user_id" IS DISTINCT FROM OLD."user_id" THEN RAISE EXCEPTION 'immutable identity or ownership'; END IF;
  IF NEW.revision<>OLD.revision+1 THEN RAISE EXCEPTION 'CAS revision must increment once'; END IF;
  IF NEW."privacy_generation"<OLD."privacy_generation" THEN RAISE EXCEPTION 'generation/fence regression'; END IF;
  SELECT COALESCE(array_agg(key),ARRAY[]::text[]) INTO changed FROM jsonb_each(n) WHERE value IS DISTINCT FROM o->key AND key<>'mutation_transaction_id';

  IF NOT platform_private.row_allowed('customer_buyer_profile','CustomerProfile',(n->>'id'),'UPDATE',array_remove(ARRAY[CASE WHEN 'id'=ANY(changed) THEN 'id' END,CASE WHEN 'user_id'=ANY(changed) THEN 'userId' END,CASE WHEN 'status'=ANY(changed) THEN 'status' END,CASE WHEN 'display_name'=ANY(changed) THEN 'displayName' END,CASE WHEN 'avatar_media_id'=ANY(changed) THEN 'avatarMediaId' END,CASE WHEN 'city'=ANY(changed) THEN 'city' END,CASE WHEN 'state'=ANY(changed) THEN 'state' END,CASE WHEN 'country'=ANY(changed) THEN 'country' END,CASE WHEN 'created_at'=ANY(changed) THEN 'createdAt' END,CASE WHEN 'updated_at'=ANY(changed) THEN 'updatedAt' END,CASE WHEN 'archived_at'=ANY(changed) THEN 'archivedAt' END,CASE WHEN 'revision'=ANY(changed) THEN 'revision' END,CASE WHEN 'privacy_generation'=ANY(changed) THEN 'privacyGeneration' END,CASE WHEN 'mutation_transaction_id'=ANY(changed) THEN 'mutationTransactionId' END]::text[],NULL),OLD."revision"::text) THEN RAISE EXCEPTION 'field or CAS scope denied' USING ERRCODE='42501'; END IF;
 ELSE
  IF NEW.revision<>0 THEN RAISE EXCEPTION 'initial revision must be zero'; END IF;
  NEW."created_at":=clock_timestamp();
 END IF;
 IF NOT platform_private.context_subject_owner(NEW.user_id,'customer_buyer_profile') THEN RAISE EXCEPTION 'foreign Customer principal'; END IF;
 NEW."updated_at":=clock_timestamp();
 NEW.mutation_transaction_id:=pg_current_xact_id()::text;
 RETURN NEW;
END;
$wa$;

CREATE TRIGGER physical_guard BEFORE INSERT OR UPDATE OR DELETE ON "app"."customer_profiles" FOR EACH ROW EXECUTE FUNCTION platform_private.guard_customerprofile();

ALTER TABLE "app"."customer_profiles" ADD CONSTRAINT "nonnegative_revision" CHECK ("revision" >= 0);

ALTER TABLE "app"."customer_profiles" ADD CONSTRAINT "nonnegative_privacy_generation" CHECK ("privacy_generation" >= 0);

CREATE FUNCTION platform_private.guard_candidateprofile() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE n jsonb:=to_jsonb(NEW); o jsonb; changed text[];
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'direct deletion denied' USING ERRCODE='42501'; END IF;
 IF TG_OP='UPDATE' THEN
  o:=to_jsonb(OLD);
  IF NEW."created_at" IS DISTINCT FROM OLD."created_at" OR NEW."id" IS DISTINCT FROM OLD."id" OR NEW."mutation_transaction_id" IS DISTINCT FROM OLD."mutation_transaction_id" OR NEW."user_id" IS DISTINCT FROM OLD."user_id" THEN RAISE EXCEPTION 'immutable identity or ownership'; END IF;
  IF NEW.revision<>OLD.revision+1 THEN RAISE EXCEPTION 'CAS revision must increment once'; END IF;
  IF NEW."privacy_generation"<OLD."privacy_generation" THEN RAISE EXCEPTION 'generation/fence regression'; END IF;
  SELECT COALESCE(array_agg(key),ARRAY[]::text[]) INTO changed FROM jsonb_each(n) WHERE value IS DISTINCT FROM o->key AND key<>'mutation_transaction_id';

  IF NOT platform_private.row_allowed('candidate_application_resume_privacy','CandidateProfile',(n->>'id'),'UPDATE',array_remove(ARRAY[CASE WHEN 'id'=ANY(changed) THEN 'id' END,CASE WHEN 'user_id'=ANY(changed) THEN 'userId' END,CASE WHEN 'headline'=ANY(changed) THEN 'headline' END,CASE WHEN 'portfolio_url'=ANY(changed) THEN 'portfolioUrl' END,CASE WHEN 'availability'=ANY(changed) THEN 'availability' END,CASE WHEN 'city'=ANY(changed) THEN 'city' END,CASE WHEN 'state'=ANY(changed) THEN 'state' END,CASE WHEN 'country'=ANY(changed) THEN 'country' END,CASE WHEN 'status'=ANY(changed) THEN 'status' END,CASE WHEN 'is_visible'=ANY(changed) THEN 'isVisible' END,CASE WHEN 'created_at'=ANY(changed) THEN 'createdAt' END,CASE WHEN 'updated_at'=ANY(changed) THEN 'updatedAt' END,CASE WHEN 'trust_score'=ANY(changed) THEN 'trustScore' END,CASE WHEN 'verified_at'=ANY(changed) THEN 'verifiedAt' END,CASE WHEN 'verification_expires_at'=ANY(changed) THEN 'verificationExpiresAt' END,CASE WHEN 'revision'=ANY(changed) THEN 'revision' END,CASE WHEN 'privacy_generation'=ANY(changed) THEN 'privacyGeneration' END,CASE WHEN 'discovery_preference_revision'=ANY(changed) THEN 'discoveryPreferenceRevision' END,CASE WHEN 'discovery_enabled_at'=ANY(changed) THEN 'discoveryEnabledAt' END,CASE WHEN 'mutation_transaction_id'=ANY(changed) THEN 'mutationTransactionId' END]::text[],NULL),OLD."revision"::text) THEN RAISE EXCEPTION 'field or CAS scope denied' USING ERRCODE='42501'; END IF;
 ELSE
  IF NEW.revision<>0 THEN RAISE EXCEPTION 'initial revision must be zero'; END IF;
  NEW."created_at":=clock_timestamp();
 END IF;
 NEW."updated_at":=clock_timestamp();
 NEW.mutation_transaction_id:=pg_current_xact_id()::text;
 RETURN NEW;
END;
$wa$;

CREATE TRIGGER physical_guard BEFORE INSERT OR UPDATE OR DELETE ON "app"."candidate_profiles" FOR EACH ROW EXECUTE FUNCTION platform_private.guard_candidateprofile();

ALTER TABLE "app"."candidate_profiles" ADD CONSTRAINT "nonnegative_revision" CHECK ("revision" >= 0);

ALTER TABLE "app"."candidate_profiles" ADD CONSTRAINT "nonnegative_privacy_generation" CHECK ("privacy_generation" >= 0);

CREATE FUNCTION platform_private.guard_auditevent() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE n jsonb:=to_jsonb(NEW); o jsonb; changed text[];
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'direct deletion denied' USING ERRCODE='42501'; END IF;
 IF TG_OP='UPDATE' THEN
  o:=to_jsonb(OLD);
  RAISE EXCEPTION 'immutable evidence or receipt';
 ELSE
  NEW."created_at":=clock_timestamp();
 END IF;
 NEW.mutation_transaction_id:=pg_current_xact_id()::text;
 RETURN NEW;
END;
$wa$;

CREATE TRIGGER physical_guard BEFORE INSERT OR UPDATE OR DELETE ON "app"."audit_events" FOR EACH ROW EXECUTE FUNCTION platform_private.guard_auditevent();

ALTER TABLE "app"."audit_events" ADD CONSTRAINT "f0_null_metadata" CHECK ("metadata" IS NULL);

CREATE FUNCTION platform_private.guard_usersecurityprofile() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE n jsonb:=to_jsonb(NEW); o jsonb; changed text[];
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'direct deletion denied' USING ERRCODE='42501'; END IF;
 IF TG_OP='UPDATE' THEN
  o:=to_jsonb(OLD);
  IF NEW."created_at" IS DISTINCT FROM OLD."created_at" OR NEW."id" IS DISTINCT FROM OLD."id" OR NEW."mutation_transaction_id" IS DISTINCT FROM OLD."mutation_transaction_id" OR NEW."user_id" IS DISTINCT FROM OLD."user_id" THEN RAISE EXCEPTION 'immutable identity or ownership'; END IF;
  IF NEW.revision<>OLD.revision+1 THEN RAISE EXCEPTION 'CAS revision must increment once'; END IF;
  IF NEW."security_generation"<OLD."security_generation" THEN RAISE EXCEPTION 'generation/fence regression'; END IF;
  SELECT COALESCE(array_agg(key),ARRAY[]::text[]) INTO changed FROM jsonb_each(n) WHERE value IS DISTINCT FROM o->key AND key<>'mutation_transaction_id';

  IF NOT platform_private.row_allowed('identity_access','UserSecurityProfile',(n->>'id'),'UPDATE',array_remove(ARRAY[CASE WHEN 'id'=ANY(changed) THEN 'id' END,CASE WHEN 'user_id'=ANY(changed) THEN 'userId' END,CASE WHEN 'security_tier'=ANY(changed) THEN 'securityTier' END,CASE WHEN 'phone_number_encrypted'=ANY(changed) THEN 'phoneNumberEncrypted' END,CASE WHEN 'phone_number_hash'=ANY(changed) THEN 'phoneNumberHash' END,CASE WHEN 'phone_verified_at'=ANY(changed) THEN 'phoneVerifiedAt' END,CASE WHEN 'phone_last_changed_at'=ANY(changed) THEN 'phoneLastChangedAt' END,CASE WHEN 'passkeys_enabled'=ANY(changed) THEN 'passkeysEnabled' END,CASE WHEN 'sms_mfa_enabled'=ANY(changed) THEN 'smsMfaEnabled' END,CASE WHEN 'backup_password_configured'=ANY(changed) THEN 'backupPasswordConfigured' END,CASE WHEN 'sensitive_action_mfa_required'=ANY(changed) THEN 'sensitiveActionMfaRequired' END,CASE WHEN 'last_step_up_at'=ANY(changed) THEN 'lastStepUpAt' END,CASE WHEN 'last_sensitive_action_at'=ANY(changed) THEN 'lastSensitiveActionAt' END,CASE WHEN 'locked_until'=ANY(changed) THEN 'lockedUntil' END,CASE WHEN 'lock_reason'=ANY(changed) THEN 'lockReason' END,CASE WHEN 'created_at'=ANY(changed) THEN 'createdAt' END,CASE WHEN 'updated_at'=ANY(changed) THEN 'updatedAt' END,CASE WHEN 'revision'=ANY(changed) THEN 'revision' END,CASE WHEN 'security_generation'=ANY(changed) THEN 'securityGeneration' END,CASE WHEN 'mutation_transaction_id'=ANY(changed) THEN 'mutationTransactionId' END]::text[],NULL),OLD."revision"::text) THEN RAISE EXCEPTION 'field or CAS scope denied' USING ERRCODE='42501'; END IF;
 ELSE
  IF NEW.revision<>0 THEN RAISE EXCEPTION 'initial revision must be zero'; END IF;
  NEW."created_at":=clock_timestamp();
 END IF;
 NEW."updated_at":=clock_timestamp();
 PERFORM pg_advisory_xact_lock(hashtextextended('identity:'||NEW.user_id::text,0));
 NEW.mutation_transaction_id:=pg_current_xact_id()::text;
 RETURN NEW;
END;
$wa$;

CREATE TRIGGER physical_guard BEFORE INSERT OR UPDATE OR DELETE ON "app"."user_security_profiles" FOR EACH ROW EXECUTE FUNCTION platform_private.guard_usersecurityprofile();

ALTER TABLE "app"."user_security_profiles" ADD CONSTRAINT "nonnegative_revision" CHECK ("revision" >= 0);

ALTER TABLE "app"."user_security_profiles" ADD CONSTRAINT "nonnegative_security_generation" CHECK ("security_generation" >= 0);

CREATE FUNCTION platform_private.guard_authprovideraccount() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE n jsonb:=to_jsonb(NEW); o jsonb; changed text[];
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'direct deletion denied' USING ERRCODE='42501'; END IF;
 IF TG_OP='UPDATE' THEN
  o:=to_jsonb(OLD);
  IF NEW."created_at" IS DISTINCT FROM OLD."created_at" OR NEW."id" IS DISTINCT FROM OLD."id" OR NEW."mutation_transaction_id" IS DISTINCT FROM OLD."mutation_transaction_id" OR NEW."provider_account_id" IS DISTINCT FROM OLD."provider_account_id" OR NEW."provider_user_id" IS DISTINCT FROM OLD."provider_user_id" OR NEW."security_profile_id" IS DISTINCT FROM OLD."security_profile_id" OR NEW."user_id" IS DISTINCT FROM OLD."user_id" THEN RAISE EXCEPTION 'immutable identity or ownership'; END IF;
  IF NEW.revision<>OLD.revision+1 THEN RAISE EXCEPTION 'CAS revision must increment once'; END IF;
  SELECT COALESCE(array_agg(key),ARRAY[]::text[]) INTO changed FROM jsonb_each(n) WHERE value IS DISTINCT FROM o->key AND key<>'mutation_transaction_id';

  IF NOT platform_private.row_allowed('identity_access','AuthProviderAccount',(n->>'id'),'UPDATE',array_remove(ARRAY[CASE WHEN 'id'=ANY(changed) THEN 'id' END,CASE WHEN 'user_id'=ANY(changed) THEN 'userId' END,CASE WHEN 'security_profile_id'=ANY(changed) THEN 'securityProfileId' END,CASE WHEN 'provider_type'=ANY(changed) THEN 'providerType' END,CASE WHEN 'provider_user_id'=ANY(changed) THEN 'providerUserId' END,CASE WHEN 'provider_account_id'=ANY(changed) THEN 'providerAccountId' END,CASE WHEN 'email'=ANY(changed) THEN 'email' END,CASE WHEN 'email_verified_at'=ANY(changed) THEN 'emailVerifiedAt' END,CASE WHEN 'status'=ANY(changed) THEN 'status' END,CASE WHEN 'linked_at'=ANY(changed) THEN 'linkedAt' END,CASE WHEN 'last_used_at'=ANY(changed) THEN 'lastUsedAt' END,CASE WHEN 'revoked_at'=ANY(changed) THEN 'revokedAt' END,CASE WHEN 'created_at'=ANY(changed) THEN 'createdAt' END,CASE WHEN 'updated_at'=ANY(changed) THEN 'updatedAt' END,CASE WHEN 'revision'=ANY(changed) THEN 'revision' END,CASE WHEN 'mutation_transaction_id'=ANY(changed) THEN 'mutationTransactionId' END]::text[],NULL),OLD."revision"::text) THEN RAISE EXCEPTION 'field or CAS scope denied' USING ERRCODE='42501'; END IF;
 ELSE
  IF NEW.revision<>0 THEN RAISE EXCEPTION 'initial revision must be zero'; END IF;
  NEW."created_at":=clock_timestamp();
 END IF;
 NEW."updated_at":=clock_timestamp();
 NEW.mutation_transaction_id:=pg_current_xact_id()::text;
 RETURN NEW;
END;
$wa$;

CREATE TRIGGER physical_guard BEFORE INSERT OR UPDATE OR DELETE ON "app"."auth_provider_accounts" FOR EACH ROW EXECUTE FUNCTION platform_private.guard_authprovideraccount();

ALTER TABLE "app"."auth_provider_accounts" ADD CONSTRAINT "nonnegative_revision" CHECK ("revision" >= 0);

CREATE FUNCTION platform_private.guard_trackplan() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE n jsonb:=to_jsonb(NEW); o jsonb; changed text[];
BEGIN
 PERFORM pg_advisory_xact_lock(hashtextextended('source:TrackPlan:'||NEW.id::text,0));
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'direct deletion denied' USING ERRCODE='42501'; END IF;
 IF TG_OP='UPDATE' THEN
  o:=to_jsonb(OLD);
  IF NEW."created_at" IS DISTINCT FROM OLD."created_at" OR NEW."id" IS DISTINCT FROM OLD."id" OR NEW."mutation_transaction_id" IS DISTINCT FROM OLD."mutation_transaction_id" OR NEW."track" IS DISTINCT FROM OLD."track" THEN RAISE EXCEPTION 'immutable identity or ownership'; END IF;
  IF NEW.revision<>OLD.revision+1 THEN RAISE EXCEPTION 'CAS revision must increment once'; END IF;
  SELECT COALESCE(array_agg(key),ARRAY[]::text[]) INTO changed FROM jsonb_each(n) WHERE value IS DISTINCT FROM o->key AND key<>'mutation_transaction_id';

  IF NOT platform_private.row_allowed('track_subscription_entitlement','TrackPlan',(n->>'id'),'UPDATE',array_remove(ARRAY[CASE WHEN 'id'=ANY(changed) THEN 'id' END,CASE WHEN 'track'=ANY(changed) THEN 'track' END,CASE WHEN 'key'=ANY(changed) THEN 'key' END,CASE WHEN 'name'=ANY(changed) THEN 'name' END,CASE WHEN 'status'=ANY(changed) THEN 'status' END,CASE WHEN 'billing_model'=ANY(changed) THEN 'billingModel' END,CASE WHEN 'monthly_price_cents'=ANY(changed) THEN 'monthlyPriceCents' END,CASE WHEN 'currency'=ANY(changed) THEN 'currency' END,CASE WHEN 'description'=ANY(changed) THEN 'description' END,CASE WHEN 'display_order'=ANY(changed) THEN 'displayOrder' END,CASE WHEN 'metadata'=ANY(changed) THEN 'metadata' END,CASE WHEN 'created_at'=ANY(changed) THEN 'createdAt' END,CASE WHEN 'updated_at'=ANY(changed) THEN 'updatedAt' END,CASE WHEN 'revision'=ANY(changed) THEN 'revision' END,CASE WHEN 'version'=ANY(changed) THEN 'version' END,CASE WHEN 'content_hash'=ANY(changed) THEN 'contentHash' END,CASE WHEN 'mutation_transaction_id'=ANY(changed) THEN 'mutationTransactionId' END]::text[],NULL),OLD."revision"::text) THEN RAISE EXCEPTION 'field or CAS scope denied' USING ERRCODE='42501'; END IF;
 ELSE
  IF NEW.revision<>0 THEN RAISE EXCEPTION 'initial revision must be zero'; END IF;
  NEW."created_at":=clock_timestamp();
 END IF;
 NEW."updated_at":=clock_timestamp();
 NEW.mutation_transaction_id:=pg_current_xact_id()::text;
 RETURN NEW;
END;
$wa$;

CREATE TRIGGER physical_guard BEFORE INSERT OR UPDATE OR DELETE ON "app"."track_plans" FOR EACH ROW EXECUTE FUNCTION platform_private.guard_trackplan();

ALTER TABLE "app"."track_plans" ADD CONSTRAINT "f0_null_metadata" CHECK ("metadata" IS NULL);

ALTER TABLE "app"."track_plans" ADD CONSTRAINT "nonnegative_revision" CHECK ("revision" >= 0);

ALTER TABLE "app"."track_plans" ADD CONSTRAINT "hash_content_hash" CHECK ("content_hash" ~ '^[0-9a-f]{64}$');

CREATE FUNCTION platform_private.guard_trackentitlementdefinition() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE n jsonb:=to_jsonb(NEW); o jsonb; changed text[];
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'direct deletion denied' USING ERRCODE='42501'; END IF;
 IF TG_OP='UPDATE' THEN
  o:=to_jsonb(OLD);
  IF NEW."created_at" IS DISTINCT FROM OLD."created_at" OR NEW."id" IS DISTINCT FROM OLD."id" OR NEW."mutation_transaction_id" IS DISTINCT FROM OLD."mutation_transaction_id" OR NEW."track" IS DISTINCT FROM OLD."track" THEN RAISE EXCEPTION 'immutable identity or ownership'; END IF;
  IF NEW.revision<>OLD.revision+1 THEN RAISE EXCEPTION 'CAS revision must increment once'; END IF;
  SELECT COALESCE(array_agg(key),ARRAY[]::text[]) INTO changed FROM jsonb_each(n) WHERE value IS DISTINCT FROM o->key AND key<>'mutation_transaction_id';

  IF NOT platform_private.row_allowed('track_subscription_entitlement','TrackEntitlementDefinition',(n->>'id'),'UPDATE',array_remove(ARRAY[CASE WHEN 'id'=ANY(changed) THEN 'id' END,CASE WHEN 'key'=ANY(changed) THEN 'key' END,CASE WHEN 'label'=ANY(changed) THEN 'label' END,CASE WHEN 'description'=ANY(changed) THEN 'description' END,CASE WHEN 'value_type'=ANY(changed) THEN 'valueType' END,CASE WHEN 'track'=ANY(changed) THEN 'track' END,CASE WHEN 'is_active'=ANY(changed) THEN 'isActive' END,CASE WHEN 'created_at'=ANY(changed) THEN 'createdAt' END,CASE WHEN 'updated_at'=ANY(changed) THEN 'updatedAt' END,CASE WHEN 'revision'=ANY(changed) THEN 'revision' END,CASE WHEN 'mutation_transaction_id'=ANY(changed) THEN 'mutationTransactionId' END]::text[],NULL),OLD."revision"::text) THEN RAISE EXCEPTION 'field or CAS scope denied' USING ERRCODE='42501'; END IF;
 ELSE
  IF NEW.revision<>0 THEN RAISE EXCEPTION 'initial revision must be zero'; END IF;
  NEW."created_at":=clock_timestamp();
 END IF;
 NEW."updated_at":=clock_timestamp();
 NEW.mutation_transaction_id:=pg_current_xact_id()::text;
 RETURN NEW;
END;
$wa$;

CREATE TRIGGER physical_guard BEFORE INSERT OR UPDATE OR DELETE ON "app"."track_entitlement_definitions" FOR EACH ROW EXECUTE FUNCTION platform_private.guard_trackentitlementdefinition();

ALTER TABLE "app"."track_entitlement_definitions" ADD CONSTRAINT "nonnegative_revision" CHECK ("revision" >= 0);

CREATE FUNCTION platform_private.guard_trackplanentitlement() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE n jsonb:=to_jsonb(NEW); o jsonb; changed text[];
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'direct deletion denied' USING ERRCODE='42501'; END IF;
 IF TG_OP='UPDATE' THEN
  o:=to_jsonb(OLD);
  IF NEW."created_at" IS DISTINCT FROM OLD."created_at" OR NEW."entitlement_id" IS DISTINCT FROM OLD."entitlement_id" OR NEW."id" IS DISTINCT FROM OLD."id" OR NEW."mutation_transaction_id" IS DISTINCT FROM OLD."mutation_transaction_id" OR NEW."plan_id" IS DISTINCT FROM OLD."plan_id" THEN RAISE EXCEPTION 'immutable identity or ownership'; END IF;
  IF NEW.revision<>OLD.revision+1 THEN RAISE EXCEPTION 'CAS revision must increment once'; END IF;
  SELECT COALESCE(array_agg(key),ARRAY[]::text[]) INTO changed FROM jsonb_each(n) WHERE value IS DISTINCT FROM o->key AND key<>'mutation_transaction_id';

  IF NOT platform_private.row_allowed('track_subscription_entitlement','TrackPlanEntitlement',(n->>'id'),'UPDATE',array_remove(ARRAY[CASE WHEN 'id'=ANY(changed) THEN 'id' END,CASE WHEN 'plan_id'=ANY(changed) THEN 'planId' END,CASE WHEN 'entitlement_id'=ANY(changed) THEN 'entitlementId' END,CASE WHEN 'value_type'=ANY(changed) THEN 'valueType' END,CASE WHEN 'boolean_value'=ANY(changed) THEN 'booleanValue' END,CASE WHEN 'int_value'=ANY(changed) THEN 'intValue' END,CASE WHEN 'decimal_value'=ANY(changed) THEN 'decimalValue' END,CASE WHEN 'string_value'=ANY(changed) THEN 'stringValue' END,CASE WHEN 'json_value'=ANY(changed) THEN 'jsonValue' END,CASE WHEN 'usage_period'=ANY(changed) THEN 'usagePeriod' END,CASE WHEN 'created_at'=ANY(changed) THEN 'createdAt' END,CASE WHEN 'updated_at'=ANY(changed) THEN 'updatedAt' END,CASE WHEN 'revision'=ANY(changed) THEN 'revision' END,CASE WHEN 'mutation_transaction_id'=ANY(changed) THEN 'mutationTransactionId' END]::text[],NULL),OLD."revision"::text) THEN RAISE EXCEPTION 'field or CAS scope denied' USING ERRCODE='42501'; END IF;
 ELSE
  IF NEW.revision<>0 THEN RAISE EXCEPTION 'initial revision must be zero'; END IF;
  NEW."created_at":=clock_timestamp();
 END IF;
 NEW."updated_at":=clock_timestamp();
 NEW.mutation_transaction_id:=pg_current_xact_id()::text;
 RETURN NEW;
END;
$wa$;

CREATE TRIGGER physical_guard BEFORE INSERT OR UPDATE OR DELETE ON "app"."track_plan_entitlements" FOR EACH ROW EXECUTE FUNCTION platform_private.guard_trackplanentitlement();

ALTER TABLE "app"."track_plan_entitlements" ADD CONSTRAINT "f0_null_json_value" CHECK ("json_value" IS NULL);

ALTER TABLE "app"."track_plan_entitlements" ADD CONSTRAINT "nonnegative_revision" CHECK ("revision" >= 0);

CREATE FUNCTION platform_private.guard_tracksubscription() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE n jsonb:=to_jsonb(NEW); o jsonb; changed text[];
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'direct deletion denied' USING ERRCODE='42501'; END IF;
 IF TG_OP='UPDATE' THEN
  o:=to_jsonb(OLD);
  IF NEW."candidate_profile_id" IS DISTINCT FROM OLD."candidate_profile_id" OR NEW."created_at" IS DISTINCT FROM OLD."created_at" OR NEW."customer_profile_id" IS DISTINCT FROM OLD."customer_profile_id" OR NEW."id" IS DISTINCT FROM OLD."id" OR NEW."mutation_transaction_id" IS DISTINCT FROM OLD."mutation_transaction_id" OR NEW."plan_id" IS DISTINCT FROM OLD."plan_id" OR NEW."professional_profile_id" IS DISTINCT FROM OLD."professional_profile_id" OR NEW."provider_customer_id" IS DISTINCT FROM OLD."provider_customer_id" OR NEW."provider_price_id" IS DISTINCT FROM OLD."provider_price_id" OR NEW."provider_subscription_id" IS DISTINCT FROM OLD."provider_subscription_id" OR NEW."track" IS DISTINCT FROM OLD."track" OR NEW."user_id" IS DISTINCT FROM OLD."user_id" THEN RAISE EXCEPTION 'immutable identity or ownership'; END IF;
  IF NEW.revision<>OLD.revision+1 THEN RAISE EXCEPTION 'CAS revision must increment once'; END IF;
  SELECT COALESCE(array_agg(key),ARRAY[]::text[]) INTO changed FROM jsonb_each(n) WHERE value IS DISTINCT FROM o->key AND key<>'mutation_transaction_id';

  IF NOT platform_private.row_allowed('track_subscription_entitlement','TrackSubscription',(n->>'id'),'UPDATE',array_remove(ARRAY[CASE WHEN 'id'=ANY(changed) THEN 'id' END,CASE WHEN 'user_id'=ANY(changed) THEN 'userId' END,CASE WHEN 'plan_id'=ANY(changed) THEN 'planId' END,CASE WHEN 'track'=ANY(changed) THEN 'track' END,CASE WHEN 'customer_profile_id'=ANY(changed) THEN 'customerProfileId' END,CASE WHEN 'candidate_profile_id'=ANY(changed) THEN 'candidateProfileId' END,CASE WHEN 'professional_profile_id'=ANY(changed) THEN 'professionalProfileId' END,CASE WHEN 'status'=ANY(changed) THEN 'status' END,CASE WHEN 'provider'=ANY(changed) THEN 'provider' END,CASE WHEN 'provider_customer_id'=ANY(changed) THEN 'providerCustomerId' END,CASE WHEN 'provider_subscription_id'=ANY(changed) THEN 'providerSubscriptionId' END,CASE WHEN 'provider_price_id'=ANY(changed) THEN 'providerPriceId' END,CASE WHEN 'current_period_start'=ANY(changed) THEN 'currentPeriodStart' END,CASE WHEN 'current_period_end'=ANY(changed) THEN 'currentPeriodEnd' END,CASE WHEN 'trial_ends_at'=ANY(changed) THEN 'trialEndsAt' END,CASE WHEN 'cancelled_at'=ANY(changed) THEN 'cancelledAt' END,CASE WHEN 'ended_at'=ANY(changed) THEN 'endedAt' END,CASE WHEN 'created_at'=ANY(changed) THEN 'createdAt' END,CASE WHEN 'updated_at'=ANY(changed) THEN 'updatedAt' END,CASE WHEN 'revision'=ANY(changed) THEN 'revision' END,CASE WHEN 'mutation_transaction_id'=ANY(changed) THEN 'mutationTransactionId' END]::text[],NULL),OLD."revision"::text) THEN RAISE EXCEPTION 'field or CAS scope denied' USING ERRCODE='42501'; END IF;
 ELSE
  IF NEW.revision<>0 THEN RAISE EXCEPTION 'initial revision must be zero'; END IF;
  NEW."created_at":=clock_timestamp();
 END IF;
 NEW."updated_at":=clock_timestamp();
 NEW.mutation_transaction_id:=pg_current_xact_id()::text;
 RETURN NEW;
END;
$wa$;

CREATE TRIGGER physical_guard BEFORE INSERT OR UPDATE OR DELETE ON "app"."track_subscriptions" FOR EACH ROW EXECUTE FUNCTION platform_private.guard_tracksubscription();

ALTER TABLE "app"."track_subscriptions" ADD CONSTRAINT "nonnegative_revision" CHECK ("revision" >= 0);

ALTER TABLE "app"."track_subscriptions" ADD CONSTRAINT "ordered_current_period_end" CHECK ("current_period_end" IS NULL OR ("current_period_start" IS NOT NULL AND "current_period_end" > "current_period_start"));

CREATE FUNCTION platform_private.guard_trackentitlementgrant() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE n jsonb:=to_jsonb(NEW); o jsonb; changed text[];
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'direct deletion denied' USING ERRCODE='42501'; END IF;
 IF TG_OP='UPDATE' THEN
  o:=to_jsonb(OLD);
  IF NEW."candidate_profile_id" IS DISTINCT FROM OLD."candidate_profile_id" OR NEW."created_at" IS DISTINCT FROM OLD."created_at" OR NEW."customer_profile_id" IS DISTINCT FROM OLD."customer_profile_id" OR NEW."entitlement_id" IS DISTINCT FROM OLD."entitlement_id" OR NEW."id" IS DISTINCT FROM OLD."id" OR NEW."mutation_transaction_id" IS DISTINCT FROM OLD."mutation_transaction_id" OR NEW."professional_profile_id" IS DISTINCT FROM OLD."professional_profile_id" OR NEW."source_event_id" IS DISTINCT FROM OLD."source_event_id" OR NEW."source_plan_id" IS DISTINCT FROM OLD."source_plan_id" OR NEW."subscription_id" IS DISTINCT FROM OLD."subscription_id" OR NEW."track" IS DISTINCT FROM OLD."track" OR NEW."user_id" IS DISTINCT FROM OLD."user_id" THEN RAISE EXCEPTION 'immutable identity or ownership'; END IF;
  IF NEW.revision<>OLD.revision+1 THEN RAISE EXCEPTION 'CAS revision must increment once'; END IF;
  SELECT COALESCE(array_agg(key),ARRAY[]::text[]) INTO changed FROM jsonb_each(n) WHERE value IS DISTINCT FROM o->key AND key<>'mutation_transaction_id';

  IF NOT platform_private.row_allowed('track_subscription_entitlement','TrackEntitlementGrant',(n->>'id'),'UPDATE',array_remove(ARRAY[CASE WHEN 'id'=ANY(changed) THEN 'id' END,CASE WHEN 'user_id'=ANY(changed) THEN 'userId' END,CASE WHEN 'subscription_id'=ANY(changed) THEN 'subscriptionId' END,CASE WHEN 'entitlement_id'=ANY(changed) THEN 'entitlementId' END,CASE WHEN 'track'=ANY(changed) THEN 'track' END,CASE WHEN 'customer_profile_id'=ANY(changed) THEN 'customerProfileId' END,CASE WHEN 'candidate_profile_id'=ANY(changed) THEN 'candidateProfileId' END,CASE WHEN 'professional_profile_id'=ANY(changed) THEN 'professionalProfileId' END,CASE WHEN 'status'=ANY(changed) THEN 'status' END,CASE WHEN 'value_type'=ANY(changed) THEN 'valueType' END,CASE WHEN 'boolean_value'=ANY(changed) THEN 'booleanValue' END,CASE WHEN 'int_value'=ANY(changed) THEN 'intValue' END,CASE WHEN 'decimal_value'=ANY(changed) THEN 'decimalValue' END,CASE WHEN 'string_value'=ANY(changed) THEN 'stringValue' END,CASE WHEN 'json_value'=ANY(changed) THEN 'jsonValue' END,CASE WHEN 'starts_at'=ANY(changed) THEN 'startsAt' END,CASE WHEN 'expires_at'=ANY(changed) THEN 'expiresAt' END,CASE WHEN 'revoked_at'=ANY(changed) THEN 'revokedAt' END,CASE WHEN 'revoke_reason'=ANY(changed) THEN 'revokeReason' END,CASE WHEN 'source_plan_id'=ANY(changed) THEN 'sourcePlanId' END,CASE WHEN 'source_event_id'=ANY(changed) THEN 'sourceEventId' END,CASE WHEN 'created_at'=ANY(changed) THEN 'createdAt' END,CASE WHEN 'updated_at'=ANY(changed) THEN 'updatedAt' END,CASE WHEN 'revision'=ANY(changed) THEN 'revision' END,CASE WHEN 'mutation_transaction_id'=ANY(changed) THEN 'mutationTransactionId' END]::text[],NULL),OLD."revision"::text) THEN RAISE EXCEPTION 'field or CAS scope denied' USING ERRCODE='42501'; END IF;
 ELSE
  IF NEW.revision<>0 THEN RAISE EXCEPTION 'initial revision must be zero'; END IF;
  NEW."created_at":=clock_timestamp();
 END IF;
 NEW."updated_at":=clock_timestamp();
 NEW.mutation_transaction_id:=pg_current_xact_id()::text;
 RETURN NEW;
END;
$wa$;

CREATE TRIGGER physical_guard BEFORE INSERT OR UPDATE OR DELETE ON "app"."track_entitlement_grants" FOR EACH ROW EXECUTE FUNCTION platform_private.guard_trackentitlementgrant();

ALTER TABLE "app"."track_entitlement_grants" ADD CONSTRAINT "f0_null_json_value" CHECK ("json_value" IS NULL);

ALTER TABLE "app"."track_entitlement_grants" ADD CONSTRAINT "nonnegative_revision" CHECK ("revision" >= 0);

ALTER TABLE "app"."track_entitlement_grants" ADD CONSTRAINT "ordered_expires_at" CHECK ("expires_at" IS NULL OR ("starts_at" IS NOT NULL AND "expires_at" > "starts_at"));

CREATE FUNCTION platform_private.guard_trackusageevent() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE n jsonb:=to_jsonb(NEW); o jsonb; changed text[];
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'direct deletion denied' USING ERRCODE='42501'; END IF;
 IF TG_OP='UPDATE' THEN
  o:=to_jsonb(OLD);
  RAISE EXCEPTION 'immutable evidence or receipt';
 ELSE
 END IF;
 NEW.mutation_transaction_id:=pg_current_xact_id()::text;
 RETURN NEW;
END;
$wa$;

CREATE TRIGGER physical_guard BEFORE INSERT OR UPDATE OR DELETE ON "app"."track_usage_events" FOR EACH ROW EXECUTE FUNCTION platform_private.guard_trackusageevent();

ALTER TABLE "app"."track_usage_events" ADD CONSTRAINT "f0_null_metadata" CHECK ("metadata" IS NULL);

ALTER TABLE "app"."track_usage_events" ADD CONSTRAINT "ordered_period_end" CHECK ("period_end" IS NULL OR ("period_start" IS NOT NULL AND "period_end" > "period_start"));

CREATE FUNCTION platform_private.guard_trackusagecounter() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE n jsonb:=to_jsonb(NEW); o jsonb; changed text[];
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'direct deletion denied' USING ERRCODE='42501'; END IF;
 IF TG_OP='UPDATE' THEN
  o:=to_jsonb(OLD);
  IF NEW."candidate_profile_id" IS DISTINCT FROM OLD."candidate_profile_id" OR NEW."created_at" IS DISTINCT FROM OLD."created_at" OR NEW."customer_profile_id" IS DISTINCT FROM OLD."customer_profile_id" OR NEW."entitlement_grant_id" IS DISTINCT FROM OLD."entitlement_grant_id" OR NEW."entitlement_id" IS DISTINCT FROM OLD."entitlement_id" OR NEW."id" IS DISTINCT FROM OLD."id" OR NEW."mutation_transaction_id" IS DISTINCT FROM OLD."mutation_transaction_id" OR NEW."professional_profile_id" IS DISTINCT FROM OLD."professional_profile_id" OR NEW."subscription_id" IS DISTINCT FROM OLD."subscription_id" OR NEW."track" IS DISTINCT FROM OLD."track" OR NEW."user_id" IS DISTINCT FROM OLD."user_id" THEN RAISE EXCEPTION 'immutable identity or ownership'; END IF;
  IF NEW.revision<>OLD.revision+1 THEN RAISE EXCEPTION 'CAS revision must increment once'; END IF;
  SELECT COALESCE(array_agg(key),ARRAY[]::text[]) INTO changed FROM jsonb_each(n) WHERE value IS DISTINCT FROM o->key AND key<>'mutation_transaction_id';

  IF NOT platform_private.row_allowed('track_subscription_entitlement','TrackUsageCounter',(n->>'id'),'UPDATE',array_remove(ARRAY[CASE WHEN 'id'=ANY(changed) THEN 'id' END,CASE WHEN 'user_id'=ANY(changed) THEN 'userId' END,CASE WHEN 'subscription_id'=ANY(changed) THEN 'subscriptionId' END,CASE WHEN 'entitlement_grant_id'=ANY(changed) THEN 'entitlementGrantId' END,CASE WHEN 'entitlement_id'=ANY(changed) THEN 'entitlementId' END,CASE WHEN 'track'=ANY(changed) THEN 'track' END,CASE WHEN 'period'=ANY(changed) THEN 'period' END,CASE WHEN 'customer_profile_id'=ANY(changed) THEN 'customerProfileId' END,CASE WHEN 'candidate_profile_id'=ANY(changed) THEN 'candidateProfileId' END,CASE WHEN 'professional_profile_id'=ANY(changed) THEN 'professionalProfileId' END,CASE WHEN 'period_start'=ANY(changed) THEN 'periodStart' END,CASE WHEN 'period_end'=ANY(changed) THEN 'periodEnd' END,CASE WHEN 'used_quantity'=ANY(changed) THEN 'usedQuantity' END,CASE WHEN 'limit_quantity'=ANY(changed) THEN 'limitQuantity' END,CASE WHEN 'updated_at'=ANY(changed) THEN 'updatedAt' END,CASE WHEN 'created_at'=ANY(changed) THEN 'createdAt' END,CASE WHEN 'revision'=ANY(changed) THEN 'revision' END,CASE WHEN 'source_revision'=ANY(changed) THEN 'sourceRevision' END,CASE WHEN 'mutation_transaction_id'=ANY(changed) THEN 'mutationTransactionId' END]::text[],NULL),OLD."revision"::text) THEN RAISE EXCEPTION 'field or CAS scope denied' USING ERRCODE='42501'; END IF;
 ELSE
  IF NEW.revision<>0 THEN RAISE EXCEPTION 'initial revision must be zero'; END IF;
  NEW."created_at":=clock_timestamp();
 END IF;
 NEW."updated_at":=clock_timestamp();
 NEW.mutation_transaction_id:=pg_current_xact_id()::text;
 RETURN NEW;
END;
$wa$;

CREATE TRIGGER physical_guard BEFORE INSERT OR UPDATE OR DELETE ON "app"."track_usage_counters" FOR EACH ROW EXECUTE FUNCTION platform_private.guard_trackusagecounter();

ALTER TABLE "app"."track_usage_counters" ADD CONSTRAINT "nonnegative_revision" CHECK ("revision" >= 0);

ALTER TABLE "app"."track_usage_counters" ADD CONSTRAINT "ordered_period_end" CHECK ("period_end" IS NULL OR ("period_start" IS NOT NULL AND "period_end" > "period_start"));

CREATE FUNCTION platform_private.guard_tracksubscriptionevent() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE n jsonb:=to_jsonb(NEW); o jsonb; changed text[];
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'direct deletion denied' USING ERRCODE='42501'; END IF;
 IF TG_OP='UPDATE' THEN
  o:=to_jsonb(OLD);
  RAISE EXCEPTION 'immutable evidence or receipt';
 ELSE
  NEW."created_at":=clock_timestamp();
 END IF;
 NEW.mutation_transaction_id:=pg_current_xact_id()::text;
 RETURN NEW;
END;
$wa$;

CREATE TRIGGER physical_guard BEFORE INSERT OR UPDATE OR DELETE ON "app"."track_subscription_events" FOR EACH ROW EXECUTE FUNCTION platform_private.guard_tracksubscriptionevent();

ALTER TABLE "app"."track_subscription_events" ADD CONSTRAINT "f0_null_metadata" CHECK ("metadata" IS NULL);

CREATE FUNCTION platform_private.guard_consentcontentrevision() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE n jsonb:=to_jsonb(NEW); o jsonb; changed text[];
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'direct deletion denied' USING ERRCODE='42501'; END IF;
 IF TG_OP='UPDATE' THEN
  o:=to_jsonb(OLD);
  RAISE EXCEPTION 'immutable evidence or receipt';
 ELSE
  NEW."created_at":=clock_timestamp();
 END IF;
 NEW.mutation_transaction_id:=pg_current_xact_id()::text;
 RETURN NEW;
END;
$wa$;

CREATE TRIGGER physical_guard BEFORE INSERT OR UPDATE OR DELETE ON "app"."consent_content_revision" FOR EACH ROW EXECUTE FUNCTION platform_private.guard_consentcontentrevision();

ALTER TABLE "app"."consent_content_revision" ADD CONSTRAINT "hash_content_hash" CHECK ("content_hash" ~ '^[0-9a-f]{64}$');

ALTER TABLE "app"."consent_content_revision" ADD CONSTRAINT "ordered_effective_until" CHECK ("effective_until" IS NULL OR ("effective_from" IS NOT NULL AND "effective_until" > "effective_from"));

CREATE FUNCTION platform_private.guard_consentpresentation() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE n jsonb:=to_jsonb(NEW); o jsonb; changed text[];
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'direct deletion denied' USING ERRCODE='42501'; END IF;
 IF TG_OP='UPDATE' THEN
  o:=to_jsonb(OLD);
  RAISE EXCEPTION 'immutable evidence or receipt';
 ELSE
  NEW."created_at":=clock_timestamp();
 END IF;
 IF NOT platform_private.context_subject_owner(NEW.user_id,'consent_disclosure') THEN RAISE EXCEPTION 'foreign Consent presentation principal'; END IF;
 NEW.mutation_transaction_id:=pg_current_xact_id()::text;
 RETURN NEW;
END;
$wa$;

CREATE TRIGGER physical_guard BEFORE INSERT OR UPDATE OR DELETE ON "app"."consent_presentation" FOR EACH ROW EXECUTE FUNCTION platform_private.guard_consentpresentation();

ALTER TABLE "app"."consent_presentation" ADD CONSTRAINT "hash_rendered_hash" CHECK ("rendered_hash" ~ '^[0-9a-f]{64}$');

CREATE FUNCTION platform_private.guard_consentdisposition() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE n jsonb:=to_jsonb(NEW); o jsonb; changed text[];
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'direct deletion denied' USING ERRCODE='42501'; END IF;
 IF TG_OP='UPDATE' THEN
  o:=to_jsonb(OLD);
  RAISE EXCEPTION 'immutable evidence or receipt';
 ELSE
  NEW."created_at":=clock_timestamp();
 END IF;
 NEW.mutation_transaction_id:=pg_current_xact_id()::text;
 RETURN NEW;
END;
$wa$;

CREATE TRIGGER physical_guard BEFORE INSERT OR UPDATE OR DELETE ON "app"."consent_disposition" FOR EACH ROW EXECUTE FUNCTION platform_private.guard_consentdisposition();

ALTER TABLE "app"."consent_disposition" ADD CONSTRAINT "hash_fingerprint" CHECK ("fingerprint" ~ '^[0-9a-f]{64}$');

CREATE FUNCTION platform_private.guard_runtimecommandreceipt() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE n jsonb:=to_jsonb(NEW); o jsonb; changed text[];
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'direct deletion denied' USING ERRCODE='42501'; END IF;
 IF TG_OP='UPDATE' THEN
  o:=to_jsonb(OLD);
  IF NEW."created_at" IS DISTINCT FROM OLD."created_at" OR NEW."fingerprint" IS DISTINCT FROM OLD."fingerprint" OR NEW."id" IS DISTINCT FROM OLD."id" OR NEW."mutation_transaction_id" IS DISTINCT FROM OLD."mutation_transaction_id" OR NEW."operation" IS DISTINCT FROM OLD."operation" OR NEW."owner_module_id" IS DISTINCT FROM OLD."owner_module_id" OR NEW."result_schema_id" IS DISTINCT FROM OLD."result_schema_id" OR NEW."semantic_key" IS DISTINCT FROM OLD."semantic_key" OR NEW."subject_scope" IS DISTINCT FROM OLD."subject_scope" THEN RAISE EXCEPTION 'immutable identity or ownership'; END IF;
  SELECT COALESCE(array_agg(key),ARRAY[]::text[]) INTO changed FROM jsonb_each(n) WHERE value IS DISTINCT FROM o->key AND key<>'mutation_transaction_id';

  IF NOT platform_private.row_allowed(n->>'owner_module_id','RuntimeCommandReceipt',(n->>'id'),'UPDATE',array_remove(ARRAY[CASE WHEN 'id'=ANY(changed) THEN 'id' END,CASE WHEN 'owner_module_id'=ANY(changed) THEN 'ownerModuleId' END,CASE WHEN 'operation'=ANY(changed) THEN 'operation' END,CASE WHEN 'subject_scope'=ANY(changed) THEN 'subjectScope' END,CASE WHEN 'semantic_key'=ANY(changed) THEN 'semanticKey' END,CASE WHEN 'fingerprint'=ANY(changed) THEN 'fingerprint' END,CASE WHEN 'state'=ANY(changed) THEN 'state' END,CASE WHEN 'source_revision'=ANY(changed) THEN 'sourceRevision' END,CASE WHEN 'result_schema_id'=ANY(changed) THEN 'resultSchemaId' END,CASE WHEN 'result_schema_version'=ANY(changed) THEN 'resultSchemaVersion' END,CASE WHEN 'result_digest'=ANY(changed) THEN 'resultDigest' END,CASE WHEN 'result_body'=ANY(changed) THEN 'resultBody' END,CASE WHEN 'created_at'=ANY(changed) THEN 'createdAt' END,CASE WHEN 'mutation_transaction_id'=ANY(changed) THEN 'mutationTransactionId' END]::text[],NULL),NULL::text) THEN RAISE EXCEPTION 'field or CAS scope denied' USING ERRCODE='42501'; END IF;
 ELSE
  NEW."created_at":=clock_timestamp();
 END IF;
 NEW.mutation_transaction_id:=pg_current_xact_id()::text;
 RETURN NEW;
END;
$wa$;

CREATE TRIGGER physical_guard BEFORE INSERT OR UPDATE OR DELETE ON "platform"."runtime_command_receipt" FOR EACH ROW EXECUTE FUNCTION platform_private.guard_runtimecommandreceipt();

ALTER TABLE "platform"."runtime_command_receipt" ADD CONSTRAINT "hash_fingerprint" CHECK ("fingerprint" ~ '^[0-9a-f]{64}$');

ALTER TABLE "platform"."runtime_command_receipt" ADD CONSTRAINT "hash_result_digest" CHECK ("result_digest" ~ '^[0-9a-f]{64}$');

CREATE FUNCTION platform_private.guard_runtimeoutboxmessage() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE n jsonb:=to_jsonb(NEW); o jsonb; changed text[];
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'direct deletion denied' USING ERRCODE='42501'; END IF;
 IF TG_OP='UPDATE' THEN
  o:=to_jsonb(OLD);
  RAISE EXCEPTION 'immutable evidence or receipt';
 ELSE
  NEW."created_at":=clock_timestamp();
 END IF;
 NEW.mutation_transaction_id:=pg_current_xact_id()::text;
 RETURN NEW;
END;
$wa$;

CREATE TRIGGER physical_guard BEFORE INSERT OR UPDATE OR DELETE ON "platform"."runtime_outbox_message" FOR EACH ROW EXECUTE FUNCTION platform_private.guard_runtimeoutboxmessage();

ALTER TABLE "platform"."runtime_outbox_message" ADD CONSTRAINT "nonnegative_source_generation" CHECK ("source_generation" >= 0);

ALTER TABLE "platform"."runtime_outbox_message" ADD CONSTRAINT "hash_payload_hash" CHECK ("payload_hash" ~ '^[0-9a-f]{64}$');

CREATE FUNCTION platform_private.guard_runtimeeffectreceipt() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE n jsonb:=to_jsonb(NEW); o jsonb; changed text[];
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'direct deletion denied' USING ERRCODE='42501'; END IF;
 IF TG_OP='UPDATE' THEN
  o:=to_jsonb(OLD);
  RAISE EXCEPTION 'immutable evidence or receipt';
 ELSE
  NEW."created_at":=clock_timestamp();
 END IF;
 NEW.mutation_transaction_id:=pg_current_xact_id()::text;
 RETURN NEW;
END;
$wa$;

CREATE TRIGGER physical_guard BEFORE INSERT OR UPDATE OR DELETE ON "platform"."runtime_effect_receipt" FOR EACH ROW EXECUTE FUNCTION platform_private.guard_runtimeeffectreceipt();

ALTER TABLE "platform"."runtime_effect_receipt" ADD CONSTRAINT "nonnegative_fence" CHECK ("fence" >= 0);

ALTER TABLE "platform"."runtime_effect_receipt" ADD CONSTRAINT "hash_fingerprint" CHECK ("fingerprint" ~ '^[0-9a-f]{64}$');

ALTER TABLE "platform"."runtime_effect_receipt" ADD CONSTRAINT "hash_result_hash" CHECK ("result_hash" ~ '^[0-9a-f]{64}$');

CREATE FUNCTION platform_private.guard_runtimeworkitem() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE n jsonb:=to_jsonb(NEW); o jsonb; changed text[];
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'direct deletion denied' USING ERRCODE='42501'; END IF;
 IF TG_OP='UPDATE' THEN
  o:=to_jsonb(OLD);
  IF NEW."created_at" IS DISTINCT FROM OLD."created_at" OR NEW."handler_name" IS DISTINCT FROM OLD."handler_name" OR NEW."id" IS DISTINCT FROM OLD."id" OR NEW."mutation_transaction_id" IS DISTINCT FROM OLD."mutation_transaction_id" OR NEW."outbox_message_id" IS DISTINCT FROM OLD."outbox_message_id" OR NEW."semantic_work_key" IS DISTINCT FROM OLD."semantic_work_key" THEN RAISE EXCEPTION 'immutable identity or ownership'; END IF;
  IF NEW."fence"<OLD."fence" THEN RAISE EXCEPTION 'generation/fence regression'; END IF;
  SELECT COALESCE(array_agg(key),ARRAY[]::text[]) INTO changed FROM jsonb_each(n) WHERE value IS DISTINCT FROM o->key AND key<>'mutation_transaction_id';

  IF NOT platform_private.row_allowed('platform_integration_owner','RuntimeWorkItem',(n->>'id'),'UPDATE',array_remove(ARRAY[CASE WHEN 'id'=ANY(changed) THEN 'id' END,CASE WHEN 'outbox_message_id'=ANY(changed) THEN 'outboxMessageId' END,CASE WHEN 'handler_name'=ANY(changed) THEN 'handlerName' END,CASE WHEN 'semantic_work_key'=ANY(changed) THEN 'semanticWorkKey' END,CASE WHEN 'state'=ANY(changed) THEN 'state' END,CASE WHEN 'fence'=ANY(changed) THEN 'fence' END,CASE WHEN 'lease_token_hash'=ANY(changed) THEN 'leaseTokenHash' END,CASE WHEN 'lease_expires_at'=ANY(changed) THEN 'leaseExpiresAt' END,CASE WHEN 'attempt_count'=ANY(changed) THEN 'attemptCount' END,CASE WHEN 'next_attempt_at'=ANY(changed) THEN 'nextAttemptAt' END,CASE WHEN 'effect_receipt_id'=ANY(changed) THEN 'effectReceiptId' END,CASE WHEN 'created_at'=ANY(changed) THEN 'createdAt' END,CASE WHEN 'mutation_transaction_id'=ANY(changed) THEN 'mutationTransactionId' END]::text[],NULL),OLD."fence"::text) THEN RAISE EXCEPTION 'field or CAS scope denied' USING ERRCODE='42501'; END IF;
 ELSE
  NEW."created_at":=clock_timestamp();
 END IF;
 NEW.mutation_transaction_id:=pg_current_xact_id()::text;
 RETURN NEW;
END;
$wa$;

CREATE TRIGGER physical_guard BEFORE INSERT OR UPDATE OR DELETE ON "platform"."runtime_work_item" FOR EACH ROW EXECUTE FUNCTION platform_private.guard_runtimeworkitem();

ALTER TABLE "platform"."runtime_work_item" ADD CONSTRAINT "nonnegative_fence" CHECK ("fence" >= 0);

ALTER TABLE "platform"."runtime_work_item" ADD CONSTRAINT "nonnegative_attempt_count" CHECK ("attempt_count" >= 0);

ALTER TABLE "platform"."runtime_work_item" ADD CONSTRAINT "hash_lease_token_hash" CHECK ("lease_token_hash" ~ '^[0-9a-f]{64}$');

CREATE FUNCTION platform_private.guard_runtimeattempt() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE n jsonb:=to_jsonb(NEW); o jsonb; changed text[];
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'direct deletion denied' USING ERRCODE='42501'; END IF;
 IF TG_OP='UPDATE' THEN
  o:=to_jsonb(OLD);
  RAISE EXCEPTION 'immutable evidence or receipt';
 ELSE
  NEW."created_at":=clock_timestamp();
 END IF;
 NEW.mutation_transaction_id:=pg_current_xact_id()::text;
 RETURN NEW;
END;
$wa$;

CREATE TRIGGER physical_guard BEFORE INSERT OR UPDATE OR DELETE ON "platform"."runtime_attempt" FOR EACH ROW EXECUTE FUNCTION platform_private.guard_runtimeattempt();

ALTER TABLE "platform"."runtime_attempt" ADD CONSTRAINT "nonnegative_fence" CHECK ("fence" >= 0);

ALTER TABLE "platform"."runtime_attempt" ADD CONSTRAINT "ordered_finished_at" CHECK ("finished_at" IS NULL OR ("started_at" IS NOT NULL AND "finished_at" > "started_at"));

CREATE FUNCTION platform_private.guard_runtimeinboxreceipt() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE n jsonb:=to_jsonb(NEW); o jsonb; changed text[];
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'direct deletion denied' USING ERRCODE='42501'; END IF;
 IF TG_OP='UPDATE' THEN
  o:=to_jsonb(OLD);
  RAISE EXCEPTION 'immutable evidence or receipt';
 ELSE
  NEW."created_at":=clock_timestamp();
 END IF;
 NEW.mutation_transaction_id:=pg_current_xact_id()::text;
 RETURN NEW;
END;
$wa$;

CREATE TRIGGER physical_guard BEFORE INSERT OR UPDATE OR DELETE ON "platform"."runtime_inbox_receipt" FOR EACH ROW EXECUTE FUNCTION platform_private.guard_runtimeinboxreceipt();

ALTER TABLE "platform"."runtime_inbox_receipt" ADD CONSTRAINT "hash_payload_hash" CHECK ("payload_hash" ~ '^[0-9a-f]{64}$');

CREATE FUNCTION platform_private.guard_runtimereservation() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE n jsonb:=to_jsonb(NEW); o jsonb; changed text[];
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'direct deletion denied' USING ERRCODE='42501'; END IF;
 IF TG_OP='UPDATE' THEN
  o:=to_jsonb(OLD);
  IF NEW."command_receipt_id" IS DISTINCT FROM OLD."command_receipt_id" OR NEW."created_at" IS DISTINCT FROM OLD."created_at" OR NEW."id" IS DISTINCT FROM OLD."id" OR NEW."mutation_transaction_id" IS DISTINCT FROM OLD."mutation_transaction_id" OR NEW."owner_module_id" IS DISTINCT FROM OLD."owner_module_id" OR NEW."quantity" IS DISTINCT FROM OLD."quantity" OR NEW."resource_key" IS DISTINCT FROM OLD."resource_key" OR NEW."resource_kind" IS DISTINCT FROM OLD."resource_kind" OR NEW."semantic_key" IS DISTINCT FROM OLD."semantic_key" THEN RAISE EXCEPTION 'immutable identity or ownership'; END IF;
  IF NEW."fence"<OLD."fence" THEN RAISE EXCEPTION 'generation/fence regression'; END IF;
  SELECT COALESCE(array_agg(key),ARRAY[]::text[]) INTO changed FROM jsonb_each(n) WHERE value IS DISTINCT FROM o->key AND key<>'mutation_transaction_id';

  IF NOT platform_private.row_allowed(n->>'owner_module_id','RuntimeReservation',(n->>'id'),'UPDATE',array_remove(ARRAY[CASE WHEN 'id'=ANY(changed) THEN 'id' END,CASE WHEN 'command_receipt_id'=ANY(changed) THEN 'commandReceiptId' END,CASE WHEN 'owner_module_id'=ANY(changed) THEN 'ownerModuleId' END,CASE WHEN 'resource_kind'=ANY(changed) THEN 'resourceKind' END,CASE WHEN 'resource_key'=ANY(changed) THEN 'resourceKey' END,CASE WHEN 'semantic_key'=ANY(changed) THEN 'semanticKey' END,CASE WHEN 'quantity'=ANY(changed) THEN 'quantity' END,CASE WHEN 'state'=ANY(changed) THEN 'state' END,CASE WHEN 'fence'=ANY(changed) THEN 'fence' END,CASE WHEN 'effect_receipt_id'=ANY(changed) THEN 'effectReceiptId' END,CASE WHEN 'expires_at'=ANY(changed) THEN 'expiresAt' END,CASE WHEN 'created_at'=ANY(changed) THEN 'createdAt' END,CASE WHEN 'mutation_transaction_id'=ANY(changed) THEN 'mutationTransactionId' END]::text[],NULL),OLD."fence"::text) THEN RAISE EXCEPTION 'field or CAS scope denied' USING ERRCODE='42501'; END IF;
 ELSE
  NEW."created_at":=clock_timestamp();
 END IF;
 NEW.mutation_transaction_id:=pg_current_xact_id()::text;
 RETURN NEW;
END;
$wa$;

CREATE TRIGGER physical_guard BEFORE INSERT OR UPDATE OR DELETE ON "platform"."runtime_reservation" FOR EACH ROW EXECUTE FUNCTION platform_private.guard_runtimereservation();

ALTER TABLE "platform"."runtime_reservation" ADD CONSTRAINT "nonnegative_fence" CHECK ("fence" >= 0);

CREATE FUNCTION platform_private.guard_ownermutationevidence() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE n jsonb:=to_jsonb(NEW); o jsonb; changed text[];
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'direct deletion denied' USING ERRCODE='42501'; END IF;
 IF TG_OP='UPDATE' THEN
  o:=to_jsonb(OLD);
  RAISE EXCEPTION 'immutable evidence or receipt';
 ELSE
  NEW."created_at":=clock_timestamp();
 END IF;
 NEW.mutation_transaction_id:=pg_current_xact_id()::text;
 RETURN NEW;
END;
$wa$;

CREATE TRIGGER physical_guard BEFORE INSERT OR UPDATE OR DELETE ON "platform"."owner_mutation_evidence" FOR EACH ROW EXECUTE FUNCTION platform_private.guard_ownermutationevidence();

ALTER TABLE "platform"."owner_mutation_evidence" ADD CONSTRAINT "hash_evidence_digest" CHECK ("evidence_digest" ~ '^[0-9a-f]{64}$');

CREATE FUNCTION platform_private.guard_customerprofilelifecycleevent() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE n jsonb:=to_jsonb(NEW); o jsonb; changed text[];
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'direct deletion denied' USING ERRCODE='42501'; END IF;
 IF TG_OP='UPDATE' THEN
  o:=to_jsonb(OLD);
  RAISE EXCEPTION 'immutable evidence or receipt';
 ELSE
  NEW."created_at":=clock_timestamp();
 END IF;
 NEW.mutation_transaction_id:=pg_current_xact_id()::text;
 RETURN NEW;
END;
$wa$;

CREATE TRIGGER physical_guard BEFORE INSERT OR UPDATE OR DELETE ON "app"."customer_profile_lifecycle_event" FOR EACH ROW EXECUTE FUNCTION platform_private.guard_customerprofilelifecycleevent();

CREATE FUNCTION platform_private.guard_trackbaseselection() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE n jsonb:=to_jsonb(NEW); o jsonb; changed text[];
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'direct deletion denied' USING ERRCODE='42501'; END IF;
 IF TG_OP='UPDATE' THEN
  o:=to_jsonb(OLD);
  IF NEW."candidate_profile_id" IS DISTINCT FROM OLD."candidate_profile_id" OR NEW."created_at" IS DISTINCT FROM OLD."created_at" OR NEW."customer_profile_id" IS DISTINCT FROM OLD."customer_profile_id" OR NEW."id" IS DISTINCT FROM OLD."id" OR NEW."mutation_transaction_id" IS DISTINCT FROM OLD."mutation_transaction_id" OR NEW."professional_profile_id" IS DISTINCT FROM OLD."professional_profile_id" OR NEW."track" IS DISTINCT FROM OLD."track" OR NEW."user_id" IS DISTINCT FROM OLD."user_id" THEN RAISE EXCEPTION 'immutable identity or ownership'; END IF;
  IF NEW.revision<>OLD.revision+1 THEN RAISE EXCEPTION 'CAS revision must increment once'; END IF;
  IF NEW."source_generation"<OLD."source_generation" THEN RAISE EXCEPTION 'generation/fence regression'; END IF;
  SELECT COALESCE(array_agg(key),ARRAY[]::text[]) INTO changed FROM jsonb_each(n) WHERE value IS DISTINCT FROM o->key AND key<>'mutation_transaction_id';

  IF NOT platform_private.row_allowed('track_subscription_entitlement','TrackBaseSelection',(n->>'id'),'UPDATE',array_remove(ARRAY[CASE WHEN 'id'=ANY(changed) THEN 'id' END,CASE WHEN 'user_id'=ANY(changed) THEN 'userId' END,CASE WHEN 'track'=ANY(changed) THEN 'track' END,CASE WHEN 'customer_profile_id'=ANY(changed) THEN 'customerProfileId' END,CASE WHEN 'candidate_profile_id'=ANY(changed) THEN 'candidateProfileId' END,CASE WHEN 'professional_profile_id'=ANY(changed) THEN 'professionalProfileId' END,CASE WHEN 'subscription_id'=ANY(changed) THEN 'subscriptionId' END,CASE WHEN 'revision'=ANY(changed) THEN 'revision' END,CASE WHEN 'source_generation'=ANY(changed) THEN 'sourceGeneration' END,CASE WHEN 'created_at'=ANY(changed) THEN 'createdAt' END,CASE WHEN 'mutation_transaction_id'=ANY(changed) THEN 'mutationTransactionId' END]::text[],NULL),OLD."revision"::text) THEN RAISE EXCEPTION 'field or CAS scope denied' USING ERRCODE='42501'; END IF;
 ELSE
  IF NEW.revision<>0 THEN RAISE EXCEPTION 'initial revision must be zero'; END IF;
  NEW."created_at":=clock_timestamp();
 END IF;
 NEW.mutation_transaction_id:=pg_current_xact_id()::text;
 RETURN NEW;
END;
$wa$;

CREATE TRIGGER physical_guard BEFORE INSERT OR UPDATE OR DELETE ON "app"."track_base_selection" FOR EACH ROW EXECUTE FUNCTION platform_private.guard_trackbaseselection();

ALTER TABLE "app"."track_base_selection" ADD CONSTRAINT "nonnegative_revision" CHECK ("revision" >= 0);

ALTER TABLE "app"."track_base_selection" ADD CONSTRAINT "nonnegative_source_generation" CHECK ("source_generation" >= 0);

CREATE FUNCTION platform_private.guard_trackenrollmentreceipt() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE n jsonb:=to_jsonb(NEW); o jsonb; changed text[];
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'direct deletion denied' USING ERRCODE='42501'; END IF;
 IF TG_OP='UPDATE' THEN
  o:=to_jsonb(OLD);
  RAISE EXCEPTION 'immutable evidence or receipt';
 ELSE
  NEW."created_at":=clock_timestamp();
 END IF;
 NEW.mutation_transaction_id:=pg_current_xact_id()::text;
 RETURN NEW;
END;
$wa$;

CREATE TRIGGER physical_guard BEFORE INSERT OR UPDATE OR DELETE ON "app"."track_enrollment_receipt" FOR EACH ROW EXECUTE FUNCTION platform_private.guard_trackenrollmentreceipt();

ALTER TABLE "app"."track_enrollment_receipt" ADD CONSTRAINT "hash_fingerprint" CHECK ("fingerprint" ~ '^[0-9a-f]{64}$');

CREATE FUNCTION platform_private.guard_trackusagereservation() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE n jsonb:=to_jsonb(NEW); o jsonb; changed text[];
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'direct deletion denied' USING ERRCODE='42501'; END IF;
 IF TG_OP='UPDATE' THEN
  o:=to_jsonb(OLD);
  IF NEW."accepted_source_id" IS DISTINCT FROM OLD."accepted_source_id" OR NEW."created_at" IS DISTINCT FROM OLD."created_at" OR NEW."entitlement_id" IS DISTINCT FROM OLD."entitlement_id" OR NEW."id" IS DISTINCT FROM OLD."id" OR NEW."mutation_transaction_id" IS DISTINCT FROM OLD."mutation_transaction_id" OR NEW."reservation_id" IS DISTINCT FROM OLD."reservation_id" OR NEW."semantic_key" IS DISTINCT FROM OLD."semantic_key" OR NEW."user_id" IS DISTINCT FROM OLD."user_id" THEN RAISE EXCEPTION 'immutable identity or ownership'; END IF;
  IF NEW.revision<>OLD.revision+1 THEN RAISE EXCEPTION 'CAS revision must increment once'; END IF;
  SELECT COALESCE(array_agg(key),ARRAY[]::text[]) INTO changed FROM jsonb_each(n) WHERE value IS DISTINCT FROM o->key AND key<>'mutation_transaction_id';

  IF NOT platform_private.row_allowed('track_subscription_entitlement','TrackUsageReservation',(n->>'id'),'UPDATE',array_remove(ARRAY[CASE WHEN 'id'=ANY(changed) THEN 'id' END,CASE WHEN 'user_id'=ANY(changed) THEN 'userId' END,CASE WHEN 'entitlement_id'=ANY(changed) THEN 'entitlementId' END,CASE WHEN 'period_start'=ANY(changed) THEN 'periodStart' END,CASE WHEN 'period_end'=ANY(changed) THEN 'periodEnd' END,CASE WHEN 'quantity'=ANY(changed) THEN 'quantity' END,CASE WHEN 'semantic_key'=ANY(changed) THEN 'semanticKey' END,CASE WHEN 'reservation_id'=ANY(changed) THEN 'reservationId' END,CASE WHEN 'accepted_source_owner'=ANY(changed) THEN 'acceptedSourceOwner' END,CASE WHEN 'accepted_source_id'=ANY(changed) THEN 'acceptedSourceId' END,CASE WHEN 'accepted_at'=ANY(changed) THEN 'acceptedAt' END,CASE WHEN 'created_at'=ANY(changed) THEN 'createdAt' END,CASE WHEN 'revision'=ANY(changed) THEN 'revision' END,CASE WHEN 'mutation_transaction_id'=ANY(changed) THEN 'mutationTransactionId' END]::text[],NULL),OLD."revision"::text) THEN RAISE EXCEPTION 'field or CAS scope denied' USING ERRCODE='42501'; END IF;
 ELSE
  IF NEW.revision<>0 THEN RAISE EXCEPTION 'initial revision must be zero'; END IF;
  NEW."created_at":=clock_timestamp();
 END IF;
 NEW.mutation_transaction_id:=pg_current_xact_id()::text;
 RETURN NEW;
END;
$wa$;

CREATE TRIGGER physical_guard BEFORE INSERT OR UPDATE OR DELETE ON "app"."track_usage_reservation" FOR EACH ROW EXECUTE FUNCTION platform_private.guard_trackusagereservation();

ALTER TABLE "app"."track_usage_reservation" ADD CONSTRAINT "nonnegative_revision" CHECK ("revision" >= 0);

ALTER TABLE "app"."track_usage_reservation" ADD CONSTRAINT "ordered_period_end" CHECK ("period_end" IS NULL OR ("period_start" IS NOT NULL AND "period_end" > "period_start"));

CREATE FUNCTION platform_private.guard_privacytargetinstruction() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE n jsonb:=to_jsonb(NEW); o jsonb; changed text[];
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'direct deletion denied' USING ERRCODE='42501'; END IF;
 IF TG_OP='UPDATE' THEN
  o:=to_jsonb(OLD);
  RAISE EXCEPTION 'immutable evidence or receipt';
 ELSE
  NEW."created_at":=clock_timestamp();
 END IF;
 NEW.mutation_transaction_id:=pg_current_xact_id()::text;
 RETURN NEW;
END;
$wa$;

CREATE TRIGGER physical_guard BEFORE INSERT OR UPDATE OR DELETE ON "app"."privacy_target_instruction" FOR EACH ROW EXECUTE FUNCTION platform_private.guard_privacytargetinstruction();

ALTER TABLE "app"."privacy_target_instruction" ADD CONSTRAINT "nonnegative_generation" CHECK ("generation" >= 0);

ALTER TABLE "app"."privacy_target_instruction" ADD CONSTRAINT "hash_descriptor_hash" CHECK ("descriptor_hash" ~ '^[0-9a-f]{64}$');

CREATE FUNCTION platform_private.guard_privacyownerreceipt() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE n jsonb:=to_jsonb(NEW); o jsonb; changed text[];
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'direct deletion denied' USING ERRCODE='42501'; END IF;
 IF TG_OP='UPDATE' THEN
  o:=to_jsonb(OLD);
  RAISE EXCEPTION 'immutable evidence or receipt';
 ELSE
  NEW."created_at":=clock_timestamp();
 END IF;
 NEW.mutation_transaction_id:=pg_current_xact_id()::text;
 RETURN NEW;
END;
$wa$;

CREATE TRIGGER physical_guard BEFORE INSERT OR UPDATE OR DELETE ON "app"."privacy_owner_receipt" FOR EACH ROW EXECUTE FUNCTION platform_private.guard_privacyownerreceipt();

ALTER TABLE "app"."privacy_owner_receipt" ADD CONSTRAINT "nonnegative_generation" CHECK ("generation" >= 0);

ALTER TABLE "app"."privacy_owner_receipt" ADD CONSTRAINT "hash_artifact_digest" CHECK ("artifact_digest" ~ '^[0-9a-f]{64}$');

CREATE FUNCTION platform_private.guard_privacyrestoremarker() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE n jsonb:=to_jsonb(NEW); o jsonb; changed text[];
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'direct deletion denied' USING ERRCODE='42501'; END IF;
 IF TG_OP='UPDATE' THEN
  o:=to_jsonb(OLD);
  IF NEW."created_at" IS DISTINCT FROM OLD."created_at" OR NEW."id" IS DISTINCT FROM OLD."id" OR NEW."mutation_transaction_id" IS DISTINCT FROM OLD."mutation_transaction_id" OR NEW."owner_module_id" IS DISTINCT FROM OLD."owner_module_id" OR NEW."source_id" IS DISTINCT FROM OLD."source_id" OR NEW."source_receipt_id" IS DISTINCT FROM OLD."source_receipt_id" THEN RAISE EXCEPTION 'immutable identity or ownership'; END IF;
  IF NEW.revision<>OLD.revision+1 THEN RAISE EXCEPTION 'CAS revision must increment once'; END IF;
  IF NEW."generation"<OLD."generation" THEN RAISE EXCEPTION 'generation/fence regression'; END IF;
  SELECT COALESCE(array_agg(key),ARRAY[]::text[]) INTO changed FROM jsonb_each(n) WHERE value IS DISTINCT FROM o->key AND key<>'mutation_transaction_id';

  IF NOT platform_private.row_allowed('privacy_data_erasure','PrivacyRestoreMarker',(n->>'id'),'UPDATE',array_remove(ARRAY[CASE WHEN 'id'=ANY(changed) THEN 'id' END,CASE WHEN 'owner_module_id'=ANY(changed) THEN 'ownerModuleId' END,CASE WHEN 'target_kind'=ANY(changed) THEN 'targetKind' END,CASE WHEN 'source_id'=ANY(changed) THEN 'sourceId' END,CASE WHEN 'generation'=ANY(changed) THEN 'generation' END,CASE WHEN 'action'=ANY(changed) THEN 'action' END,CASE WHEN 'source_receipt_id'=ANY(changed) THEN 'sourceReceiptId' END,CASE WHEN 'restore_point_ref'=ANY(changed) THEN 'restorePointRef' END,CASE WHEN 'applied_at'=ANY(changed) THEN 'appliedAt' END,CASE WHEN 'created_at'=ANY(changed) THEN 'createdAt' END,CASE WHEN 'revision'=ANY(changed) THEN 'revision' END,CASE WHEN 'mutation_transaction_id'=ANY(changed) THEN 'mutationTransactionId' END]::text[],NULL),OLD."revision"::text) THEN RAISE EXCEPTION 'field or CAS scope denied' USING ERRCODE='42501'; END IF;
 ELSE
  IF NEW.revision<>0 THEN RAISE EXCEPTION 'initial revision must be zero'; END IF;
  NEW."created_at":=clock_timestamp();
 END IF;
 NEW.mutation_transaction_id:=pg_current_xact_id()::text;
 RETURN NEW;
END;
$wa$;

CREATE TRIGGER physical_guard BEFORE INSERT OR UPDATE OR DELETE ON "app"."privacy_restore_marker" FOR EACH ROW EXECUTE FUNCTION platform_private.guard_privacyrestoremarker();

ALTER TABLE "app"."privacy_restore_marker" ADD CONSTRAINT "nonnegative_revision" CHECK ("revision" >= 0);

ALTER TABLE "app"."privacy_restore_marker" ADD CONSTRAINT "nonnegative_generation" CHECK ("generation" >= 0);

-- SQL-03/04/05/07/08/09/12/14/16: F0 only. Never run in this assignment.
-- This source fragment is assembled after structure/functions and before atomic guards.

ALTER TABLE platform.owner_mutation_evidence ADD CONSTRAINT evidence_identity
 CHECK (evidence_schema_id='urn:workinants:database-review:owner-evidence:v1#/$defs/'||aggregate_kind AND evidence_schema_version='1'
 AND evidence_body->>'schema'='database-owner-evidence.v1' AND evidence_body->>'model'=aggregate_kind
 AND evidence_body->>'owner'=owner_module_id AND evidence_body->>'decisionRef'=decision_ref
 AND length(decision_ref)>0 AND committed_revision>=0
 AND ((previous_revision IS NULL AND committed_revision=0 AND COALESCE(evidence_body->'prior','null'::jsonb)='null'::jsonb)
  OR (previous_revision IS NOT NULL AND previous_revision>=0 AND committed_revision=previous_revision+1 AND COALESCE(jsonb_typeof(evidence_body->'prior')='object',false))));
-- Review SQL storage digest codec: SHA-256 over PostgreSQL 17 jsonb::text UTF-8.
-- Wire serializers must implement this exact storage codec or use a reviewed
-- separate wire digest; equality with an unspecified JSON encoding is not assumed.
ALTER TABLE platform.owner_mutation_evidence ADD CONSTRAINT evidence_storage_digest CHECK
 (evidence_digest=encode(sha256(convert_to(evidence_body::text,'UTF8')),'hex'));
ALTER TABLE platform.runtime_outbox_message ADD CONSTRAINT payload_storage_digest CHECK
 (payload_hash=encode(sha256(convert_to(payload::text,'UTF8')),'hex'));
ALTER TABLE platform.runtime_command_receipt ADD CONSTRAINT result_storage_digest CHECK
 (result_body IS NULL OR (result_digest IS NOT NULL AND result_digest=encode(sha256(convert_to(result_body::text,'UTF8')),'hex')));

CREATE FUNCTION platform_private.message_json_guard() RETURNS trigger
LANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog AS $wa$
BEGIN
 IF NEW.kind='event' AND NEW.name='customer.lifecycle_changed.v1'
  AND NEW.payload_schema_id='urn:workin-ants:types:v1#/$defs/EventPayload_customer_lifecycle_changed_v1'
  AND NEW.schema_version='1' AND NEW.producer_owner='customer_buyer_profile'
  AND platform_private.json_customer_event(NEW.payload)
  AND NEW.payload->>'customerProfileId'=NEW.aggregate_id
  AND NEW.payload->>'lifecycleRevision'=NEW.source_revision::text THEN RETURN NEW; END IF;
 IF NEW.kind='command' AND NEW.name='assignDefaultFreeTrack.v1'
  AND NEW.payload_schema_id='urn:workinants:database-review:foundation-payloads:v1#/$defs/assignDefaultFreeTrackCustomerCommand'
  AND NEW.schema_version='1' AND NEW.producer_owner='customer_buyer_profile'
  AND platform_private.json_track_command(NEW.payload)
  AND NEW.payload->>'customerProfileId'=NEW.aggregate_id
  AND NEW.payload->>'sourceCreationRevision'=NEW.source_revision::text
  AND NEW.payload->>'sourceCreationReceipt'=NEW.command_receipt_id::text
  AND NEW.payload->>'semanticKey'='customer_buyer_profile/'||NEW.aggregate_id||'/default-free-enrollment/v1' THEN RETURN NEW; END IF;
 RAISE EXCEPTION 'unregistered or incoherent F0 message';
END $wa$;
CREATE TRIGGER message_json BEFORE INSERT ON platform.runtime_outbox_message
 FOR EACH ROW EXECUTE FUNCTION platform_private.message_json_guard();

ALTER TABLE platform.runtime_command_receipt ADD CONSTRAINT result_json_boundary CHECK (
 result_body IS NULL OR (
  (operation='SH-004.v1' AND result_schema_id='SH-004.v1#/$defs/response'
   AND platform_private.json_sh004_result(result_body)) OR
  (operation='SH-114.v1' AND result_schema_id='SH-114.v1#/$defs/response'
   AND platform_private.json_sh114_result(result_body)) OR
  (operation='assignDefaultFreeTrack.v1'
   AND result_schema_id='urn:workinants:database-review:foundation-payloads:v1#/$defs/assignDefaultFreeTrackCustomerResult'
   AND platform_private.json_track_result(result_body))
 ));
ALTER TABLE platform.runtime_command_receipt ADD CONSTRAINT result_version_registered CHECK (result_schema_version='1');
ALTER TABLE platform.runtime_command_receipt ADD CONSTRAINT committed_result CHECK
 (state<>'committed' OR (result_digest IS NOT NULL AND
  (operation NOT IN ('SH-004.v1','SH-114.v1','assignDefaultFreeTrack.v1') OR result_body IS NOT NULL)));
ALTER TABLE platform.runtime_outbox_message ADD CONSTRAINT source_message_revision CHECK
 (source_revision>=0 AND source_generation>=0 AND ordinal>=0 AND aggregate_kind='CustomerProfile');

CREATE FUNCTION platform_private.command_state_guard() RETURNS trigger
LANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog AS $wa$
BEGIN
 IF NOT platform_private.command_context_allows(NEW.owner_module_id,NEW.operation,NEW.subject_scope)
  AND NOT EXISTS(SELECT 1 FROM platform.runtime_reservation r WHERE r.command_receipt_id=NEW.id
   AND r.owner_module_id=NEW.owner_module_id
   AND platform_private.context_allows(NEW.owner_module_id,'runtime.reservation.v1','RuntimeReservation',r.id::text,'reservation'))
 THEN RAISE EXCEPTION 'command action/root does not match protected scope'; END IF;
 IF TG_OP='UPDATE' AND (OLD.state IN ('committed','denied','fenced_noncommit')
  OR (to_jsonb(NEW)-ARRAY['state','source_revision','result_digest','result_body','mutation_transaction_id'])
   IS DISTINCT FROM (to_jsonb(OLD)-ARRAY['state','source_revision','result_digest','result_body','mutation_transaction_id']))
 THEN RAISE EXCEPTION 'terminal receipt or semantic identity immutable'; END IF;
 RETURN NEW;
END $wa$;
CREATE TRIGGER command_state BEFORE INSERT OR UPDATE ON platform.runtime_command_receipt
 FOR EACH ROW EXECUTE FUNCTION platform_private.command_state_guard();

ALTER TABLE app.consent_content_revision ADD CONSTRAINT exact_content_hash CHECK
 (content_hash=encode(sha256(convert_to(content_text,'UTF8')),'hex') AND
  (review_state<>'legal_approved' OR NULLIF(legal_approval_ref,'') IS NOT NULL));
ALTER TABLE app.consent_presentation ADD CONSTRAINT exact_rendered_hash CHECK
 (rendered_hash=encode(sha256(convert_to(rendered_text,'UTF8')),'hex'));
CREATE FUNCTION platform_private.consent_guard() RETURNS trigger
LANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog AS $wa$
DECLARE p app.consent_presentation; c app.consent_content_revision; a app.consent_logs;
BEGIN
 IF NOT platform_private.context_subject(NEW.user_id) THEN RAISE EXCEPTION 'accepting subject is not current principal' USING ERRCODE='42501'; END IF;
 IF TG_TABLE_NAME='consent_logs' THEN
  SELECT * INTO STRICT p FROM app.consent_presentation WHERE id=NEW.presentation_id;
  SELECT * INTO STRICT c FROM app.consent_content_revision WHERE id=p.content_revision_id;
  IF p.user_id<>NEW.user_id OR p.content_revision_id<>NEW.content_revision_id
   OR c.type<>NEW.type OR c.version<>NEW.version OR p.rendered_hash<>NEW.presentation_hash
   OR p.action_owner<>NEW.action_owner OR p.action<>NEW.action
   OR p.context_owner<>NEW.context_owner OR p.context_kind<>NEW.context_kind
   OR p.context_id IS DISTINCT FROM NEW.context_id
   OR (NULLIF(NEW.context_id,'') IS NULL AND NOT platform_private.global_context_registered(p.action_owner,p.action,p.context_owner,p.context_kind))
   OR NEW.accepted_at<p.created_at OR NEW.accepted_at<c.effective_from
   OR (c.effective_until IS NOT NULL AND NEW.accepted_at>=c.effective_until)
   OR c.review_state='draft' OR NULLIF(NEW.acceptance_key,'') IS NULL
  THEN RAISE EXCEPTION 'exact consent binding required'; END IF;
  -- Actual rendering, affirmative acceptance and production legal applicability
  -- are trusted Consent-owner code obligations, never inferred from these hashes.
 ELSIF TG_TABLE_NAME='consent_disposition' THEN
  SELECT * INTO STRICT p FROM app.consent_presentation WHERE id=NEW.presentation_id;
  IF p.user_id<>NEW.user_id THEN RAISE EXCEPTION 'foreign consent subject'; END IF;
  IF NEW.proof_id IS NOT NULL THEN
   SELECT * INTO STRICT a FROM app.consent_logs WHERE id=NEW.proof_id;
   IF a.user_id<>NEW.user_id OR a.presentation_id<>NEW.presentation_id THEN RAISE EXCEPTION 'foreign proof'; END IF;
  ELSIF NEW.kind<>'declined' THEN RAISE EXCEPTION 'withdrawal/supersession needs original proof'; END IF;
 END IF;
 RETURN NEW;
END $wa$;
CREATE TRIGGER consent_proof BEFORE INSERT ON app.consent_logs
 FOR EACH ROW EXECUTE FUNCTION platform_private.consent_guard();
CREATE TRIGGER consent_disposition BEFORE INSERT ON app.consent_disposition
 FOR EACH ROW EXECUTE FUNCTION platform_private.consent_guard();
CREATE TRIGGER consent_presentation_subject BEFORE INSERT ON app.consent_presentation
 FOR EACH ROW EXECUTE FUNCTION platform_private.consent_guard();

-- SQL-08: Customer source event and both outbox kinds must describe the same write.
CREATE FUNCTION platform_private.customer_atomic() RETURNS trigger
LANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog AS $wa$
DECLARE e platform.owner_mutation_evidence; h app.customer_profile_lifecycle_event;
BEGIN
 SELECT * INTO STRICT e FROM platform.owner_mutation_evidence WHERE aggregate_kind='CustomerProfile'
  AND aggregate_id=NEW.id::text AND committed_revision=NEW.revision
  AND mutation_transaction_id=pg_current_xact_id()::text;
 SELECT * INTO STRICT h FROM app.customer_profile_lifecycle_event WHERE customer_profile_id=NEW.id
  AND source_revision=NEW.revision AND command_receipt_id=e.command_receipt_id
  AND mutation_transaction_id=e.mutation_transaction_id;
 IF h.to_status<>NEW.status OR h.actor_user_id<>NEW.user_id OR h.name<>'customer.lifecycle_changed.v1'
  OR h.from_status IS DISTINCT FROM (CASE WHEN TG_OP='INSERT' THEN NULL::app.profile_status ELSE OLD.status END)
  OR NOT EXISTS(SELECT 1 FROM platform.runtime_outbox_message o WHERE o.command_receipt_id=e.command_receipt_id
    AND o.aggregate_kind='CustomerProfile' AND o.aggregate_id=NEW.id::text
    AND o.source_revision=NEW.revision AND o.source_generation=NEW.privacy_generation
    AND o.name='customer.lifecycle_changed.v1' AND o.kind='event'
    AND o.payload->>'userId'=NEW.user_id::text AND o.payload->>'safeState'=NEW.status::text
    AND o.mutation_transaction_id=e.mutation_transaction_id)
 THEN RAISE EXCEPTION 'missing atomic Customer lifecycle fact'; END IF;
 IF TG_OP='INSERT' AND NOT EXISTS(SELECT 1 FROM platform.runtime_outbox_message o
   WHERE o.command_receipt_id=e.command_receipt_id AND o.name='assignDefaultFreeTrack.v1' AND o.kind='command'
    AND o.aggregate_id=NEW.id::text AND o.source_revision=NEW.revision
    AND o.source_generation=NEW.privacy_generation AND o.payload->>'userId'=NEW.user_id::text
    AND o.mutation_transaction_id=e.mutation_transaction_id)
 THEN RAISE EXCEPTION 'missing durable default-Free intent'; END IF;
 IF (SELECT count(*) FROM platform.runtime_outbox_message o WHERE o.aggregate_kind='CustomerProfile'
   AND o.aggregate_id=NEW.id::text AND o.source_revision=NEW.revision AND o.command_receipt_id=e.command_receipt_id
   AND o.mutation_transaction_id=e.mutation_transaction_id) <> (CASE WHEN TG_OP='INSERT' THEN 2 ELSE 1 END)
 THEN RAISE EXCEPTION 'extra or missing Customer messages'; END IF;
 RETURN NULL;
END $wa$;
CREATE CONSTRAINT TRIGGER customer_atomic AFTER INSERT OR UPDATE ON app.customer_profiles
 DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.customer_atomic();

CREATE FUNCTION platform_private.customer_message_commit() RETURNS trigger
LANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog AS $wa$
DECLARE e platform.owner_mutation_evidence; h app.customer_profile_lifecycle_event; c app.customer_profiles;
BEGIN
 SELECT * INTO STRICT c FROM app.customer_profiles WHERE id=NEW.aggregate_id::uuid;
 SELECT * INTO STRICT e FROM platform.owner_mutation_evidence WHERE owner_module_id='customer_buyer_profile'
  AND aggregate_kind='CustomerProfile' AND aggregate_id=NEW.aggregate_id AND committed_revision=NEW.source_revision
  AND command_receipt_id=NEW.command_receipt_id AND mutation_transaction_id=NEW.mutation_transaction_id;
 SELECT * INTO STRICT h FROM app.customer_profile_lifecycle_event WHERE customer_profile_id=c.id AND source_revision=NEW.source_revision
  AND command_receipt_id=e.command_receipt_id AND mutation_transaction_id=e.mutation_transaction_id;
 IF c.revision<>NEW.source_revision OR c.privacy_generation<>NEW.source_generation
  OR c.mutation_transaction_id<>NEW.mutation_transaction_id OR NEW.mutation_transaction_id<>pg_current_xact_id()::text
  OR h.name<>'customer.lifecycle_changed.v1' OR h.to_status<>c.status OR h.actor_user_id<>c.user_id
  OR NEW.payload->>'userId'<>c.user_id::text
  OR (NEW.kind='event' AND (NEW.name<>'customer.lifecycle_changed.v1' OR NEW.ordinal<>0 OR NEW.payload->>'safeState'<>c.status::text))
  OR (NEW.kind='command' AND (NEW.name<>'assignDefaultFreeTrack.v1' OR NEW.ordinal<>1 OR e.previous_revision IS NOT NULL OR c.revision<>0 OR h.from_status IS NOT NULL))
  OR (SELECT count(*) FROM platform.runtime_outbox_message m WHERE m.command_receipt_id=e.command_receipt_id
    AND m.aggregate_kind='CustomerProfile' AND m.aggregate_id=c.id::text AND m.source_revision=c.revision
    AND m.mutation_transaction_id=e.mutation_transaction_id) <> (CASE WHEN e.previous_revision IS NULL THEN 2 ELSE 1 END)
 THEN RAISE EXCEPTION 'message does not match exact source/history/count'; END IF;
 RETURN NULL;
END $wa$;
CREATE CONSTRAINT TRIGGER exact_customer_message AFTER INSERT ON platform.runtime_outbox_message
 DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.customer_message_commit();
CREATE FUNCTION platform_private.customer_history_commit() RETURNS trigger
LANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog AS $wa$
DECLARE c app.customer_profiles; e platform.owner_mutation_evidence;
BEGIN
 SELECT * INTO STRICT c FROM app.customer_profiles WHERE id=NEW.customer_profile_id;
 SELECT * INTO STRICT e FROM platform.owner_mutation_evidence WHERE aggregate_kind='CustomerProfile' AND aggregate_id=c.id::text
  AND owner_module_id='customer_buyer_profile' AND committed_revision=NEW.source_revision
  AND command_receipt_id=NEW.command_receipt_id AND mutation_transaction_id=NEW.mutation_transaction_id;
 IF c.mutation_transaction_id<>NEW.mutation_transaction_id OR c.revision<>NEW.source_revision OR c.status<>NEW.to_status
  OR NEW.actor_user_id<>c.user_id OR NEW.name<>'customer.lifecycle_changed.v1'
  OR NEW.from_status::text IS DISTINCT FROM e.evidence_body->'prior'->>'status'
 THEN RAISE EXCEPTION 'orphan Customer history'; END IF;
 RETURN NULL;
END $wa$;
CREATE CONSTRAINT TRIGGER exact_customer_history AFTER INSERT ON app.customer_profile_lifecycle_event
 DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.customer_history_commit();

-- SQL-09: unknown never releases by clock expiry; durable noncommit is necessary.
ALTER TABLE platform.runtime_reservation ADD CONSTRAINT positive_reservation CHECK (quantity>0);
ALTER TABLE platform.runtime_attempt ADD CONSTRAINT attempt_order CHECK (attempt_number>0 AND fence>0);
ALTER TABLE platform.runtime_work_item ADD CONSTRAINT lease_shape CHECK
 ((state IN ('leased','completed') AND lease_token_hash IS NOT NULL AND lease_expires_at IS NOT NULL AND fence>0)
  OR (state NOT IN ('leased','completed') AND lease_token_hash IS NULL AND lease_expires_at IS NULL));
CREATE FUNCTION platform_private.runtime_transition() RETURNS trigger
LANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog AS $wa$
DECLARE w platform.runtime_work_item; e platform.runtime_effect_receipt; c platform.runtime_command_receipt;
BEGIN
 IF TG_TABLE_NAME='runtime_work_item' THEN
  IF TG_OP='INSERT' THEN
   IF session_user::text<>'wa_app_runtime' OR NEW.state<>'pending' OR NEW.fence<>0 OR NEW.attempt_count<>0
    OR NEW.effect_receipt_id IS NOT NULL OR NOT platform_private.context_allows('platform_integration_owner','runtime.schedule_work.v1','RuntimeWorkItem',NEW.id::text,'work.schedule')
   THEN RAISE EXCEPTION 'job must enter through registered scheduler'; END IF;
  END IF;
  IF TG_OP='UPDATE' THEN
   IF OLD.state='completed' OR NEW.attempt_count<OLD.attempt_count THEN RAISE EXCEPTION 'terminal work/regressive attempt'; END IF;
   IF NEW.effect_receipt_id IS DISTINCT FROM OLD.effect_receipt_id THEN
    IF OLD.effect_receipt_id IS NOT NULL OR NEW.effect_receipt_id IS NULL OR OLD.state<>'leased'
     OR NOT platform_private.worker_effect_matches(OLD.id,NEW.effect_receipt_id,false)
    THEN RAISE EXCEPTION 'effect link must be one exact protected attachment'; END IF;
   END IF;
   IF NEW.state='leased' AND (OLD.state<>'leased' OR NEW.lease_token_hash IS DISTINCT FROM OLD.lease_token_hash) THEN
    IF session_user::text<>'wa_worker' OR NOT platform_private.context_allows('platform_integration_owner','runtime.claim_work.v1','RuntimeWorkItem',OLD.id::text,'work.claim')
     OR NEW.fence<>OLD.fence+1 OR NEW.attempt_count<>OLD.attempt_count+1
     OR NEW.lease_expires_at<=clock_timestamp()
     OR (OLD.state='leased' AND OLD.lease_expires_at>clock_timestamp())
     OR NOT platform_private.lease_secret_matches(NEW.lease_token_hash::text)
    THEN RAISE EXCEPTION 'invalid claim/reclaim'; END IF;
   ELSIF NEW.fence<>OLD.fence OR NEW.attempt_count<>OLD.attempt_count
   THEN RAISE EXCEPTION 'fence and attempt may change only on claim'; END IF;
   IF OLD.state='leased' AND NEW.lease_token_hash IS NOT DISTINCT FROM OLD.lease_token_hash AND NEW.state='leased'
    AND NEW.lease_expires_at IS DISTINCT FROM OLD.lease_expires_at THEN
    IF NOT platform_private.context_allows('platform_integration_owner','runtime.renew_work.v1','RuntimeWorkItem',OLD.id::text,'work.renew')
     OR OLD.lease_expires_at<=clock_timestamp() OR NOT platform_private.lease_secret_matches(OLD.lease_token_hash::text)
     OR NEW.lease_expires_at<=OLD.lease_expires_at OR NEW.attempt_count<>OLD.attempt_count
    THEN RAISE EXCEPTION 'renewal requires current secret and extends live lease'; END IF;
   END IF;
   IF OLD.state='leased' AND NEW.state<>'leased' AND (OLD.lease_expires_at<=clock_timestamp()
    OR NOT platform_private.lease_secret_matches(OLD.lease_token_hash::text)
    OR current_setting('wa.fence',true) IS DISTINCT FROM OLD.fence::text)
   THEN RAISE EXCEPTION 'expired or foreign worker'; END IF;
  END IF;
  IF NEW.state='completed' THEN
   SELECT * INTO STRICT e FROM platform.runtime_effect_receipt WHERE id=NEW.effect_receipt_id;
   IF e.state<>'committed' OR e.fence>NEW.fence OR NOT platform_private.worker_effect_matches(NEW.id,e.id,false)
   THEN RAISE EXCEPTION 'completion without exact committed effect and current holder'; END IF;
  END IF;
 ELSIF TG_TABLE_NAME='runtime_attempt' THEN
  SELECT * INTO STRICT w FROM platform.runtime_work_item WHERE id=NEW.work_item_id;
  IF w.fence<>NEW.fence OR NEW.attempt_number<>w.attempt_count OR NOT platform_private.worker_lease_valid(w.id,NULL,true)
  THEN RAISE EXCEPTION 'stale attempt'; END IF;
 ELSIF TG_TABLE_NAME='runtime_reservation' AND TG_OP='INSERT' THEN
  IF NEW.state<>'active' OR NEW.effect_receipt_id IS NOT NULL
  THEN RAISE EXCEPTION 'reservation must start active without outcome'; END IF;
 ELSIF TG_TABLE_NAME='runtime_reservation' AND TG_OP='UPDATE' THEN
  IF OLD.state IN ('committed','released') THEN RAISE EXCEPTION 'terminal reservation'; END IF;
  IF NEW.effect_receipt_id IS DISTINCT FROM OLD.effect_receipt_id AND
   (OLD.effect_receipt_id IS NOT NULL OR NEW.effect_receipt_id IS NULL OR NEW.state NOT IN ('committed','released'))
  THEN RAISE EXCEPTION 'reservation outcome link attaches once at exact terminal proof'; END IF;
  IF NOT ((OLD.state='active' AND NEW.state IN ('active','unknown','committed','released'))
   OR (OLD.state='unknown' AND NEW.state IN ('unknown','committed','released')))
  THEN RAISE EXCEPTION 'unsupported reservation transition'; END IF;
  IF NEW.state IN ('committed','released') THEN
   SELECT * INTO STRICT c FROM platform.runtime_command_receipt WHERE id=NEW.command_receipt_id;
   SELECT * INTO STRICT e FROM platform.runtime_effect_receipt WHERE id=NEW.effect_receipt_id;
   IF e.command_receipt_id IS DISTINCT FROM NEW.command_receipt_id OR e.owner_module_id<>NEW.owner_module_id
    OR c.owner_module_id<>NEW.owner_module_id OR e.operation<>c.operation OR e.fingerprint<>c.fingerprint OR e.fence<>NEW.fence
    OR e.subject_scope<>'RuntimeReservation:'||NEW.id::text OR c.subject_scope<>e.subject_scope
    OR e.semantic_effect_key<>NEW.semantic_key OR c.semantic_key<>NEW.semantic_key
    OR (NEW.state='released' AND (e.state<>'fenced_noncommit' OR c.state<>'fenced_noncommit'
      OR e.mutation_transaction_id<>pg_current_xact_id()::text OR c.mutation_transaction_id<>e.mutation_transaction_id))
    OR (NEW.state='committed' AND (e.state<>'committed' OR c.state<>'committed'))
   THEN RAISE EXCEPTION 'reservation outcome needs exact command/operation/effect proof'; END IF;
  END IF;
 END IF;
 RETURN NEW;
END $wa$;
CREATE TRIGGER work_transition BEFORE INSERT OR UPDATE ON platform.runtime_work_item FOR EACH ROW EXECUTE FUNCTION platform_private.runtime_transition();
CREATE TRIGGER attempt_transition BEFORE INSERT ON platform.runtime_attempt FOR EACH ROW EXECUTE FUNCTION platform_private.runtime_transition();
CREATE TRIGGER reservation_transition BEFORE INSERT OR UPDATE ON platform.runtime_reservation FOR EACH ROW EXECUTE FUNCTION platform_private.runtime_transition();

-- Effect insertion must match the still-current protected work lease, not an
-- arbitrary fence copied from an old message or an untrusted GUC alone.
CREATE FUNCTION platform_private.effect_fence_guard() RETURNS trigger
LANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog AS $wa$
DECLARE w platform.runtime_work_item;
BEGIN
 IF session_user::text='wa_worker' THEN
  SELECT * INTO STRICT w FROM platform.runtime_work_item WHERE effect_receipt_id=NEW.id;
  IF NOT platform_private.worker_lease_valid(w.id,NEW.id,true) OR w.fence<>NEW.fence
   OR NOT platform_private.worker_effect_matches(w.id,NEW.id,true)
  THEN RAISE EXCEPTION 'stale worker effect'; END IF;
 END IF;
 RETURN NULL;
END $wa$;
CREATE CONSTRAINT TRIGGER effect_fence AFTER INSERT ON platform.runtime_effect_receipt
 DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.effect_fence_guard();

-- Locked current selection is authoritative. Catalog retirement alone does not
-- invalidate an already valid selected subscription.
CREATE FUNCTION platform_private.track_enrollment_commit() RETURNS trigger
LANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog AS $wa$
BEGIN
 IF session_user::text<>'wa_worker' THEN
  IF TG_TABLE_NAME IN ('track_subscription_events','track_enrollment_receipt') THEN
   RAISE EXCEPTION 'F0 history/receipt uses qualified worker only'; END IF;
  RETURN NULL;
 END IF;
 IF NOT platform_private.track_atomic_valid(TG_TABLE_NAME,to_jsonb(NEW),CASE WHEN TG_OP='UPDATE' THEN to_jsonb(OLD) ELSE NULL::jsonb END)
 THEN RAISE EXCEPTION 'fixed Track atomic verifier denied'; END IF;
 RETURN NULL;
END $wa$;
CREATE CONSTRAINT TRIGGER enrollment_commit AFTER INSERT OR UPDATE ON app.track_base_selection DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.track_enrollment_commit();
CREATE CONSTRAINT TRIGGER enrollment_commit AFTER INSERT ON app.track_subscriptions DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.track_enrollment_commit();
CREATE CONSTRAINT TRIGGER enrollment_commit AFTER INSERT ON app.track_entitlement_grants DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.track_enrollment_commit();
CREATE CONSTRAINT TRIGGER enrollment_commit AFTER INSERT ON app.track_subscription_events DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.track_enrollment_commit();
CREATE CONSTRAINT TRIGGER enrollment_commit AFTER INSERT ON app.track_enrollment_receipt DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.track_enrollment_commit();

-- SQL-12: typed Track bindings and value arms. No product Track path is activated.
CREATE FUNCTION platform_private.track_binding() RETURNS trigger
LANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog AS $wa$
DECLARE v jsonb:=to_jsonb(NEW); u uuid; plan app.track_plans; sub app.track_subscriptions;
BEGIN
 IF session_user::text='wa_worker' THEN
  IF NOT platform_private.worker_track_allowed(CASE TG_TABLE_NAME WHEN 'track_subscriptions' THEN 'TrackSubscription'
   WHEN 'track_entitlement_grants' THEN 'TrackEntitlementGrant' WHEN 'track_base_selection' THEN 'TrackBaseSelection' END,to_jsonb(NEW),TG_OP)
  THEN RAISE EXCEPTION 'fixed Track binding denied'; END IF;
  RETURN NEW;
 END IF;
 IF v ? 'customer_profile_id' THEN
  IF num_nonnulls(v->>'customer_profile_id',v->>'candidate_profile_id',v->>'professional_profile_id')<>1
   OR ((v->>'track'='customer') IS DISTINCT FROM (v->>'customer_profile_id' IS NOT NULL))
   OR ((v->>'track'='candidate') IS DISTINCT FROM (v->>'candidate_profile_id' IS NOT NULL))
   OR ((v->>'track'='professional') IS DISTINCT FROM (v->>'professional_profile_id' IS NOT NULL))
  THEN RAISE EXCEPTION 'exact typed Track profile required'; END IF;
  IF v->>'track'='customer' THEN
   SELECT user_id INTO STRICT u FROM app.customer_profiles WHERE id=(v->>'customer_profile_id')::uuid;
  ELSIF v->>'track'='candidate' THEN
   SELECT user_id INTO STRICT u FROM app.candidate_profiles WHERE id=(v->>'candidate_profile_id')::uuid;
  ELSE SELECT user_id INTO STRICT u FROM app.professional_profiles WHERE id=(v->>'professional_profile_id')::uuid;
  END IF;
  IF u::text IS DISTINCT FROM v->>'user_id' THEN RAISE EXCEPTION 'foreign Track owner'; END IF;
 END IF;
 IF TG_TABLE_NAME='track_subscriptions' THEN
  SELECT * INTO STRICT plan FROM app.track_plans WHERE id=NEW.plan_id;
  IF plan.track<>NEW.track THEN RAISE EXCEPTION 'foreign plan track'; END IF;
  IF plan.billing_model='free' AND (NEW.provider<>'none' OR NEW.provider_customer_id IS NOT NULL
   OR NEW.provider_subscription_id IS NOT NULL OR NEW.provider_price_id IS NOT NULL)
  THEN RAISE EXCEPTION 'Free must be provider-neutral'; END IF;
 ELSIF TG_TABLE_NAME='track_base_selection' THEN
  PERFORM pg_advisory_xact_lock(hashtextextended('track:'||NEW.user_id::text||':'||NEW.track::text,0));
  SELECT * INTO STRICT sub FROM app.track_subscriptions WHERE id=NEW.subscription_id;
  IF sub.user_id<>NEW.user_id OR sub.track<>NEW.track OR sub.customer_profile_id IS DISTINCT FROM NEW.customer_profile_id
   OR sub.candidate_profile_id IS DISTINCT FROM NEW.candidate_profile_id
   OR sub.professional_profile_id IS DISTINCT FROM NEW.professional_profile_id
  THEN RAISE EXCEPTION 'foreign base selection'; END IF;
 ELSIF TG_TABLE_NAME='track_entitlement_grants' AND NEW.subscription_id IS NOT NULL THEN
  SELECT * INTO STRICT sub FROM app.track_subscriptions WHERE id=NEW.subscription_id;
  IF sub.user_id<>NEW.user_id OR sub.track<>NEW.track OR sub.customer_profile_id IS DISTINCT FROM NEW.customer_profile_id
   OR sub.candidate_profile_id IS DISTINCT FROM NEW.candidate_profile_id
   OR sub.professional_profile_id IS DISTINCT FROM NEW.professional_profile_id
  THEN RAISE EXCEPTION 'foreign entitlement grant'; END IF;
 END IF;
 RETURN NEW;
END $wa$;
CREATE TRIGGER subscription_binding BEFORE INSERT OR UPDATE ON app.track_subscriptions FOR EACH ROW EXECUTE FUNCTION platform_private.track_binding();
CREATE TRIGGER grant_binding BEFORE INSERT OR UPDATE ON app.track_entitlement_grants FOR EACH ROW EXECUTE FUNCTION platform_private.track_binding();
CREATE TRIGGER selection_binding BEFORE INSERT OR UPDATE ON app.track_base_selection FOR EACH ROW EXECUTE FUNCTION platform_private.track_binding();

ALTER TABLE app.track_plan_entitlements ADD CONSTRAINT typed_plan_value CHECK
 ((value_type='boolean' AND boolean_value IS NOT NULL AND int_value IS NULL AND decimal_value IS NULL AND string_value IS NULL)
 OR (value_type IN ('integer','percent_bps','money_cents') AND int_value IS NOT NULL AND boolean_value IS NULL AND decimal_value IS NULL AND string_value IS NULL)
 OR (value_type='decimal' AND decimal_value IS NOT NULL AND int_value IS NULL AND boolean_value IS NULL AND string_value IS NULL)
 OR (value_type='string' AND string_value IS NOT NULL AND int_value IS NULL AND decimal_value IS NULL AND boolean_value IS NULL));
ALTER TABLE app.track_entitlement_grants ADD CONSTRAINT typed_grant_value CHECK
 ((value_type='boolean' AND boolean_value IS NOT NULL AND int_value IS NULL AND decimal_value IS NULL AND string_value IS NULL)
 OR (value_type IN ('integer','percent_bps','money_cents') AND int_value IS NOT NULL AND boolean_value IS NULL AND decimal_value IS NULL AND string_value IS NULL)
 OR (value_type='decimal' AND decimal_value IS NOT NULL AND int_value IS NULL AND boolean_value IS NULL AND string_value IS NULL)
 OR (value_type='string' AND string_value IS NOT NULL AND int_value IS NULL AND decimal_value IS NULL AND boolean_value IS NULL));
ALTER TABLE app.track_plan_entitlements ADD CONSTRAINT plan_value_bounds CHECK
 ((value_type<>'percent_bps' OR int_value BETWEEN 0 AND 10000) AND (value_type<>'money_cents' OR int_value>=0)
 AND (decimal_value IS NULL OR decimal_value NOT IN ('NaN'::float8,'Infinity'::float8,'-Infinity'::float8)));
ALTER TABLE app.track_entitlement_grants ADD CONSTRAINT grant_value_bounds CHECK
 ((value_type<>'percent_bps' OR int_value BETWEEN 0 AND 10000) AND (value_type<>'money_cents' OR int_value>=0)
 AND (decimal_value IS NULL OR decimal_value NOT IN ('NaN'::float8,'Infinity'::float8,'-Infinity'::float8)));
ALTER TABLE app.track_usage_events ADD CONSTRAINT usage_window CHECK (quantity>0 AND accepted_at>=period_start AND accepted_at<period_end);
ALTER TABLE app.track_usage_reservation ADD CONSTRAINT usage_reservation_window CHECK (quantity>0 AND
 (accepted_at IS NULL OR (accepted_at>=period_start AND accepted_at<period_end)));
ALTER TABLE app.track_usage_counters ADD CONSTRAINT counter_bounds CHECK (used_quantity>=0 AND (limit_quantity IS NULL OR limit_quantity>=0));
-- Quota period calculation and event-derived counter reconciliation are owner-code
-- dependencies. In this draft direct usage mutation is blocked until qualified.
CREATE FUNCTION platform_private.block_usage_mutation() RETURNS trigger
LANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog AS $wa$
BEGIN RAISE EXCEPTION 'usage mutation requires separately qualified period/reconciliation owner adapter' USING ERRCODE='0A000'; END $wa$;
CREATE TRIGGER usage_adapter_gate BEFORE INSERT OR UPDATE ON app.track_usage_events FOR EACH ROW EXECUTE FUNCTION platform_private.block_usage_mutation();
CREATE TRIGGER usage_adapter_gate BEFORE INSERT OR UPDATE ON app.track_usage_counters FOR EACH ROW EXECUTE FUNCTION platform_private.block_usage_mutation();
CREATE TRIGGER usage_adapter_gate BEFORE INSERT OR UPDATE ON app.track_usage_reservation FOR EACH ROW EXECUTE FUNCTION platform_private.block_usage_mutation();

-- SQL-14: versioned owner instructions, receipts and restoration markers.
ALTER TABLE app.privacy_owner_receipt ADD CONSTRAINT retained_basis CHECK
 (disposition<>'retained' OR NULLIF(legal_basis_ref,'') IS NOT NULL);
CREATE FUNCTION platform_private.privacy_guard() RETURNS trigger
LANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog AS $wa$
DECLARE i app.privacy_target_instruction; r app.privacy_requests; p app.privacy_owner_receipt;
BEGIN
 IF TG_TABLE_NAME='privacy_target_instruction' THEN
  SELECT * INTO STRICT r FROM app.privacy_requests WHERE id=NEW.privacy_request_id;
  IF r.verified_at IS NULL OR r.status NOT IN ('verified','processing')
   OR r.instruction_generation<>NEW.generation OR NEW.field_map_version='' OR NEW.executor_version=''
  THEN RAISE EXCEPTION 'unverified or stale privacy instruction'; END IF;
 ELSIF TG_TABLE_NAME='privacy_owner_receipt' THEN
  SELECT * INTO STRICT i FROM app.privacy_target_instruction WHERE id=NEW.instruction_id;
  SELECT * INTO STRICT r FROM app.privacy_requests WHERE id=i.privacy_request_id;
  IF i.generation<>NEW.generation OR r.instruction_generation<>NEW.generation OR r.verified_at IS NULL
  THEN RAISE EXCEPTION 'stale privacy disposition'; END IF;
  IF NEW.disposition='completed' THEN
   RAISE EXCEPTION 'completed execution needs qualified owner field-map and exact-byte/provider evidence' USING ERRCODE='0A000';
  END IF;
 ELSIF TG_TABLE_NAME='privacy_restore_marker' THEN
  SELECT * INTO STRICT p FROM app.privacy_owner_receipt WHERE id=NEW.source_receipt_id;
  SELECT * INTO STRICT i FROM app.privacy_target_instruction WHERE id=p.instruction_id;
  IF NEW.generation<>i.generation OR NEW.owner_module_id<>i.owner_module_id
   OR NEW.target_kind<>i.target_kind OR NEW.source_id<>i.source_id OR NEW.action<>i.action
   OR p.disposition NOT IN ('completed','retained') THEN RAISE EXCEPTION 'incoherent restore marker'; END IF;
 ELSIF TG_TABLE_NAME='privacy_requests' THEN
  IF TG_OP='UPDATE' AND NEW.requested_at IS DISTINCT FROM OLD.requested_at THEN RAISE EXCEPTION 'request origin immutable'; END IF;
  IF NEW.status IN ('completed','partially_completed') OR NEW.completed_at IS NOT NULL THEN
   RAISE EXCEPTION 'request completion requires qualified full owner accounting' USING ERRCODE='0A000';
  END IF;
 END IF;
 RETURN NEW;
END $wa$;
CREATE TRIGGER privacy_instruction BEFORE INSERT ON app.privacy_target_instruction FOR EACH ROW EXECUTE FUNCTION platform_private.privacy_guard();
CREATE TRIGGER privacy_receipt BEFORE INSERT ON app.privacy_owner_receipt FOR EACH ROW EXECUTE FUNCTION platform_private.privacy_guard();
CREATE TRIGGER privacy_restore BEFORE INSERT OR UPDATE ON app.privacy_restore_marker FOR EACH ROW EXECUTE FUNCTION platform_private.privacy_guard();
CREATE TRIGGER privacy_request BEFORE INSERT OR UPDATE ON app.privacy_requests FOR EACH ROW EXECUTE FUNCTION platform_private.privacy_guard();

-- SQL-08/09 nonrecursive infrastructure roots: FK/semantic/txn guards, not evidence-of-evidence.
CREATE FUNCTION platform_private.infrastructure_atomic() RETURNS trigger
LANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog AS $wa$
DECLARE c platform.runtime_command_receipt; o platform.runtime_outbox_message; e platform.runtime_effect_receipt; w platform.runtime_work_item;
BEGIN
 IF TG_TABLE_NAME IN ('owner_mutation_evidence','runtime_outbox_message') THEN
  SELECT * INTO STRICT c FROM platform.runtime_command_receipt WHERE id=NEW.command_receipt_id;
  IF c.state<>'committed' OR c.mutation_transaction_id<>NEW.mutation_transaction_id THEN RAISE EXCEPTION 'foreign transaction command'; END IF;
  IF TG_TABLE_NAME='owner_mutation_evidence' AND (c.owner_module_id<>NEW.owner_module_id OR c.operation<>NEW.action)
   THEN RAISE EXCEPTION 'foreign owner command'; END IF;
 ELSIF TG_TABLE_NAME='runtime_inbox_receipt' THEN
  SELECT * INTO STRICT o FROM platform.runtime_outbox_message WHERE id=NEW.outbox_message_id;
  SELECT * INTO STRICT e FROM platform.runtime_effect_receipt WHERE id=NEW.effect_receipt_id;
  SELECT * INTO STRICT w FROM platform.runtime_work_item WHERE outbox_message_id=o.id AND handler_name=NEW.handler_name;
  IF o.payload_hash<>NEW.payload_hash OR e.owner_module_id<>NEW.consumer_owner OR e.state<>'committed'
   OR e.mutation_transaction_id<>NEW.mutation_transaction_id OR e.fence<>w.fence
   OR NOT platform_private.worker_lease_valid(w.id,e.id,true)
   OR NOT platform_private.worker_effect_matches(w.id,e.id,true)
  THEN RAISE EXCEPTION 'stale or incoherent inbox effect'; END IF;
 END IF;
 RETURN NULL;
END $wa$;
CREATE CONSTRAINT TRIGGER infrastructure_commit AFTER INSERT ON platform.owner_mutation_evidence DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.infrastructure_atomic();
CREATE CONSTRAINT TRIGGER infrastructure_commit AFTER INSERT ON platform.runtime_outbox_message DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.infrastructure_atomic();
CREATE CONSTRAINT TRIGGER infrastructure_commit AFTER INSERT ON platform.runtime_inbox_receipt DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.infrastructure_atomic();

CREATE FUNCTION platform_private.commit_consentlog() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE e platform.owner_mutation_evidence; prior_value jsonb;
BEGIN
 prior_value:=CASE WHEN TG_OP='UPDATE' THEN jsonb_build_object('id',to_jsonb(OLD."id"),'userId',to_jsonb(OLD."user_id"),'type',to_jsonb(OLD."type"),'acceptedAt',to_jsonb(OLD."accepted_at"),'ipHash',to_jsonb(OLD."ip_hash"),'presentationHash',to_jsonb(OLD."presentation_hash")) ELSE 'null'::jsonb END;
 SELECT * INTO e FROM platform.owner_mutation_evidence WHERE aggregate_kind='ConsentLog'
  AND aggregate_id=(to_jsonb(NEW)->>'id') AND committed_revision=0::bigint
  AND owner_module_id='consent_disclosure' AND mutation_transaction_id=pg_current_xact_id()::text;
 IF NOT FOUND OR e.evidence_body->'primaryKey' IS DISTINCT FROM jsonb_build_object('id',NEW."id")
  OR e.evidence_body->'committed' IS DISTINCT FROM jsonb_build_object('id',to_jsonb(NEW."id"),'userId',to_jsonb(NEW."user_id"),'type',to_jsonb(NEW."type"),'acceptedAt',to_jsonb(NEW."accepted_at"),'ipHash',to_jsonb(NEW."ip_hash"),'presentationHash',to_jsonb(NEW."presentation_hash"))
  OR COALESCE(e.evidence_body->'prior','null'::jsonb) IS DISTINCT FROM prior_value
  OR e.previous_revision IS DISTINCT FROM (CASE WHEN TG_OP='UPDATE' THEN 0::bigint ELSE NULL::bigint END)
  OR e.decision_ref IS DISTINCT FROM e.evidence_body->>'decisionRef'
  OR NOT platform_private.json_evidence_consentlog(e.evidence_body)
  OR NOT EXISTS(SELECT 1 FROM platform.runtime_command_receipt c WHERE c.id=e.command_receipt_id
   AND c.mutation_transaction_id=e.mutation_transaction_id AND c.owner_module_id=e.owner_module_id
   AND c.state='committed' AND c.operation=e.action )
 THEN RAISE EXCEPTION 'missing exact atomic owner proof for ConsentLog'; END IF;
 RETURN NULL;
END;
$wa$;

CREATE CONSTRAINT TRIGGER owner_commit AFTER INSERT OR UPDATE ON "app"."consent_logs" DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.commit_consentlog();

CREATE FUNCTION platform_private.commit_privacyrequest() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE e platform.owner_mutation_evidence; prior_value jsonb;
BEGIN
 prior_value:=CASE WHEN TG_OP='UPDATE' THEN jsonb_build_object('id',to_jsonb(OLD."id"),'userId',to_jsonb(OLD."user_id"),'type',to_jsonb(OLD."type"),'status',to_jsonb(OLD."status"),'revision',to_jsonb(OLD."revision"::text),'privacyGeneration',to_jsonb(OLD."privacy_generation"::text),'instructionGeneration',to_jsonb(OLD."instruction_generation"::text)) ELSE 'null'::jsonb END;
 SELECT * INTO e FROM platform.owner_mutation_evidence WHERE aggregate_kind='PrivacyRequest'
  AND aggregate_id=(to_jsonb(NEW)->>'id') AND committed_revision=NEW.revision
  AND owner_module_id='privacy_data_erasure' AND mutation_transaction_id=pg_current_xact_id()::text;
 IF NOT FOUND OR e.evidence_body->'primaryKey' IS DISTINCT FROM jsonb_build_object('id',NEW."id")
  OR e.evidence_body->'committed' IS DISTINCT FROM jsonb_build_object('id',to_jsonb(NEW."id"),'userId',to_jsonb(NEW."user_id"),'type',to_jsonb(NEW."type"),'status',to_jsonb(NEW."status"),'revision',to_jsonb(NEW."revision"::text),'privacyGeneration',to_jsonb(NEW."privacy_generation"::text),'instructionGeneration',to_jsonb(NEW."instruction_generation"::text))
  OR COALESCE(e.evidence_body->'prior','null'::jsonb) IS DISTINCT FROM prior_value
  OR e.previous_revision IS DISTINCT FROM (CASE WHEN TG_OP='UPDATE' THEN OLD.revision ELSE NULL::bigint END)
  OR e.decision_ref IS DISTINCT FROM e.evidence_body->>'decisionRef'
  OR NOT platform_private.json_evidence_privacyrequest(e.evidence_body)
  OR NOT EXISTS(SELECT 1 FROM platform.runtime_command_receipt c WHERE c.id=e.command_receipt_id
   AND c.mutation_transaction_id=e.mutation_transaction_id AND c.owner_module_id=e.owner_module_id
   AND c.state='committed' AND c.operation=e.action )
 THEN RAISE EXCEPTION 'missing exact atomic owner proof for PrivacyRequest'; END IF;
 RETURN NULL;
END;
$wa$;

CREATE CONSTRAINT TRIGGER owner_commit AFTER INSERT OR UPDATE ON "app"."privacy_requests" DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.commit_privacyrequest();

CREATE FUNCTION platform_private.commit_agegateattempt() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE e platform.owner_mutation_evidence; prior_value jsonb;
BEGIN
 prior_value:=CASE WHEN TG_OP='UPDATE' THEN jsonb_build_object('id',to_jsonb(OLD."id"),'userId',to_jsonb(OLD."user_id"),'ipHash',to_jsonb(OLD."ip_hash"),'deviceHash',to_jsonb(OLD."device_hash"),'result',to_jsonb(OLD."result")) ELSE 'null'::jsonb END;
 SELECT * INTO e FROM platform.owner_mutation_evidence WHERE aggregate_kind='AgeGateAttempt'
  AND aggregate_id=(to_jsonb(NEW)->>'id') AND committed_revision=0::bigint
  AND owner_module_id='identity_access' AND mutation_transaction_id=pg_current_xact_id()::text;
 IF NOT FOUND OR e.evidence_body->'primaryKey' IS DISTINCT FROM jsonb_build_object('id',NEW."id")
  OR e.evidence_body->'committed' IS DISTINCT FROM jsonb_build_object('id',to_jsonb(NEW."id"),'userId',to_jsonb(NEW."user_id"),'ipHash',to_jsonb(NEW."ip_hash"),'deviceHash',to_jsonb(NEW."device_hash"),'result',to_jsonb(NEW."result"))
  OR COALESCE(e.evidence_body->'prior','null'::jsonb) IS DISTINCT FROM prior_value
  OR e.previous_revision IS DISTINCT FROM (CASE WHEN TG_OP='UPDATE' THEN 0::bigint ELSE NULL::bigint END)
  OR e.decision_ref IS DISTINCT FROM e.evidence_body->>'decisionRef'
  OR NOT platform_private.json_evidence_agegateattempt(e.evidence_body)
  OR NOT EXISTS(SELECT 1 FROM platform.runtime_command_receipt c WHERE c.id=e.command_receipt_id
   AND c.mutation_transaction_id=e.mutation_transaction_id AND c.owner_module_id=e.owner_module_id
   AND c.state='committed' AND c.operation=e.action )
 THEN RAISE EXCEPTION 'missing exact atomic owner proof for AgeGateAttempt'; END IF;
 RETURN NULL;
END;
$wa$;

CREATE CONSTRAINT TRIGGER owner_commit AFTER INSERT OR UPDATE ON "app"."age_gate_attempts" DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.commit_agegateattempt();

CREATE FUNCTION platform_private.commit_agegateblock() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE e platform.owner_mutation_evidence; prior_value jsonb;
BEGIN
 prior_value:=CASE WHEN TG_OP='UPDATE' THEN jsonb_build_object('id',to_jsonb(OLD."id"),'ipHash',to_jsonb(OLD."ip_hash"),'deviceHash',to_jsonb(OLD."device_hash")) ELSE 'null'::jsonb END;
 SELECT * INTO e FROM platform.owner_mutation_evidence WHERE aggregate_kind='AgeGateBlock'
  AND aggregate_id=(to_jsonb(NEW)->>'id') AND committed_revision=0::bigint
  AND owner_module_id='identity_access' AND mutation_transaction_id=pg_current_xact_id()::text;
 IF NOT FOUND OR e.evidence_body->'primaryKey' IS DISTINCT FROM jsonb_build_object('id',NEW."id")
  OR e.evidence_body->'committed' IS DISTINCT FROM jsonb_build_object('id',to_jsonb(NEW."id"),'ipHash',to_jsonb(NEW."ip_hash"),'deviceHash',to_jsonb(NEW."device_hash"))
  OR COALESCE(e.evidence_body->'prior','null'::jsonb) IS DISTINCT FROM prior_value
  OR e.previous_revision IS DISTINCT FROM (CASE WHEN TG_OP='UPDATE' THEN 0::bigint ELSE NULL::bigint END)
  OR e.decision_ref IS DISTINCT FROM e.evidence_body->>'decisionRef'
  OR NOT platform_private.json_evidence_agegateblock(e.evidence_body)
  OR NOT EXISTS(SELECT 1 FROM platform.runtime_command_receipt c WHERE c.id=e.command_receipt_id
   AND c.mutation_transaction_id=e.mutation_transaction_id AND c.owner_module_id=e.owner_module_id
   AND c.state='committed' AND c.operation=e.action )
 THEN RAISE EXCEPTION 'missing exact atomic owner proof for AgeGateBlock'; END IF;
 RETURN NULL;
END;
$wa$;

CREATE CONSTRAINT TRIGGER owner_commit AFTER INSERT OR UPDATE ON "app"."age_gate_blocks" DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.commit_agegateblock();

CREATE FUNCTION platform_private.commit_accessauditlog() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE e platform.owner_mutation_evidence; prior_value jsonb;
BEGIN
 prior_value:=CASE WHEN TG_OP='UPDATE' THEN jsonb_build_object('id',to_jsonb(OLD."id"),'action',to_jsonb(OLD."action"),'sensitivity',to_jsonb(OLD."sensitivity"),'accessDecision',to_jsonb(OLD."access_decision"),'ipHash',to_jsonb(OLD."ip_hash"),'previousHash',to_jsonb(OLD."previous_hash"),'entryHash',to_jsonb(OLD."entry_hash")) ELSE 'null'::jsonb END;
 SELECT * INTO e FROM platform.owner_mutation_evidence WHERE aggregate_kind='AccessAuditLog'
  AND aggregate_id=(to_jsonb(NEW)->>'id') AND committed_revision=0::bigint
  AND owner_module_id='audit_event_ledger' AND mutation_transaction_id=pg_current_xact_id()::text;
 IF NOT FOUND OR e.evidence_body->'primaryKey' IS DISTINCT FROM jsonb_build_object('id',NEW."id")
  OR e.evidence_body->'committed' IS DISTINCT FROM jsonb_build_object('id',to_jsonb(NEW."id"),'action',to_jsonb(NEW."action"),'sensitivity',to_jsonb(NEW."sensitivity"),'accessDecision',to_jsonb(NEW."access_decision"),'ipHash',to_jsonb(NEW."ip_hash"),'previousHash',to_jsonb(NEW."previous_hash"),'entryHash',to_jsonb(NEW."entry_hash"))
  OR COALESCE(e.evidence_body->'prior','null'::jsonb) IS DISTINCT FROM prior_value
  OR e.previous_revision IS DISTINCT FROM (CASE WHEN TG_OP='UPDATE' THEN 0::bigint ELSE NULL::bigint END)
  OR e.decision_ref IS DISTINCT FROM e.evidence_body->>'decisionRef'
  OR NOT platform_private.json_evidence_accessauditlog(e.evidence_body)
  OR NOT EXISTS(SELECT 1 FROM platform.runtime_command_receipt c WHERE c.id=e.command_receipt_id
   AND c.mutation_transaction_id=e.mutation_transaction_id AND c.owner_module_id=e.owner_module_id
   AND c.state='committed' AND c.operation=e.action )
 THEN RAISE EXCEPTION 'missing exact atomic owner proof for AccessAuditLog'; END IF;
 RETURN NULL;
END;
$wa$;

CREATE CONSTRAINT TRIGGER owner_commit AFTER INSERT OR UPDATE ON "app"."access_audit_logs" DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.commit_accessauditlog();

CREATE FUNCTION platform_private.commit_user() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE e platform.owner_mutation_evidence; prior_value jsonb;
BEGIN
 prior_value:=CASE WHEN TG_OP='UPDATE' THEN jsonb_build_object('id',to_jsonb(OLD."id"),'revision',to_jsonb(OLD."revision"::text),'privacyGeneration',to_jsonb(OLD."privacy_generation"::text)) ELSE 'null'::jsonb END;
 SELECT * INTO e FROM platform.owner_mutation_evidence WHERE aggregate_kind='User'
  AND aggregate_id=(to_jsonb(NEW)->>'id') AND committed_revision=NEW.revision
  AND owner_module_id='identity_access' AND mutation_transaction_id=pg_current_xact_id()::text;
 IF NOT FOUND OR e.evidence_body->'primaryKey' IS DISTINCT FROM jsonb_build_object('id',NEW."id")
  OR e.evidence_body->'committed' IS DISTINCT FROM jsonb_build_object('id',to_jsonb(NEW."id"),'revision',to_jsonb(NEW."revision"::text),'privacyGeneration',to_jsonb(NEW."privacy_generation"::text))
  OR COALESCE(e.evidence_body->'prior','null'::jsonb) IS DISTINCT FROM prior_value
  OR e.previous_revision IS DISTINCT FROM (CASE WHEN TG_OP='UPDATE' THEN OLD.revision ELSE NULL::bigint END)
  OR e.decision_ref IS DISTINCT FROM e.evidence_body->>'decisionRef'
  OR NOT platform_private.json_evidence_user(e.evidence_body)
  OR NOT EXISTS(SELECT 1 FROM platform.runtime_command_receipt c WHERE c.id=e.command_receipt_id
   AND c.mutation_transaction_id=e.mutation_transaction_id AND c.owner_module_id=e.owner_module_id
   AND c.state='committed' AND c.operation=e.action )
 THEN RAISE EXCEPTION 'missing exact atomic owner proof for User'; END IF;
 RETURN NULL;
END;
$wa$;

CREATE CONSTRAINT TRIGGER owner_commit AFTER INSERT OR UPDATE ON "app"."users" DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.commit_user();

CREATE FUNCTION platform_private.commit_userrole() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE e platform.owner_mutation_evidence; prior_value jsonb;
BEGIN
 prior_value:=CASE WHEN TG_OP='UPDATE' THEN jsonb_build_object('userId',to_jsonb(OLD."user_id"),'role',to_jsonb(OLD."role"),'revision',to_jsonb(OLD."revision"::text)) ELSE 'null'::jsonb END;
 SELECT * INTO e FROM platform.owner_mutation_evidence WHERE aggregate_kind='UserRole'
  AND aggregate_id=(to_jsonb(NEW)->>'user_id') || ':' || (to_jsonb(NEW)->>'role') AND committed_revision=NEW.revision
  AND owner_module_id='identity_access' AND mutation_transaction_id=pg_current_xact_id()::text;
 IF NOT FOUND OR e.evidence_body->'primaryKey' IS DISTINCT FROM jsonb_build_object('userId',NEW."user_id",'role',NEW."role")
  OR e.evidence_body->'committed' IS DISTINCT FROM jsonb_build_object('userId',to_jsonb(NEW."user_id"),'role',to_jsonb(NEW."role"),'revision',to_jsonb(NEW."revision"::text))
  OR COALESCE(e.evidence_body->'prior','null'::jsonb) IS DISTINCT FROM prior_value
  OR e.previous_revision IS DISTINCT FROM (CASE WHEN TG_OP='UPDATE' THEN OLD.revision ELSE NULL::bigint END)
  OR e.decision_ref IS DISTINCT FROM e.evidence_body->>'decisionRef'
  OR NOT platform_private.json_evidence_userrole(e.evidence_body)
  OR NOT EXISTS(SELECT 1 FROM platform.runtime_command_receipt c WHERE c.id=e.command_receipt_id
   AND c.mutation_transaction_id=e.mutation_transaction_id AND c.owner_module_id=e.owner_module_id
   AND c.state='committed' AND c.operation=e.action )
 THEN RAISE EXCEPTION 'missing exact atomic owner proof for UserRole'; END IF;
 RETURN NULL;
END;
$wa$;

CREATE CONSTRAINT TRIGGER owner_commit AFTER INSERT OR UPDATE ON "app"."user_roles" DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.commit_userrole();

CREATE FUNCTION platform_private.commit_customerprofile() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE e platform.owner_mutation_evidence; prior_value jsonb;
BEGIN
 prior_value:=CASE WHEN TG_OP='UPDATE' THEN jsonb_build_object('id',to_jsonb(OLD."id"),'userId',to_jsonb(OLD."user_id"),'status',to_jsonb(OLD."status"),'revision',to_jsonb(OLD."revision"::text),'privacyGeneration',to_jsonb(OLD."privacy_generation"::text)) ELSE 'null'::jsonb END;
 SELECT * INTO e FROM platform.owner_mutation_evidence WHERE aggregate_kind='CustomerProfile'
  AND aggregate_id=(to_jsonb(NEW)->>'id') AND committed_revision=NEW.revision
  AND owner_module_id='customer_buyer_profile' AND mutation_transaction_id=pg_current_xact_id()::text;
 IF NOT FOUND OR e.evidence_body->'primaryKey' IS DISTINCT FROM jsonb_build_object('id',NEW."id")
  OR e.evidence_body->'committed' IS DISTINCT FROM jsonb_build_object('id',to_jsonb(NEW."id"),'userId',to_jsonb(NEW."user_id"),'status',to_jsonb(NEW."status"),'revision',to_jsonb(NEW."revision"::text),'privacyGeneration',to_jsonb(NEW."privacy_generation"::text))
  OR COALESCE(e.evidence_body->'prior','null'::jsonb) IS DISTINCT FROM prior_value
  OR e.previous_revision IS DISTINCT FROM (CASE WHEN TG_OP='UPDATE' THEN OLD.revision ELSE NULL::bigint END)
  OR e.decision_ref IS DISTINCT FROM e.evidence_body->>'decisionRef'
  OR NOT platform_private.json_evidence_customerprofile(e.evidence_body)
  OR NOT EXISTS(SELECT 1 FROM platform.runtime_command_receipt c WHERE c.id=e.command_receipt_id
   AND c.mutation_transaction_id=e.mutation_transaction_id AND c.owner_module_id=e.owner_module_id
   AND c.state='committed' AND c.operation=e.action AND c.source_revision=e.committed_revision)
 THEN RAISE EXCEPTION 'missing exact atomic owner proof for CustomerProfile'; END IF;
 RETURN NULL;
END;
$wa$;

CREATE CONSTRAINT TRIGGER owner_commit AFTER INSERT OR UPDATE ON "app"."customer_profiles" DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.commit_customerprofile();

CREATE FUNCTION platform_private.commit_auditevent() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE e platform.owner_mutation_evidence; prior_value jsonb;
BEGIN
 prior_value:=CASE WHEN TG_OP='UPDATE' THEN jsonb_build_object('id',to_jsonb(OLD."id")) ELSE 'null'::jsonb END;
 SELECT * INTO e FROM platform.owner_mutation_evidence WHERE aggregate_kind='AuditEvent'
  AND aggregate_id=(to_jsonb(NEW)->>'id') AND committed_revision=0::bigint
  AND owner_module_id='audit_event_ledger' AND mutation_transaction_id=pg_current_xact_id()::text;
 IF NOT FOUND OR e.evidence_body->'primaryKey' IS DISTINCT FROM jsonb_build_object('id',NEW."id")
  OR e.evidence_body->'committed' IS DISTINCT FROM jsonb_build_object('id',to_jsonb(NEW."id"))
  OR COALESCE(e.evidence_body->'prior','null'::jsonb) IS DISTINCT FROM prior_value
  OR e.previous_revision IS DISTINCT FROM (CASE WHEN TG_OP='UPDATE' THEN 0::bigint ELSE NULL::bigint END)
  OR e.decision_ref IS DISTINCT FROM e.evidence_body->>'decisionRef'
  OR NOT platform_private.json_evidence_auditevent(e.evidence_body)
  OR NOT EXISTS(SELECT 1 FROM platform.runtime_command_receipt c WHERE c.id=e.command_receipt_id
   AND c.mutation_transaction_id=e.mutation_transaction_id AND c.owner_module_id=e.owner_module_id
   AND c.state='committed' AND c.operation=e.action )
 THEN RAISE EXCEPTION 'missing exact atomic owner proof for AuditEvent'; END IF;
 RETURN NULL;
END;
$wa$;

CREATE CONSTRAINT TRIGGER owner_commit AFTER INSERT OR UPDATE ON "app"."audit_events" DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.commit_auditevent();

CREATE FUNCTION platform_private.commit_usersecurityprofile() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE e platform.owner_mutation_evidence; prior_value jsonb;
BEGIN
 prior_value:=CASE WHEN TG_OP='UPDATE' THEN jsonb_build_object('id',to_jsonb(OLD."id"),'userId',to_jsonb(OLD."user_id"),'securityTier',to_jsonb(OLD."security_tier"),'phoneNumberHash',to_jsonb(OLD."phone_number_hash"),'revision',to_jsonb(OLD."revision"::text),'securityGeneration',to_jsonb(OLD."security_generation"::text)) ELSE 'null'::jsonb END;
 SELECT * INTO e FROM platform.owner_mutation_evidence WHERE aggregate_kind='UserSecurityProfile'
  AND aggregate_id=(to_jsonb(NEW)->>'id') AND committed_revision=NEW.revision
  AND owner_module_id='identity_access' AND mutation_transaction_id=pg_current_xact_id()::text;
 IF NOT FOUND OR e.evidence_body->'primaryKey' IS DISTINCT FROM jsonb_build_object('id',NEW."id")
  OR e.evidence_body->'committed' IS DISTINCT FROM jsonb_build_object('id',to_jsonb(NEW."id"),'userId',to_jsonb(NEW."user_id"),'securityTier',to_jsonb(NEW."security_tier"),'phoneNumberHash',to_jsonb(NEW."phone_number_hash"),'revision',to_jsonb(NEW."revision"::text),'securityGeneration',to_jsonb(NEW."security_generation"::text))
  OR COALESCE(e.evidence_body->'prior','null'::jsonb) IS DISTINCT FROM prior_value
  OR e.previous_revision IS DISTINCT FROM (CASE WHEN TG_OP='UPDATE' THEN OLD.revision ELSE NULL::bigint END)
  OR e.decision_ref IS DISTINCT FROM e.evidence_body->>'decisionRef'
  OR NOT platform_private.json_evidence_usersecurityprofile(e.evidence_body)
  OR NOT EXISTS(SELECT 1 FROM platform.runtime_command_receipt c WHERE c.id=e.command_receipt_id
   AND c.mutation_transaction_id=e.mutation_transaction_id AND c.owner_module_id=e.owner_module_id
   AND c.state='committed' AND c.operation=e.action )
 THEN RAISE EXCEPTION 'missing exact atomic owner proof for UserSecurityProfile'; END IF;
 RETURN NULL;
END;
$wa$;

CREATE CONSTRAINT TRIGGER owner_commit AFTER INSERT OR UPDATE ON "app"."user_security_profiles" DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.commit_usersecurityprofile();

CREATE FUNCTION platform_private.commit_authprovideraccount() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE e platform.owner_mutation_evidence; prior_value jsonb;
BEGIN
 prior_value:=CASE WHEN TG_OP='UPDATE' THEN jsonb_build_object('id',to_jsonb(OLD."id"),'userId',to_jsonb(OLD."user_id"),'providerType',to_jsonb(OLD."provider_type"),'status',to_jsonb(OLD."status"),'revision',to_jsonb(OLD."revision"::text)) ELSE 'null'::jsonb END;
 SELECT * INTO e FROM platform.owner_mutation_evidence WHERE aggregate_kind='AuthProviderAccount'
  AND aggregate_id=(to_jsonb(NEW)->>'id') AND committed_revision=NEW.revision
  AND owner_module_id='identity_access' AND mutation_transaction_id=pg_current_xact_id()::text;
 IF NOT FOUND OR e.evidence_body->'primaryKey' IS DISTINCT FROM jsonb_build_object('id',NEW."id")
  OR e.evidence_body->'committed' IS DISTINCT FROM jsonb_build_object('id',to_jsonb(NEW."id"),'userId',to_jsonb(NEW."user_id"),'providerType',to_jsonb(NEW."provider_type"),'status',to_jsonb(NEW."status"),'revision',to_jsonb(NEW."revision"::text))
  OR COALESCE(e.evidence_body->'prior','null'::jsonb) IS DISTINCT FROM prior_value
  OR e.previous_revision IS DISTINCT FROM (CASE WHEN TG_OP='UPDATE' THEN OLD.revision ELSE NULL::bigint END)
  OR e.decision_ref IS DISTINCT FROM e.evidence_body->>'decisionRef'
  OR NOT platform_private.json_evidence_authprovideraccount(e.evidence_body)
  OR NOT EXISTS(SELECT 1 FROM platform.runtime_command_receipt c WHERE c.id=e.command_receipt_id
   AND c.mutation_transaction_id=e.mutation_transaction_id AND c.owner_module_id=e.owner_module_id
   AND c.state='committed' AND c.operation=e.action )
 THEN RAISE EXCEPTION 'missing exact atomic owner proof for AuthProviderAccount'; END IF;
 RETURN NULL;
END;
$wa$;

CREATE CONSTRAINT TRIGGER owner_commit AFTER INSERT OR UPDATE ON "app"."auth_provider_accounts" DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.commit_authprovideraccount();

CREATE FUNCTION platform_private.commit_trackplan() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE e platform.owner_mutation_evidence; prior_value jsonb;
BEGIN
 prior_value:=CASE WHEN TG_OP='UPDATE' THEN jsonb_build_object('id',to_jsonb(OLD."id"),'track',to_jsonb(OLD."track"),'status',to_jsonb(OLD."status"),'billingModel',to_jsonb(OLD."billing_model"),'monthlyPriceCents',to_jsonb(OLD."monthly_price_cents"),'currency',to_jsonb(OLD."currency"),'revision',to_jsonb(OLD."revision"::text),'contentHash',to_jsonb(OLD."content_hash")) ELSE 'null'::jsonb END;
 SELECT * INTO e FROM platform.owner_mutation_evidence WHERE aggregate_kind='TrackPlan'
  AND aggregate_id=(to_jsonb(NEW)->>'id') AND committed_revision=NEW.revision
  AND owner_module_id='track_subscription_entitlement' AND mutation_transaction_id=pg_current_xact_id()::text;
 IF NOT FOUND OR e.evidence_body->'primaryKey' IS DISTINCT FROM jsonb_build_object('id',NEW."id")
  OR e.evidence_body->'committed' IS DISTINCT FROM jsonb_build_object('id',to_jsonb(NEW."id"),'track',to_jsonb(NEW."track"),'status',to_jsonb(NEW."status"),'billingModel',to_jsonb(NEW."billing_model"),'monthlyPriceCents',to_jsonb(NEW."monthly_price_cents"),'currency',to_jsonb(NEW."currency"),'revision',to_jsonb(NEW."revision"::text),'contentHash',to_jsonb(NEW."content_hash"))
  OR COALESCE(e.evidence_body->'prior','null'::jsonb) IS DISTINCT FROM prior_value
  OR e.previous_revision IS DISTINCT FROM (CASE WHEN TG_OP='UPDATE' THEN OLD.revision ELSE NULL::bigint END)
  OR e.decision_ref IS DISTINCT FROM e.evidence_body->>'decisionRef'
  OR NOT platform_private.json_evidence_trackplan(e.evidence_body)
  OR NOT EXISTS(SELECT 1 FROM platform.runtime_command_receipt c WHERE c.id=e.command_receipt_id
   AND c.mutation_transaction_id=e.mutation_transaction_id AND c.owner_module_id=e.owner_module_id
   AND c.state='committed' AND c.operation=e.action )
 THEN RAISE EXCEPTION 'missing exact atomic owner proof for TrackPlan'; END IF;
 RETURN NULL;
END;
$wa$;

CREATE CONSTRAINT TRIGGER owner_commit AFTER INSERT OR UPDATE ON "app"."track_plans" DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.commit_trackplan();

CREATE FUNCTION platform_private.commit_trackentitlementdefinition() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE e platform.owner_mutation_evidence; prior_value jsonb;
BEGIN
 prior_value:=CASE WHEN TG_OP='UPDATE' THEN jsonb_build_object('id',to_jsonb(OLD."id"),'valueType',to_jsonb(OLD."value_type"),'track',to_jsonb(OLD."track"),'revision',to_jsonb(OLD."revision"::text)) ELSE 'null'::jsonb END;
 SELECT * INTO e FROM platform.owner_mutation_evidence WHERE aggregate_kind='TrackEntitlementDefinition'
  AND aggregate_id=(to_jsonb(NEW)->>'id') AND committed_revision=NEW.revision
  AND owner_module_id='track_subscription_entitlement' AND mutation_transaction_id=pg_current_xact_id()::text;
 IF NOT FOUND OR e.evidence_body->'primaryKey' IS DISTINCT FROM jsonb_build_object('id',NEW."id")
  OR e.evidence_body->'committed' IS DISTINCT FROM jsonb_build_object('id',to_jsonb(NEW."id"),'valueType',to_jsonb(NEW."value_type"),'track',to_jsonb(NEW."track"),'revision',to_jsonb(NEW."revision"::text))
  OR COALESCE(e.evidence_body->'prior','null'::jsonb) IS DISTINCT FROM prior_value
  OR e.previous_revision IS DISTINCT FROM (CASE WHEN TG_OP='UPDATE' THEN OLD.revision ELSE NULL::bigint END)
  OR e.decision_ref IS DISTINCT FROM e.evidence_body->>'decisionRef'
  OR NOT platform_private.json_evidence_trackentitlementdefinition(e.evidence_body)
  OR NOT EXISTS(SELECT 1 FROM platform.runtime_command_receipt c WHERE c.id=e.command_receipt_id
   AND c.mutation_transaction_id=e.mutation_transaction_id AND c.owner_module_id=e.owner_module_id
   AND c.state='committed' AND c.operation=e.action )
 THEN RAISE EXCEPTION 'missing exact atomic owner proof for TrackEntitlementDefinition'; END IF;
 RETURN NULL;
END;
$wa$;

CREATE CONSTRAINT TRIGGER owner_commit AFTER INSERT OR UPDATE ON "app"."track_entitlement_definitions" DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.commit_trackentitlementdefinition();

CREATE FUNCTION platform_private.commit_trackplanentitlement() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE e platform.owner_mutation_evidence; prior_value jsonb;
BEGIN
 prior_value:=CASE WHEN TG_OP='UPDATE' THEN jsonb_build_object('id',to_jsonb(OLD."id"),'valueType',to_jsonb(OLD."value_type"),'usagePeriod',to_jsonb(OLD."usage_period"),'revision',to_jsonb(OLD."revision"::text)) ELSE 'null'::jsonb END;
 SELECT * INTO e FROM platform.owner_mutation_evidence WHERE aggregate_kind='TrackPlanEntitlement'
  AND aggregate_id=(to_jsonb(NEW)->>'id') AND committed_revision=NEW.revision
  AND owner_module_id='track_subscription_entitlement' AND mutation_transaction_id=pg_current_xact_id()::text;
 IF NOT FOUND OR e.evidence_body->'primaryKey' IS DISTINCT FROM jsonb_build_object('id',NEW."id")
  OR e.evidence_body->'committed' IS DISTINCT FROM jsonb_build_object('id',to_jsonb(NEW."id"),'valueType',to_jsonb(NEW."value_type"),'usagePeriod',to_jsonb(NEW."usage_period"),'revision',to_jsonb(NEW."revision"::text))
  OR COALESCE(e.evidence_body->'prior','null'::jsonb) IS DISTINCT FROM prior_value
  OR e.previous_revision IS DISTINCT FROM (CASE WHEN TG_OP='UPDATE' THEN OLD.revision ELSE NULL::bigint END)
  OR e.decision_ref IS DISTINCT FROM e.evidence_body->>'decisionRef'
  OR NOT platform_private.json_evidence_trackplanentitlement(e.evidence_body)
  OR NOT EXISTS(SELECT 1 FROM platform.runtime_command_receipt c WHERE c.id=e.command_receipt_id
   AND c.mutation_transaction_id=e.mutation_transaction_id AND c.owner_module_id=e.owner_module_id
   AND c.state='committed' AND c.operation=e.action )
 THEN RAISE EXCEPTION 'missing exact atomic owner proof for TrackPlanEntitlement'; END IF;
 RETURN NULL;
END;
$wa$;

CREATE CONSTRAINT TRIGGER owner_commit AFTER INSERT OR UPDATE ON "app"."track_plan_entitlements" DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.commit_trackplanentitlement();

CREATE FUNCTION platform_private.commit_tracksubscription() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE e platform.owner_mutation_evidence; prior_value jsonb;
BEGIN
 prior_value:=CASE WHEN TG_OP='UPDATE' THEN jsonb_build_object('id',to_jsonb(OLD."id"),'userId',to_jsonb(OLD."user_id"),'track',to_jsonb(OLD."track"),'status',to_jsonb(OLD."status"),'provider',to_jsonb(OLD."provider"),'revision',to_jsonb(OLD."revision"::text)) ELSE 'null'::jsonb END;
 SELECT * INTO e FROM platform.owner_mutation_evidence WHERE aggregate_kind='TrackSubscription'
  AND aggregate_id=(to_jsonb(NEW)->>'id') AND committed_revision=NEW.revision
  AND owner_module_id='track_subscription_entitlement' AND mutation_transaction_id=pg_current_xact_id()::text;
 IF NOT FOUND OR e.evidence_body->'primaryKey' IS DISTINCT FROM jsonb_build_object('id',NEW."id")
  OR e.evidence_body->'committed' IS DISTINCT FROM jsonb_build_object('id',to_jsonb(NEW."id"),'userId',to_jsonb(NEW."user_id"),'track',to_jsonb(NEW."track"),'status',to_jsonb(NEW."status"),'provider',to_jsonb(NEW."provider"),'revision',to_jsonb(NEW."revision"::text))
  OR COALESCE(e.evidence_body->'prior','null'::jsonb) IS DISTINCT FROM prior_value
  OR e.previous_revision IS DISTINCT FROM (CASE WHEN TG_OP='UPDATE' THEN OLD.revision ELSE NULL::bigint END)
  OR e.decision_ref IS DISTINCT FROM e.evidence_body->>'decisionRef'
  OR NOT platform_private.json_evidence_tracksubscription(e.evidence_body)
  OR NOT EXISTS(SELECT 1 FROM platform.runtime_command_receipt c WHERE c.id=e.command_receipt_id
   AND c.mutation_transaction_id=e.mutation_transaction_id AND c.owner_module_id=e.owner_module_id
   AND c.state='committed' AND c.operation=e.action )
 THEN RAISE EXCEPTION 'missing exact atomic owner proof for TrackSubscription'; END IF;
 RETURN NULL;
END;
$wa$;

CREATE CONSTRAINT TRIGGER owner_commit AFTER INSERT OR UPDATE ON "app"."track_subscriptions" DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.commit_tracksubscription();

CREATE FUNCTION platform_private.commit_trackentitlementgrant() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE e platform.owner_mutation_evidence; prior_value jsonb;
BEGIN
 prior_value:=CASE WHEN TG_OP='UPDATE' THEN jsonb_build_object('id',to_jsonb(OLD."id"),'userId',to_jsonb(OLD."user_id"),'track',to_jsonb(OLD."track"),'status',to_jsonb(OLD."status"),'valueType',to_jsonb(OLD."value_type"),'revision',to_jsonb(OLD."revision"::text)) ELSE 'null'::jsonb END;
 SELECT * INTO e FROM platform.owner_mutation_evidence WHERE aggregate_kind='TrackEntitlementGrant'
  AND aggregate_id=(to_jsonb(NEW)->>'id') AND committed_revision=NEW.revision
  AND owner_module_id='track_subscription_entitlement' AND mutation_transaction_id=pg_current_xact_id()::text;
 IF NOT FOUND OR e.evidence_body->'primaryKey' IS DISTINCT FROM jsonb_build_object('id',NEW."id")
  OR e.evidence_body->'committed' IS DISTINCT FROM jsonb_build_object('id',to_jsonb(NEW."id"),'userId',to_jsonb(NEW."user_id"),'track',to_jsonb(NEW."track"),'status',to_jsonb(NEW."status"),'valueType',to_jsonb(NEW."value_type"),'revision',to_jsonb(NEW."revision"::text))
  OR COALESCE(e.evidence_body->'prior','null'::jsonb) IS DISTINCT FROM prior_value
  OR e.previous_revision IS DISTINCT FROM (CASE WHEN TG_OP='UPDATE' THEN OLD.revision ELSE NULL::bigint END)
  OR e.decision_ref IS DISTINCT FROM e.evidence_body->>'decisionRef'
  OR NOT platform_private.json_evidence_trackentitlementgrant(e.evidence_body)
  OR NOT EXISTS(SELECT 1 FROM platform.runtime_command_receipt c WHERE c.id=e.command_receipt_id
   AND c.mutation_transaction_id=e.mutation_transaction_id AND c.owner_module_id=e.owner_module_id
   AND c.state='committed' AND c.operation=e.action )
 THEN RAISE EXCEPTION 'missing exact atomic owner proof for TrackEntitlementGrant'; END IF;
 RETURN NULL;
END;
$wa$;

CREATE CONSTRAINT TRIGGER owner_commit AFTER INSERT OR UPDATE ON "app"."track_entitlement_grants" DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.commit_trackentitlementgrant();

CREATE FUNCTION platform_private.commit_trackusageevent() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE e platform.owner_mutation_evidence; prior_value jsonb;
BEGIN
 prior_value:=CASE WHEN TG_OP='UPDATE' THEN jsonb_build_object('id',to_jsonb(OLD."id"),'userId',to_jsonb(OLD."user_id"),'track',to_jsonb(OLD."track"),'type',to_jsonb(OLD."type"),'semanticEffectKey',to_jsonb(OLD."semantic_effect_key"),'sourceRevision',to_jsonb(OLD."source_revision"::text),'sourceOwner',to_jsonb(OLD."source_owner"),'sourceId',to_jsonb(OLD."source_id"),'acceptedAt',to_jsonb(OLD."accepted_at"),'periodStart',to_jsonb(OLD."period_start"),'periodEnd',to_jsonb(OLD."period_end")) ELSE 'null'::jsonb END;
 SELECT * INTO e FROM platform.owner_mutation_evidence WHERE aggregate_kind='TrackUsageEvent'
  AND aggregate_id=(to_jsonb(NEW)->>'id') AND committed_revision=0::bigint
  AND owner_module_id='track_subscription_entitlement' AND mutation_transaction_id=pg_current_xact_id()::text;
 IF NOT FOUND OR e.evidence_body->'primaryKey' IS DISTINCT FROM jsonb_build_object('id',NEW."id")
  OR e.evidence_body->'committed' IS DISTINCT FROM jsonb_build_object('id',to_jsonb(NEW."id"),'userId',to_jsonb(NEW."user_id"),'track',to_jsonb(NEW."track"),'type',to_jsonb(NEW."type"),'semanticEffectKey',to_jsonb(NEW."semantic_effect_key"),'sourceRevision',to_jsonb(NEW."source_revision"::text),'sourceOwner',to_jsonb(NEW."source_owner"),'sourceId',to_jsonb(NEW."source_id"),'acceptedAt',to_jsonb(NEW."accepted_at"),'periodStart',to_jsonb(NEW."period_start"),'periodEnd',to_jsonb(NEW."period_end"))
  OR COALESCE(e.evidence_body->'prior','null'::jsonb) IS DISTINCT FROM prior_value
  OR e.previous_revision IS DISTINCT FROM (CASE WHEN TG_OP='UPDATE' THEN 0::bigint ELSE NULL::bigint END)
  OR e.decision_ref IS DISTINCT FROM e.evidence_body->>'decisionRef'
  OR NOT platform_private.json_evidence_trackusageevent(e.evidence_body)
  OR NOT EXISTS(SELECT 1 FROM platform.runtime_command_receipt c WHERE c.id=e.command_receipt_id
   AND c.mutation_transaction_id=e.mutation_transaction_id AND c.owner_module_id=e.owner_module_id
   AND c.state='committed' AND c.operation=e.action )
 THEN RAISE EXCEPTION 'missing exact atomic owner proof for TrackUsageEvent'; END IF;
 RETURN NULL;
END;
$wa$;

CREATE CONSTRAINT TRIGGER owner_commit AFTER INSERT OR UPDATE ON "app"."track_usage_events" DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.commit_trackusageevent();

CREATE FUNCTION platform_private.commit_trackusagecounter() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE e platform.owner_mutation_evidence; prior_value jsonb;
BEGIN
 prior_value:=CASE WHEN TG_OP='UPDATE' THEN jsonb_build_object('id',to_jsonb(OLD."id"),'userId',to_jsonb(OLD."user_id"),'track',to_jsonb(OLD."track"),'period',to_jsonb(OLD."period"),'periodStart',to_jsonb(OLD."period_start"),'periodEnd',to_jsonb(OLD."period_end"),'usedQuantity',to_jsonb(OLD."used_quantity"),'limitQuantity',to_jsonb(OLD."limit_quantity"),'revision',to_jsonb(OLD."revision"::text),'sourceRevision',to_jsonb(OLD."source_revision"::text)) ELSE 'null'::jsonb END;
 SELECT * INTO e FROM platform.owner_mutation_evidence WHERE aggregate_kind='TrackUsageCounter'
  AND aggregate_id=(to_jsonb(NEW)->>'id') AND committed_revision=NEW.revision
  AND owner_module_id='track_subscription_entitlement' AND mutation_transaction_id=pg_current_xact_id()::text;
 IF NOT FOUND OR e.evidence_body->'primaryKey' IS DISTINCT FROM jsonb_build_object('id',NEW."id")
  OR e.evidence_body->'committed' IS DISTINCT FROM jsonb_build_object('id',to_jsonb(NEW."id"),'userId',to_jsonb(NEW."user_id"),'track',to_jsonb(NEW."track"),'period',to_jsonb(NEW."period"),'periodStart',to_jsonb(NEW."period_start"),'periodEnd',to_jsonb(NEW."period_end"),'usedQuantity',to_jsonb(NEW."used_quantity"),'limitQuantity',to_jsonb(NEW."limit_quantity"),'revision',to_jsonb(NEW."revision"::text),'sourceRevision',to_jsonb(NEW."source_revision"::text))
  OR COALESCE(e.evidence_body->'prior','null'::jsonb) IS DISTINCT FROM prior_value
  OR e.previous_revision IS DISTINCT FROM (CASE WHEN TG_OP='UPDATE' THEN OLD.revision ELSE NULL::bigint END)
  OR e.decision_ref IS DISTINCT FROM e.evidence_body->>'decisionRef'
  OR NOT platform_private.json_evidence_trackusagecounter(e.evidence_body)
  OR NOT EXISTS(SELECT 1 FROM platform.runtime_command_receipt c WHERE c.id=e.command_receipt_id
   AND c.mutation_transaction_id=e.mutation_transaction_id AND c.owner_module_id=e.owner_module_id
   AND c.state='committed' AND c.operation=e.action )
 THEN RAISE EXCEPTION 'missing exact atomic owner proof for TrackUsageCounter'; END IF;
 RETURN NULL;
END;
$wa$;

CREATE CONSTRAINT TRIGGER owner_commit AFTER INSERT OR UPDATE ON "app"."track_usage_counters" DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.commit_trackusagecounter();

CREATE FUNCTION platform_private.commit_consentcontentrevision() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE e platform.owner_mutation_evidence; prior_value jsonb;
BEGIN
 prior_value:=CASE WHEN TG_OP='UPDATE' THEN jsonb_build_object('id',to_jsonb(OLD."id"),'type',to_jsonb(OLD."type"),'contentHash',to_jsonb(OLD."content_hash"),'reviewState',to_jsonb(OLD."review_state")) ELSE 'null'::jsonb END;
 SELECT * INTO e FROM platform.owner_mutation_evidence WHERE aggregate_kind='ConsentContentRevision'
  AND aggregate_id=(to_jsonb(NEW)->>'id') AND committed_revision=0::bigint
  AND owner_module_id='consent_disclosure' AND mutation_transaction_id=pg_current_xact_id()::text;
 IF NOT FOUND OR e.evidence_body->'primaryKey' IS DISTINCT FROM jsonb_build_object('id',NEW."id")
  OR e.evidence_body->'committed' IS DISTINCT FROM jsonb_build_object('id',to_jsonb(NEW."id"),'type',to_jsonb(NEW."type"),'contentHash',to_jsonb(NEW."content_hash"),'reviewState',to_jsonb(NEW."review_state"))
  OR COALESCE(e.evidence_body->'prior','null'::jsonb) IS DISTINCT FROM prior_value
  OR e.previous_revision IS DISTINCT FROM (CASE WHEN TG_OP='UPDATE' THEN 0::bigint ELSE NULL::bigint END)
  OR e.decision_ref IS DISTINCT FROM e.evidence_body->>'decisionRef'
  OR NOT platform_private.json_evidence_consentcontentrevision(e.evidence_body)
  OR NOT EXISTS(SELECT 1 FROM platform.runtime_command_receipt c WHERE c.id=e.command_receipt_id
   AND c.mutation_transaction_id=e.mutation_transaction_id AND c.owner_module_id=e.owner_module_id
   AND c.state='committed' AND c.operation=e.action )
 THEN RAISE EXCEPTION 'missing exact atomic owner proof for ConsentContentRevision'; END IF;
 RETURN NULL;
END;
$wa$;

CREATE CONSTRAINT TRIGGER owner_commit AFTER INSERT OR UPDATE ON "app"."consent_content_revision" DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.commit_consentcontentrevision();

CREATE FUNCTION platform_private.commit_consentpresentation() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE e platform.owner_mutation_evidence; prior_value jsonb;
BEGIN
 prior_value:=CASE WHEN TG_OP='UPDATE' THEN jsonb_build_object('id',to_jsonb(OLD."id"),'userId',to_jsonb(OLD."user_id"),'renderedHash',to_jsonb(OLD."rendered_hash")) ELSE 'null'::jsonb END;
 SELECT * INTO e FROM platform.owner_mutation_evidence WHERE aggregate_kind='ConsentPresentation'
  AND aggregate_id=(to_jsonb(NEW)->>'id') AND committed_revision=0::bigint
  AND owner_module_id='consent_disclosure' AND mutation_transaction_id=pg_current_xact_id()::text;
 IF NOT FOUND OR e.evidence_body->'primaryKey' IS DISTINCT FROM jsonb_build_object('id',NEW."id")
  OR e.evidence_body->'committed' IS DISTINCT FROM jsonb_build_object('id',to_jsonb(NEW."id"),'userId',to_jsonb(NEW."user_id"),'renderedHash',to_jsonb(NEW."rendered_hash"))
  OR COALESCE(e.evidence_body->'prior','null'::jsonb) IS DISTINCT FROM prior_value
  OR e.previous_revision IS DISTINCT FROM (CASE WHEN TG_OP='UPDATE' THEN 0::bigint ELSE NULL::bigint END)
  OR e.decision_ref IS DISTINCT FROM e.evidence_body->>'decisionRef'
  OR NOT platform_private.json_evidence_consentpresentation(e.evidence_body)
  OR NOT EXISTS(SELECT 1 FROM platform.runtime_command_receipt c WHERE c.id=e.command_receipt_id
   AND c.mutation_transaction_id=e.mutation_transaction_id AND c.owner_module_id=e.owner_module_id
   AND c.state='committed' AND c.operation=e.action )
 THEN RAISE EXCEPTION 'missing exact atomic owner proof for ConsentPresentation'; END IF;
 RETURN NULL;
END;
$wa$;

CREATE CONSTRAINT TRIGGER owner_commit AFTER INSERT OR UPDATE ON "app"."consent_presentation" DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.commit_consentpresentation();

CREATE FUNCTION platform_private.commit_consentdisposition() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE e platform.owner_mutation_evidence; prior_value jsonb;
BEGIN
 prior_value:=CASE WHEN TG_OP='UPDATE' THEN jsonb_build_object('id',to_jsonb(OLD."id"),'userId',to_jsonb(OLD."user_id"),'kind',to_jsonb(OLD."kind")) ELSE 'null'::jsonb END;
 SELECT * INTO e FROM platform.owner_mutation_evidence WHERE aggregate_kind='ConsentDisposition'
  AND aggregate_id=(to_jsonb(NEW)->>'id') AND committed_revision=0::bigint
  AND owner_module_id='consent_disclosure' AND mutation_transaction_id=pg_current_xact_id()::text;
 IF NOT FOUND OR e.evidence_body->'primaryKey' IS DISTINCT FROM jsonb_build_object('id',NEW."id")
  OR e.evidence_body->'committed' IS DISTINCT FROM jsonb_build_object('id',to_jsonb(NEW."id"),'userId',to_jsonb(NEW."user_id"),'kind',to_jsonb(NEW."kind"))
  OR COALESCE(e.evidence_body->'prior','null'::jsonb) IS DISTINCT FROM prior_value
  OR e.previous_revision IS DISTINCT FROM (CASE WHEN TG_OP='UPDATE' THEN 0::bigint ELSE NULL::bigint END)
  OR e.decision_ref IS DISTINCT FROM e.evidence_body->>'decisionRef'
  OR NOT platform_private.json_evidence_consentdisposition(e.evidence_body)
  OR NOT EXISTS(SELECT 1 FROM platform.runtime_command_receipt c WHERE c.id=e.command_receipt_id
   AND c.mutation_transaction_id=e.mutation_transaction_id AND c.owner_module_id=e.owner_module_id
   AND c.state='committed' AND c.operation=e.action )
 THEN RAISE EXCEPTION 'missing exact atomic owner proof for ConsentDisposition'; END IF;
 RETURN NULL;
END;
$wa$;

CREATE CONSTRAINT TRIGGER owner_commit AFTER INSERT OR UPDATE ON "app"."consent_disposition" DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.commit_consentdisposition();

CREATE FUNCTION platform_private.commit_trackbaseselection() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE e platform.owner_mutation_evidence; prior_value jsonb;
BEGIN
 prior_value:=CASE WHEN TG_OP='UPDATE' THEN jsonb_build_object('id',to_jsonb(OLD."id"),'userId',to_jsonb(OLD."user_id"),'track',to_jsonb(OLD."track"),'revision',to_jsonb(OLD."revision"::text),'sourceGeneration',to_jsonb(OLD."source_generation"::text)) ELSE 'null'::jsonb END;
 SELECT * INTO e FROM platform.owner_mutation_evidence WHERE aggregate_kind='TrackBaseSelection'
  AND aggregate_id=(to_jsonb(NEW)->>'id') AND committed_revision=NEW.revision
  AND owner_module_id='track_subscription_entitlement' AND mutation_transaction_id=pg_current_xact_id()::text;
 IF NOT FOUND OR e.evidence_body->'primaryKey' IS DISTINCT FROM jsonb_build_object('id',NEW."id")
  OR e.evidence_body->'committed' IS DISTINCT FROM jsonb_build_object('id',to_jsonb(NEW."id"),'userId',to_jsonb(NEW."user_id"),'track',to_jsonb(NEW."track"),'revision',to_jsonb(NEW."revision"::text),'sourceGeneration',to_jsonb(NEW."source_generation"::text))
  OR COALESCE(e.evidence_body->'prior','null'::jsonb) IS DISTINCT FROM prior_value
  OR e.previous_revision IS DISTINCT FROM (CASE WHEN TG_OP='UPDATE' THEN OLD.revision ELSE NULL::bigint END)
  OR e.decision_ref IS DISTINCT FROM e.evidence_body->>'decisionRef'
  OR NOT platform_private.json_evidence_trackbaseselection(e.evidence_body)
  OR NOT EXISTS(SELECT 1 FROM platform.runtime_command_receipt c WHERE c.id=e.command_receipt_id
   AND c.mutation_transaction_id=e.mutation_transaction_id AND c.owner_module_id=e.owner_module_id
   AND c.state='committed' AND c.operation=e.action )
 THEN RAISE EXCEPTION 'missing exact atomic owner proof for TrackBaseSelection'; END IF;
 RETURN NULL;
END;
$wa$;

CREATE CONSTRAINT TRIGGER owner_commit AFTER INSERT OR UPDATE ON "app"."track_base_selection" DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.commit_trackbaseselection();

CREATE FUNCTION platform_private.commit_trackusagereservation() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE e platform.owner_mutation_evidence; prior_value jsonb;
BEGIN
 prior_value:=CASE WHEN TG_OP='UPDATE' THEN jsonb_build_object('id',to_jsonb(OLD."id"),'userId',to_jsonb(OLD."user_id"),'periodStart',to_jsonb(OLD."period_start"),'periodEnd',to_jsonb(OLD."period_end"),'acceptedAt',to_jsonb(OLD."accepted_at"),'revision',to_jsonb(OLD."revision"::text)) ELSE 'null'::jsonb END;
 SELECT * INTO e FROM platform.owner_mutation_evidence WHERE aggregate_kind='TrackUsageReservation'
  AND aggregate_id=(to_jsonb(NEW)->>'id') AND committed_revision=NEW.revision
  AND owner_module_id='track_subscription_entitlement' AND mutation_transaction_id=pg_current_xact_id()::text;
 IF NOT FOUND OR e.evidence_body->'primaryKey' IS DISTINCT FROM jsonb_build_object('id',NEW."id")
  OR e.evidence_body->'committed' IS DISTINCT FROM jsonb_build_object('id',to_jsonb(NEW."id"),'userId',to_jsonb(NEW."user_id"),'periodStart',to_jsonb(NEW."period_start"),'periodEnd',to_jsonb(NEW."period_end"),'acceptedAt',to_jsonb(NEW."accepted_at"),'revision',to_jsonb(NEW."revision"::text))
  OR COALESCE(e.evidence_body->'prior','null'::jsonb) IS DISTINCT FROM prior_value
  OR e.previous_revision IS DISTINCT FROM (CASE WHEN TG_OP='UPDATE' THEN OLD.revision ELSE NULL::bigint END)
  OR e.decision_ref IS DISTINCT FROM e.evidence_body->>'decisionRef'
  OR NOT platform_private.json_evidence_trackusagereservation(e.evidence_body)
  OR NOT EXISTS(SELECT 1 FROM platform.runtime_command_receipt c WHERE c.id=e.command_receipt_id
   AND c.mutation_transaction_id=e.mutation_transaction_id AND c.owner_module_id=e.owner_module_id
   AND c.state='committed' AND c.operation=e.action )
 THEN RAISE EXCEPTION 'missing exact atomic owner proof for TrackUsageReservation'; END IF;
 RETURN NULL;
END;
$wa$;

CREATE CONSTRAINT TRIGGER owner_commit AFTER INSERT OR UPDATE ON "app"."track_usage_reservation" DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.commit_trackusagereservation();

CREATE FUNCTION platform_private.commit_privacytargetinstruction() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE e platform.owner_mutation_evidence; prior_value jsonb;
BEGIN
 prior_value:=CASE WHEN TG_OP='UPDATE' THEN jsonb_build_object('id',to_jsonb(OLD."id"),'sourceId',to_jsonb(OLD."source_id"),'sourceRevision',to_jsonb(OLD."source_revision"),'action',to_jsonb(OLD."action"),'generation',to_jsonb(OLD."generation"::text),'descriptorHash',to_jsonb(OLD."descriptor_hash")) ELSE 'null'::jsonb END;
 SELECT * INTO e FROM platform.owner_mutation_evidence WHERE aggregate_kind='PrivacyTargetInstruction'
  AND aggregate_id=(to_jsonb(NEW)->>'id') AND committed_revision=0::bigint
  AND owner_module_id='privacy_data_erasure' AND mutation_transaction_id=pg_current_xact_id()::text;
 IF NOT FOUND OR e.evidence_body->'primaryKey' IS DISTINCT FROM jsonb_build_object('id',NEW."id")
  OR e.evidence_body->'committed' IS DISTINCT FROM jsonb_build_object('id',to_jsonb(NEW."id"),'sourceId',to_jsonb(NEW."source_id"),'sourceRevision',to_jsonb(NEW."source_revision"),'action',to_jsonb(NEW."action"),'generation',to_jsonb(NEW."generation"::text),'descriptorHash',to_jsonb(NEW."descriptor_hash"))
  OR COALESCE(e.evidence_body->'prior','null'::jsonb) IS DISTINCT FROM prior_value
  OR e.previous_revision IS DISTINCT FROM (CASE WHEN TG_OP='UPDATE' THEN 0::bigint ELSE NULL::bigint END)
  OR e.decision_ref IS DISTINCT FROM e.evidence_body->>'decisionRef'
  OR NOT platform_private.json_evidence_privacytargetinstruction(e.evidence_body)
  OR NOT EXISTS(SELECT 1 FROM platform.runtime_command_receipt c WHERE c.id=e.command_receipt_id
   AND c.mutation_transaction_id=e.mutation_transaction_id AND c.owner_module_id=e.owner_module_id
   AND c.state='committed' AND c.operation=e.action )
 THEN RAISE EXCEPTION 'missing exact atomic owner proof for PrivacyTargetInstruction'; END IF;
 RETURN NULL;
END;
$wa$;

CREATE CONSTRAINT TRIGGER owner_commit AFTER INSERT OR UPDATE ON "app"."privacy_target_instruction" DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.commit_privacytargetinstruction();

CREATE FUNCTION platform_private.commit_privacyownerreceipt() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE e platform.owner_mutation_evidence; prior_value jsonb;
BEGIN
 prior_value:=CASE WHEN TG_OP='UPDATE' THEN jsonb_build_object('id',to_jsonb(OLD."id"),'generation',to_jsonb(OLD."generation"::text),'disposition',to_jsonb(OLD."disposition"),'artifactDigest',to_jsonb(OLD."artifact_digest")) ELSE 'null'::jsonb END;
 SELECT * INTO e FROM platform.owner_mutation_evidence WHERE aggregate_kind='PrivacyOwnerReceipt'
  AND aggregate_id=(to_jsonb(NEW)->>'id') AND committed_revision=0::bigint
  AND owner_module_id='privacy_data_erasure' AND mutation_transaction_id=pg_current_xact_id()::text;
 IF NOT FOUND OR e.evidence_body->'primaryKey' IS DISTINCT FROM jsonb_build_object('id',NEW."id")
  OR e.evidence_body->'committed' IS DISTINCT FROM jsonb_build_object('id',to_jsonb(NEW."id"),'generation',to_jsonb(NEW."generation"::text),'disposition',to_jsonb(NEW."disposition"),'artifactDigest',to_jsonb(NEW."artifact_digest"))
  OR COALESCE(e.evidence_body->'prior','null'::jsonb) IS DISTINCT FROM prior_value
  OR e.previous_revision IS DISTINCT FROM (CASE WHEN TG_OP='UPDATE' THEN 0::bigint ELSE NULL::bigint END)
  OR e.decision_ref IS DISTINCT FROM e.evidence_body->>'decisionRef'
  OR NOT platform_private.json_evidence_privacyownerreceipt(e.evidence_body)
  OR NOT EXISTS(SELECT 1 FROM platform.runtime_command_receipt c WHERE c.id=e.command_receipt_id
   AND c.mutation_transaction_id=e.mutation_transaction_id AND c.owner_module_id=e.owner_module_id
   AND c.state='committed' AND c.operation=e.action )
 THEN RAISE EXCEPTION 'missing exact atomic owner proof for PrivacyOwnerReceipt'; END IF;
 RETURN NULL;
END;
$wa$;

CREATE CONSTRAINT TRIGGER owner_commit AFTER INSERT OR UPDATE ON "app"."privacy_owner_receipt" DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.commit_privacyownerreceipt();

CREATE FUNCTION platform_private.commit_privacyrestoremarker() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE e platform.owner_mutation_evidence; prior_value jsonb;
BEGIN
 prior_value:=CASE WHEN TG_OP='UPDATE' THEN jsonb_build_object('id',to_jsonb(OLD."id"),'sourceId',to_jsonb(OLD."source_id"),'generation',to_jsonb(OLD."generation"::text),'action',to_jsonb(OLD."action"),'revision',to_jsonb(OLD."revision"::text)) ELSE 'null'::jsonb END;
 SELECT * INTO e FROM platform.owner_mutation_evidence WHERE aggregate_kind='PrivacyRestoreMarker'
  AND aggregate_id=(to_jsonb(NEW)->>'id') AND committed_revision=NEW.revision
  AND owner_module_id='privacy_data_erasure' AND mutation_transaction_id=pg_current_xact_id()::text;
 IF NOT FOUND OR e.evidence_body->'primaryKey' IS DISTINCT FROM jsonb_build_object('id',NEW."id")
  OR e.evidence_body->'committed' IS DISTINCT FROM jsonb_build_object('id',to_jsonb(NEW."id"),'sourceId',to_jsonb(NEW."source_id"),'generation',to_jsonb(NEW."generation"::text),'action',to_jsonb(NEW."action"),'revision',to_jsonb(NEW."revision"::text))
  OR COALESCE(e.evidence_body->'prior','null'::jsonb) IS DISTINCT FROM prior_value
  OR e.previous_revision IS DISTINCT FROM (CASE WHEN TG_OP='UPDATE' THEN OLD.revision ELSE NULL::bigint END)
  OR e.decision_ref IS DISTINCT FROM e.evidence_body->>'decisionRef'
  OR NOT platform_private.json_evidence_privacyrestoremarker(e.evidence_body)
  OR NOT EXISTS(SELECT 1 FROM platform.runtime_command_receipt c WHERE c.id=e.command_receipt_id
   AND c.mutation_transaction_id=e.mutation_transaction_id AND c.owner_module_id=e.owner_module_id
   AND c.state='committed' AND c.operation=e.action )
 THEN RAISE EXCEPTION 'missing exact atomic owner proof for PrivacyRestoreMarker'; END IF;
 RETURN NULL;
END;
$wa$;

CREATE CONSTRAINT TRIGGER owner_commit AFTER INSERT OR UPDATE ON "app"."privacy_restore_marker" DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.commit_privacyrestoremarker();

CREATE FUNCTION platform_private.worker_evidence_source_matches(model_name text, aggregate_id text, committed_revision bigint, source_transaction text, committed_value jsonb) RETURNS boolean
LANGUAGE plpgsql VOLATILE SECURITY DEFINER
SET search_path = pg_catalog
AS $wa$
DECLARE g platform.database_action_grant;
BEGIN
 g:=platform_private.bound_grant(true);
 IF g.id IS NULL OR session_user::text<>'wa_worker' OR g.service_principal IS NULL
  OR source_transaction IS DISTINCT FROM pg_current_xact_id()::text
  OR NOT platform_private.worker_lease_valid(g.target_id::uuid,NULL,true)
 THEN RETURN false; END IF;
 CASE model_name
WHEN 'TrackSubscription' THEN
  RETURN EXISTS(SELECT 1 FROM "app"."track_subscriptions" s WHERE s."id"::text=aggregate_id
   AND s.mutation_transaction_id=source_transaction AND s.revision=committed_revision
   AND jsonb_build_object('id',to_jsonb(s."id"),'userId',to_jsonb(s."user_id"),'track',to_jsonb(s."track"),'status',to_jsonb(s."status"),'provider',to_jsonb(s."provider"),'revision',to_jsonb(s."revision"::text))=committed_value
   AND platform_private.worker_track_allowed('TrackSubscription',jsonb_build_object('id',s."id",'user_id',s."user_id",'track',s."track",'customer_profile_id',s."customer_profile_id",'candidate_profile_id',s."candidate_profile_id",'professional_profile_id',s."professional_profile_id"),'SELECT'));
WHEN 'TrackEntitlementGrant' THEN
  RETURN EXISTS(SELECT 1 FROM "app"."track_entitlement_grants" s WHERE s."id"::text=aggregate_id
   AND s.mutation_transaction_id=source_transaction AND s.revision=committed_revision
   AND jsonb_build_object('id',to_jsonb(s."id"),'userId',to_jsonb(s."user_id"),'track',to_jsonb(s."track"),'status',to_jsonb(s."status"),'valueType',to_jsonb(s."value_type"),'revision',to_jsonb(s."revision"::text))=committed_value
   AND platform_private.worker_track_allowed('TrackEntitlementGrant',jsonb_build_object('id',s."id",'user_id',s."user_id",'track',s."track",'customer_profile_id',s."customer_profile_id",'candidate_profile_id',s."candidate_profile_id",'professional_profile_id',s."professional_profile_id"),'SELECT'));
WHEN 'TrackBaseSelection' THEN
  RETURN EXISTS(SELECT 1 FROM "app"."track_base_selection" s WHERE s."id"::text=aggregate_id
   AND s.mutation_transaction_id=source_transaction AND s.revision=committed_revision
   AND jsonb_build_object('id',to_jsonb(s."id"),'userId',to_jsonb(s."user_id"),'track',to_jsonb(s."track"),'revision',to_jsonb(s."revision"::text),'sourceGeneration',to_jsonb(s."source_generation"::text))=committed_value
   AND platform_private.worker_track_allowed('TrackBaseSelection',jsonb_build_object('id',s."id",'user_id',s."user_id",'track',s."track",'customer_profile_id',s."customer_profile_id",'candidate_profile_id',s."candidate_profile_id",'professional_profile_id',s."professional_profile_id"),'SELECT'));
 ELSE RETURN false;
 END CASE;
END;
$wa$;

CREATE FUNCTION platform_private.evidence_source_commit() RETURNS trigger
LANGUAGE plpgsql VOLATILE SECURITY INVOKER
SET search_path = pg_catalog
AS $wa$
DECLARE matches boolean:=false;
BEGIN
 CASE NEW.aggregate_kind
WHEN 'ConsentLog' THEN
  SELECT EXISTS(SELECT 1 FROM "app"."consent_logs" s WHERE (to_jsonb(s)->>'id')=NEW.aggregate_id
   AND s.mutation_transaction_id=NEW.mutation_transaction_id
   AND jsonb_build_object('id',to_jsonb(s."id"),'userId',to_jsonb(s."user_id"),'type',to_jsonb(s."type"),'acceptedAt',to_jsonb(s."accepted_at"),'ipHash',to_jsonb(s."ip_hash"),'presentationHash',to_jsonb(s."presentation_hash"))=NEW.evidence_body->'committed'
   AND 0::bigint=NEW.committed_revision) INTO matches;
WHEN 'PrivacyRequest' THEN
  SELECT EXISTS(SELECT 1 FROM "app"."privacy_requests" s WHERE (to_jsonb(s)->>'id')=NEW.aggregate_id
   AND s.mutation_transaction_id=NEW.mutation_transaction_id
   AND jsonb_build_object('id',to_jsonb(s."id"),'userId',to_jsonb(s."user_id"),'type',to_jsonb(s."type"),'status',to_jsonb(s."status"),'revision',to_jsonb(s."revision"::text),'privacyGeneration',to_jsonb(s."privacy_generation"::text),'instructionGeneration',to_jsonb(s."instruction_generation"::text))=NEW.evidence_body->'committed'
   AND s.revision=NEW.committed_revision) INTO matches;
WHEN 'AgeGateAttempt' THEN
  SELECT EXISTS(SELECT 1 FROM "app"."age_gate_attempts" s WHERE (to_jsonb(s)->>'id')=NEW.aggregate_id
   AND s.mutation_transaction_id=NEW.mutation_transaction_id
   AND jsonb_build_object('id',to_jsonb(s."id"),'userId',to_jsonb(s."user_id"),'ipHash',to_jsonb(s."ip_hash"),'deviceHash',to_jsonb(s."device_hash"),'result',to_jsonb(s."result"))=NEW.evidence_body->'committed'
   AND 0::bigint=NEW.committed_revision) INTO matches;
WHEN 'AgeGateBlock' THEN
  SELECT EXISTS(SELECT 1 FROM "app"."age_gate_blocks" s WHERE (to_jsonb(s)->>'id')=NEW.aggregate_id
   AND s.mutation_transaction_id=NEW.mutation_transaction_id
   AND jsonb_build_object('id',to_jsonb(s."id"),'ipHash',to_jsonb(s."ip_hash"),'deviceHash',to_jsonb(s."device_hash"))=NEW.evidence_body->'committed'
   AND 0::bigint=NEW.committed_revision) INTO matches;
WHEN 'AccessAuditLog' THEN
  SELECT EXISTS(SELECT 1 FROM "app"."access_audit_logs" s WHERE (to_jsonb(s)->>'id')=NEW.aggregate_id
   AND s.mutation_transaction_id=NEW.mutation_transaction_id
   AND jsonb_build_object('id',to_jsonb(s."id"),'action',to_jsonb(s."action"),'sensitivity',to_jsonb(s."sensitivity"),'accessDecision',to_jsonb(s."access_decision"),'ipHash',to_jsonb(s."ip_hash"),'previousHash',to_jsonb(s."previous_hash"),'entryHash',to_jsonb(s."entry_hash"))=NEW.evidence_body->'committed'
   AND 0::bigint=NEW.committed_revision) INTO matches;
WHEN 'User' THEN
  SELECT EXISTS(SELECT 1 FROM "app"."users" s WHERE (to_jsonb(s)->>'id')=NEW.aggregate_id
   AND s.mutation_transaction_id=NEW.mutation_transaction_id
   AND jsonb_build_object('id',to_jsonb(s."id"),'revision',to_jsonb(s."revision"::text),'privacyGeneration',to_jsonb(s."privacy_generation"::text))=NEW.evidence_body->'committed'
   AND s.revision=NEW.committed_revision) INTO matches;
WHEN 'UserRole' THEN
  SELECT EXISTS(SELECT 1 FROM "app"."user_roles" s WHERE (to_jsonb(s)->>'user_id') || ':' || (to_jsonb(s)->>'role')=NEW.aggregate_id
   AND s.mutation_transaction_id=NEW.mutation_transaction_id
   AND jsonb_build_object('userId',to_jsonb(s."user_id"),'role',to_jsonb(s."role"),'revision',to_jsonb(s."revision"::text))=NEW.evidence_body->'committed'
   AND s.revision=NEW.committed_revision) INTO matches;
WHEN 'CustomerProfile' THEN
  SELECT EXISTS(SELECT 1 FROM "app"."customer_profiles" s WHERE (to_jsonb(s)->>'id')=NEW.aggregate_id
   AND s.mutation_transaction_id=NEW.mutation_transaction_id
   AND jsonb_build_object('id',to_jsonb(s."id"),'userId',to_jsonb(s."user_id"),'status',to_jsonb(s."status"),'revision',to_jsonb(s."revision"::text),'privacyGeneration',to_jsonb(s."privacy_generation"::text))=NEW.evidence_body->'committed'
   AND s.revision=NEW.committed_revision) INTO matches;
WHEN 'AuditEvent' THEN
  SELECT EXISTS(SELECT 1 FROM "app"."audit_events" s WHERE (to_jsonb(s)->>'id')=NEW.aggregate_id
   AND s.mutation_transaction_id=NEW.mutation_transaction_id
   AND jsonb_build_object('id',to_jsonb(s."id"))=NEW.evidence_body->'committed'
   AND 0::bigint=NEW.committed_revision) INTO matches;
WHEN 'UserSecurityProfile' THEN
  SELECT EXISTS(SELECT 1 FROM "app"."user_security_profiles" s WHERE (to_jsonb(s)->>'id')=NEW.aggregate_id
   AND s.mutation_transaction_id=NEW.mutation_transaction_id
   AND jsonb_build_object('id',to_jsonb(s."id"),'userId',to_jsonb(s."user_id"),'securityTier',to_jsonb(s."security_tier"),'phoneNumberHash',to_jsonb(s."phone_number_hash"),'revision',to_jsonb(s."revision"::text),'securityGeneration',to_jsonb(s."security_generation"::text))=NEW.evidence_body->'committed'
   AND s.revision=NEW.committed_revision) INTO matches;
WHEN 'AuthProviderAccount' THEN
  SELECT EXISTS(SELECT 1 FROM "app"."auth_provider_accounts" s WHERE (to_jsonb(s)->>'id')=NEW.aggregate_id
   AND s.mutation_transaction_id=NEW.mutation_transaction_id
   AND jsonb_build_object('id',to_jsonb(s."id"),'userId',to_jsonb(s."user_id"),'providerType',to_jsonb(s."provider_type"),'status',to_jsonb(s."status"),'revision',to_jsonb(s."revision"::text))=NEW.evidence_body->'committed'
   AND s.revision=NEW.committed_revision) INTO matches;
WHEN 'TrackPlan' THEN
  SELECT EXISTS(SELECT 1 FROM "app"."track_plans" s WHERE (to_jsonb(s)->>'id')=NEW.aggregate_id
   AND s.mutation_transaction_id=NEW.mutation_transaction_id
   AND jsonb_build_object('id',to_jsonb(s."id"),'track',to_jsonb(s."track"),'status',to_jsonb(s."status"),'billingModel',to_jsonb(s."billing_model"),'monthlyPriceCents',to_jsonb(s."monthly_price_cents"),'currency',to_jsonb(s."currency"),'revision',to_jsonb(s."revision"::text),'contentHash',to_jsonb(s."content_hash"))=NEW.evidence_body->'committed'
   AND s.revision=NEW.committed_revision) INTO matches;
WHEN 'TrackEntitlementDefinition' THEN
  SELECT EXISTS(SELECT 1 FROM "app"."track_entitlement_definitions" s WHERE (to_jsonb(s)->>'id')=NEW.aggregate_id
   AND s.mutation_transaction_id=NEW.mutation_transaction_id
   AND jsonb_build_object('id',to_jsonb(s."id"),'valueType',to_jsonb(s."value_type"),'track',to_jsonb(s."track"),'revision',to_jsonb(s."revision"::text))=NEW.evidence_body->'committed'
   AND s.revision=NEW.committed_revision) INTO matches;
WHEN 'TrackPlanEntitlement' THEN
  SELECT EXISTS(SELECT 1 FROM "app"."track_plan_entitlements" s WHERE (to_jsonb(s)->>'id')=NEW.aggregate_id
   AND s.mutation_transaction_id=NEW.mutation_transaction_id
   AND jsonb_build_object('id',to_jsonb(s."id"),'valueType',to_jsonb(s."value_type"),'usagePeriod',to_jsonb(s."usage_period"),'revision',to_jsonb(s."revision"::text))=NEW.evidence_body->'committed'
   AND s.revision=NEW.committed_revision) INTO matches;
WHEN 'TrackSubscription' THEN
  IF session_user::text='wa_worker' THEN
   matches:=platform_private.worker_evidence_source_matches(NEW.aggregate_kind,NEW.aggregate_id,NEW.committed_revision,NEW.mutation_transaction_id,NEW.evidence_body->'committed');
  ELSE
   SELECT EXISTS(SELECT 1 FROM "app"."track_subscriptions" s WHERE (to_jsonb(s)->>'id')=NEW.aggregate_id
   AND s.mutation_transaction_id=NEW.mutation_transaction_id
   AND jsonb_build_object('id',to_jsonb(s."id"),'userId',to_jsonb(s."user_id"),'track',to_jsonb(s."track"),'status',to_jsonb(s."status"),'provider',to_jsonb(s."provider"),'revision',to_jsonb(s."revision"::text))=NEW.evidence_body->'committed'
   AND s.revision=NEW.committed_revision) INTO matches;
  END IF;
WHEN 'TrackEntitlementGrant' THEN
  IF session_user::text='wa_worker' THEN
   matches:=platform_private.worker_evidence_source_matches(NEW.aggregate_kind,NEW.aggregate_id,NEW.committed_revision,NEW.mutation_transaction_id,NEW.evidence_body->'committed');
  ELSE
   SELECT EXISTS(SELECT 1 FROM "app"."track_entitlement_grants" s WHERE (to_jsonb(s)->>'id')=NEW.aggregate_id
   AND s.mutation_transaction_id=NEW.mutation_transaction_id
   AND jsonb_build_object('id',to_jsonb(s."id"),'userId',to_jsonb(s."user_id"),'track',to_jsonb(s."track"),'status',to_jsonb(s."status"),'valueType',to_jsonb(s."value_type"),'revision',to_jsonb(s."revision"::text))=NEW.evidence_body->'committed'
   AND s.revision=NEW.committed_revision) INTO matches;
  END IF;
WHEN 'TrackUsageEvent' THEN
  SELECT EXISTS(SELECT 1 FROM "app"."track_usage_events" s WHERE (to_jsonb(s)->>'id')=NEW.aggregate_id
   AND s.mutation_transaction_id=NEW.mutation_transaction_id
   AND jsonb_build_object('id',to_jsonb(s."id"),'userId',to_jsonb(s."user_id"),'track',to_jsonb(s."track"),'type',to_jsonb(s."type"),'semanticEffectKey',to_jsonb(s."semantic_effect_key"),'sourceRevision',to_jsonb(s."source_revision"::text),'sourceOwner',to_jsonb(s."source_owner"),'sourceId',to_jsonb(s."source_id"),'acceptedAt',to_jsonb(s."accepted_at"),'periodStart',to_jsonb(s."period_start"),'periodEnd',to_jsonb(s."period_end"))=NEW.evidence_body->'committed'
   AND 0::bigint=NEW.committed_revision) INTO matches;
WHEN 'TrackUsageCounter' THEN
  SELECT EXISTS(SELECT 1 FROM "app"."track_usage_counters" s WHERE (to_jsonb(s)->>'id')=NEW.aggregate_id
   AND s.mutation_transaction_id=NEW.mutation_transaction_id
   AND jsonb_build_object('id',to_jsonb(s."id"),'userId',to_jsonb(s."user_id"),'track',to_jsonb(s."track"),'period',to_jsonb(s."period"),'periodStart',to_jsonb(s."period_start"),'periodEnd',to_jsonb(s."period_end"),'usedQuantity',to_jsonb(s."used_quantity"),'limitQuantity',to_jsonb(s."limit_quantity"),'revision',to_jsonb(s."revision"::text),'sourceRevision',to_jsonb(s."source_revision"::text))=NEW.evidence_body->'committed'
   AND s.revision=NEW.committed_revision) INTO matches;
WHEN 'ConsentContentRevision' THEN
  SELECT EXISTS(SELECT 1 FROM "app"."consent_content_revision" s WHERE (to_jsonb(s)->>'id')=NEW.aggregate_id
   AND s.mutation_transaction_id=NEW.mutation_transaction_id
   AND jsonb_build_object('id',to_jsonb(s."id"),'type',to_jsonb(s."type"),'contentHash',to_jsonb(s."content_hash"),'reviewState',to_jsonb(s."review_state"))=NEW.evidence_body->'committed'
   AND 0::bigint=NEW.committed_revision) INTO matches;
WHEN 'ConsentPresentation' THEN
  SELECT EXISTS(SELECT 1 FROM "app"."consent_presentation" s WHERE (to_jsonb(s)->>'id')=NEW.aggregate_id
   AND s.mutation_transaction_id=NEW.mutation_transaction_id
   AND jsonb_build_object('id',to_jsonb(s."id"),'userId',to_jsonb(s."user_id"),'renderedHash',to_jsonb(s."rendered_hash"))=NEW.evidence_body->'committed'
   AND 0::bigint=NEW.committed_revision) INTO matches;
WHEN 'ConsentDisposition' THEN
  SELECT EXISTS(SELECT 1 FROM "app"."consent_disposition" s WHERE (to_jsonb(s)->>'id')=NEW.aggregate_id
   AND s.mutation_transaction_id=NEW.mutation_transaction_id
   AND jsonb_build_object('id',to_jsonb(s."id"),'userId',to_jsonb(s."user_id"),'kind',to_jsonb(s."kind"))=NEW.evidence_body->'committed'
   AND 0::bigint=NEW.committed_revision) INTO matches;
WHEN 'TrackBaseSelection' THEN
  IF session_user::text='wa_worker' THEN
   matches:=platform_private.worker_evidence_source_matches(NEW.aggregate_kind,NEW.aggregate_id,NEW.committed_revision,NEW.mutation_transaction_id,NEW.evidence_body->'committed');
  ELSE
   SELECT EXISTS(SELECT 1 FROM "app"."track_base_selection" s WHERE (to_jsonb(s)->>'id')=NEW.aggregate_id
   AND s.mutation_transaction_id=NEW.mutation_transaction_id
   AND jsonb_build_object('id',to_jsonb(s."id"),'userId',to_jsonb(s."user_id"),'track',to_jsonb(s."track"),'revision',to_jsonb(s."revision"::text),'sourceGeneration',to_jsonb(s."source_generation"::text))=NEW.evidence_body->'committed'
   AND s.revision=NEW.committed_revision) INTO matches;
  END IF;
WHEN 'TrackUsageReservation' THEN
  SELECT EXISTS(SELECT 1 FROM "app"."track_usage_reservation" s WHERE (to_jsonb(s)->>'id')=NEW.aggregate_id
   AND s.mutation_transaction_id=NEW.mutation_transaction_id
   AND jsonb_build_object('id',to_jsonb(s."id"),'userId',to_jsonb(s."user_id"),'periodStart',to_jsonb(s."period_start"),'periodEnd',to_jsonb(s."period_end"),'acceptedAt',to_jsonb(s."accepted_at"),'revision',to_jsonb(s."revision"::text))=NEW.evidence_body->'committed'
   AND s.revision=NEW.committed_revision) INTO matches;
WHEN 'PrivacyTargetInstruction' THEN
  SELECT EXISTS(SELECT 1 FROM "app"."privacy_target_instruction" s WHERE (to_jsonb(s)->>'id')=NEW.aggregate_id
   AND s.mutation_transaction_id=NEW.mutation_transaction_id
   AND jsonb_build_object('id',to_jsonb(s."id"),'sourceId',to_jsonb(s."source_id"),'sourceRevision',to_jsonb(s."source_revision"),'action',to_jsonb(s."action"),'generation',to_jsonb(s."generation"::text),'descriptorHash',to_jsonb(s."descriptor_hash"))=NEW.evidence_body->'committed'
   AND 0::bigint=NEW.committed_revision) INTO matches;
WHEN 'PrivacyOwnerReceipt' THEN
  SELECT EXISTS(SELECT 1 FROM "app"."privacy_owner_receipt" s WHERE (to_jsonb(s)->>'id')=NEW.aggregate_id
   AND s.mutation_transaction_id=NEW.mutation_transaction_id
   AND jsonb_build_object('id',to_jsonb(s."id"),'generation',to_jsonb(s."generation"::text),'disposition',to_jsonb(s."disposition"),'artifactDigest',to_jsonb(s."artifact_digest"))=NEW.evidence_body->'committed'
   AND 0::bigint=NEW.committed_revision) INTO matches;
WHEN 'PrivacyRestoreMarker' THEN
  SELECT EXISTS(SELECT 1 FROM "app"."privacy_restore_marker" s WHERE (to_jsonb(s)->>'id')=NEW.aggregate_id
   AND s.mutation_transaction_id=NEW.mutation_transaction_id
   AND jsonb_build_object('id',to_jsonb(s."id"),'sourceId',to_jsonb(s."source_id"),'generation',to_jsonb(s."generation"::text),'action',to_jsonb(s."action"),'revision',to_jsonb(s."revision"::text))=NEW.evidence_body->'committed'
   AND s.revision=NEW.committed_revision) INTO matches;
 ELSE RAISE EXCEPTION 'unsupported source or recursive evidence bootstrap';
 END CASE;
 IF NOT matches THEN RAISE EXCEPTION 'orphan or invented source evidence'; END IF;
 RETURN NULL;
END;
$wa$;

CREATE CONSTRAINT TRIGGER exact_evidence_source AFTER INSERT ON platform.owner_mutation_evidence DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.evidence_source_commit();

ALTER TABLE platform.owner_mutation_evidence ADD CONSTRAINT closed_evidence_json CHECK (CASE aggregate_kind WHEN 'ConsentLog' THEN platform_private.json_evidence_consentlog(evidence_body) WHEN 'PrivacyRequest' THEN platform_private.json_evidence_privacyrequest(evidence_body) WHEN 'AgeGateAttempt' THEN platform_private.json_evidence_agegateattempt(evidence_body) WHEN 'AgeGateBlock' THEN platform_private.json_evidence_agegateblock(evidence_body) WHEN 'AccessAuditLog' THEN platform_private.json_evidence_accessauditlog(evidence_body) WHEN 'User' THEN platform_private.json_evidence_user(evidence_body) WHEN 'UserRole' THEN platform_private.json_evidence_userrole(evidence_body) WHEN 'CustomerProfile' THEN platform_private.json_evidence_customerprofile(evidence_body) WHEN 'AuditEvent' THEN platform_private.json_evidence_auditevent(evidence_body) WHEN 'UserSecurityProfile' THEN platform_private.json_evidence_usersecurityprofile(evidence_body) WHEN 'AuthProviderAccount' THEN platform_private.json_evidence_authprovideraccount(evidence_body) WHEN 'TrackPlan' THEN platform_private.json_evidence_trackplan(evidence_body) WHEN 'TrackEntitlementDefinition' THEN platform_private.json_evidence_trackentitlementdefinition(evidence_body) WHEN 'TrackPlanEntitlement' THEN platform_private.json_evidence_trackplanentitlement(evidence_body) WHEN 'TrackSubscription' THEN platform_private.json_evidence_tracksubscription(evidence_body) WHEN 'TrackEntitlementGrant' THEN platform_private.json_evidence_trackentitlementgrant(evidence_body) WHEN 'TrackUsageEvent' THEN platform_private.json_evidence_trackusageevent(evidence_body) WHEN 'TrackUsageCounter' THEN platform_private.json_evidence_trackusagecounter(evidence_body) WHEN 'ConsentContentRevision' THEN platform_private.json_evidence_consentcontentrevision(evidence_body) WHEN 'ConsentPresentation' THEN platform_private.json_evidence_consentpresentation(evidence_body) WHEN 'ConsentDisposition' THEN platform_private.json_evidence_consentdisposition(evidence_body) WHEN 'TrackBaseSelection' THEN platform_private.json_evidence_trackbaseselection(evidence_body) WHEN 'TrackUsageReservation' THEN platform_private.json_evidence_trackusagereservation(evidence_body) WHEN 'PrivacyTargetInstruction' THEN platform_private.json_evidence_privacytargetinstruction(evidence_body) WHEN 'PrivacyOwnerReceipt' THEN platform_private.json_evidence_privacyownerreceipt(evidence_body) WHEN 'PrivacyRestoreMarker' THEN platform_private.json_evidence_privacyrestoremarker(evidence_body) ELSE false END);

REVOKE ALL ON ALL FUNCTIONS IN SCHEMA platform_private FROM PUBLIC;

GRANT EXECUTE ON FUNCTION platform_private.json_evidence_consentlog(jsonb) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.json_evidence_privacyrequest(jsonb) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.json_evidence_agegateattempt(jsonb) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.json_evidence_agegateblock(jsonb) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.json_evidence_accessauditlog(jsonb) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.json_evidence_user(jsonb) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.json_evidence_userrole(jsonb) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.json_evidence_professionalprofile(jsonb) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.json_evidence_customerprofile(jsonb) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.json_evidence_candidateprofile(jsonb) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.json_evidence_auditevent(jsonb) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.json_evidence_usersecurityprofile(jsonb) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.json_evidence_authprovideraccount(jsonb) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.json_evidence_trackplan(jsonb) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.json_evidence_trackentitlementdefinition(jsonb) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.json_evidence_trackplanentitlement(jsonb) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.json_evidence_tracksubscription(jsonb) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.json_evidence_trackentitlementgrant(jsonb) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.json_evidence_trackusageevent(jsonb) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.json_evidence_trackusagecounter(jsonb) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.json_evidence_tracksubscriptionevent(jsonb) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.json_evidence_consentcontentrevision(jsonb) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.json_evidence_consentpresentation(jsonb) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.json_evidence_consentdisposition(jsonb) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.json_evidence_databaseactiongrant(jsonb) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.json_evidence_runtimecommandreceipt(jsonb) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.json_evidence_runtimeoutboxmessage(jsonb) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.json_evidence_runtimeeffectreceipt(jsonb) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.json_evidence_runtimeworkitem(jsonb) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.json_evidence_runtimeattempt(jsonb) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.json_evidence_runtimeinboxreceipt(jsonb) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.json_evidence_runtimereservation(jsonb) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.json_evidence_ownermutationevidence(jsonb) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.json_evidence_customerprofilelifecycleevent(jsonb) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.json_evidence_trackbaseselection(jsonb) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.json_evidence_trackenrollmentreceipt(jsonb) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.json_evidence_trackusagereservation(jsonb) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.json_evidence_privacytargetinstruction(jsonb) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.json_evidence_privacyownerreceipt(jsonb) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.json_evidence_privacyrestoremarker(jsonb) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.json_customer_event(jsonb) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.json_track_command(jsonb) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.json_track_result(jsonb) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.json_sh004_result(jsonb) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.json_sh114_result(jsonb) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.json_datetime(text) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.bind_request_context(text) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.context_allows(text,text,text,text,text) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.row_allowed(text,text,text,text,text[],text,text) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.context_subject(uuid) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.context_subject_owner(uuid,text) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.command_context_allows(text,text,text) TO wa_app_runtime,wa_worker;

GRANT EXECUTE ON FUNCTION platform_private.global_context_registered(text,text,text,text) TO wa_app_runtime,wa_worker;

REVOKE EXECUTE ON FUNCTION platform_private.bound_grant(boolean) FROM wa_app_runtime,wa_worker;

GRANT CREATE ON SCHEMA platform_private TO wa_private_helper_owner;
ALTER FUNCTION platform_private.bound_grant(boolean) OWNER TO wa_private_helper_owner;

GRANT CREATE ON SCHEMA platform_private TO wa_private_helper_owner;
ALTER FUNCTION platform_private.bind_request_context(text) OWNER TO wa_private_helper_owner;

GRANT CREATE ON SCHEMA platform_private TO wa_private_helper_owner;
ALTER FUNCTION platform_private.context_allows(text,text,text,text,text) OWNER TO wa_private_helper_owner;

GRANT CREATE ON SCHEMA platform_private TO wa_private_helper_owner;
ALTER FUNCTION platform_private.protected_scope(text,text,text) OWNER TO wa_private_helper_owner;

GRANT CREATE ON SCHEMA platform_private TO wa_private_helper_owner;
ALTER FUNCTION platform_private.row_allowed(text,text,text,text,text[],text,text) OWNER TO wa_private_helper_owner;

GRANT CREATE ON SCHEMA platform_private TO wa_private_helper_owner;
ALTER FUNCTION platform_private.context_subject(uuid) OWNER TO wa_private_helper_owner;

GRANT CREATE ON SCHEMA platform_private TO wa_private_helper_owner;
ALTER FUNCTION platform_private.context_subject_owner(uuid,text) OWNER TO wa_private_helper_owner;

GRANT CREATE ON SCHEMA platform_private TO wa_private_helper_owner;
ALTER FUNCTION platform_private.command_context_allows(text,text,text) OWNER TO wa_private_helper_owner;

GRANT CREATE ON SCHEMA platform_private TO wa_customer_verifier;
ALTER FUNCTION platform_private.customer_current_for_track(uuid,uuid,bigint,bigint,uuid) OWNER TO wa_customer_verifier;

REVOKE CREATE ON SCHEMA platform_private FROM wa_customer_verifier;

GRANT CREATE ON SCHEMA platform_private TO wa_track_verifier;
ALTER FUNCTION platform_private.worker_track_allowed(text,jsonb,text) OWNER TO wa_track_verifier;

GRANT CREATE ON SCHEMA platform_private TO wa_track_verifier;
ALTER FUNCTION platform_private.worker_lease_valid(uuid,uuid,boolean) OWNER TO wa_track_verifier;

GRANT CREATE ON SCHEMA platform_private TO wa_track_verifier;
ALTER FUNCTION platform_private.worker_effect_matches(uuid,uuid,boolean) OWNER TO wa_track_verifier;

GRANT CREATE ON SCHEMA platform_private TO wa_track_verifier;
ALTER FUNCTION platform_private.track_atomic_valid(text,jsonb,jsonb) OWNER TO wa_track_verifier;

GRANT CREATE ON SCHEMA platform_private TO wa_track_verifier;
ALTER FUNCTION platform_private.worker_evidence_source_matches(text,text,bigint,text,jsonb) OWNER TO wa_track_verifier;

REVOKE CREATE ON SCHEMA platform_private FROM wa_track_verifier;

GRANT EXECUTE ON FUNCTION platform_private.bound_grant(boolean),platform_private.context_allows(text,text,text,text,text) TO wa_customer_verifier,wa_track_verifier;
GRANT EXECUTE ON FUNCTION platform_private.customer_current_for_track(uuid,uuid,bigint,bigint,uuid) TO wa_track_verifier;
GRANT EXECUTE ON FUNCTION platform_private.worker_track_allowed(text,jsonb,text),platform_private.worker_lease_valid(uuid,uuid,boolean),platform_private.worker_effect_matches(uuid,uuid,boolean),platform_private.track_atomic_valid(text,jsonb,jsonb),platform_private.worker_evidence_source_matches(text,text,bigint,text,jsonb) TO wa_worker;
GRANT EXECUTE ON FUNCTION platform_private.lease_secret_matches(text) TO wa_track_verifier,wa_worker;
REVOKE CREATE ON SCHEMA platform_private FROM wa_private_helper_owner;
-- Separate original bootstrap grantor must run foundation-bootstrap-finalize.review.sql
-- after success OR failure. wa_schema_owner has ADMIN FALSE and cannot do that cleanup.
-- Helper may call its own functions and pure JSON predicates only; no business DML.
-- Owned context functions need no grant of arbitrary application functions.
-- Issuer invokes only grant trigger automatically; no context discovery endpoints.
REVOKE ALL ON ALL TABLES IN SCHEMA app,platform FROM PUBLIC;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA app,platform FROM PUBLIC;
-- Managed browser/service roles are untouched; revoke application grants if present.
DO $roles$ DECLARE r text; BEGIN
 FOREACH r IN ARRAY ARRAY['anon','authenticated','service_role'] LOOP
  IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname=r) THEN
   EXECUTE format('REVOKE ALL ON ALL TABLES IN SCHEMA app,platform FROM %I',r);
   EXECUTE format('REVOKE ALL ON SCHEMA app,platform,platform_private FROM %I',r);
   EXECUTE format('REVOKE ALL ON ALL FUNCTIONS IN SCHEMA platform_private FROM %I',r);
  END IF;
 END LOOP;
END $roles$;
RESET ROLE;
COMMIT;
