-- CreateSchema
CREATE SCHEMA IF NOT EXISTS "app";

-- CreateEnum
CREATE TYPE "app"."platform_role" AS ENUM ('user', 'admin', 'support');

-- CreateEnum
CREATE TYPE "app"."organization_role" AS ENUM ('owner', 'admin', 'recruiter', 'member', 'viewer');

-- CreateEnum
CREATE TYPE "app"."profile_status" AS ENUM ('draft', 'active', 'paused', 'suspended', 'archived');

-- CreateEnum
CREATE TYPE "app"."organization_status" AS ENUM ('draft', 'active', 'suspended', 'archived');

-- CreateEnum
CREATE TYPE "app"."offering_kind" AS ENUM ('service', 'product', 'course', 'bundle');

-- CreateEnum
CREATE TYPE "app"."offering_status" AS ENUM ('draft', 'active', 'paused', 'archived');

-- CreateEnum
CREATE TYPE "app"."service_delivery_mode" AS ENUM ('digital', 'in_person', 'hybrid');

-- CreateEnum
CREATE TYPE "app"."product_delivery_mode" AS ENUM ('download', 'shipped', 'external_access');

-- CreateEnum
CREATE TYPE "app"."course_delivery_mode" AS ENUM ('self_paced', 'live', 'cohort', 'hybrid');

-- CreateEnum
CREATE TYPE "app"."gig_status" AS ENUM ('draft', 'open', 'paused', 'assigned', 'completed', 'cancelled', 'expired', 'archived');

-- CreateEnum
CREATE TYPE "app"."gig_visibility" AS ENUM ('public', 'private', 'invite_only');

-- CreateEnum
CREATE TYPE "app"."gig_response_status" AS ENUM ('submitted', 'viewed', 'shortlisted', 'accepted', 'rejected', 'withdrawn');

-- CreateEnum
CREATE TYPE "app"."gig_assignment_status" AS ENUM ('proposed', 'accepted', 'active', 'delivered', 'completed', 'cancelled', 'disputed');

-- CreateEnum
CREATE TYPE "app"."job_status" AS ENUM ('draft', 'open', 'paused', 'filled', 'closed', 'archived');

-- CreateEnum
CREATE TYPE "app"."job_visibility" AS ENUM ('public', 'private', 'invite_only');

-- CreateEnum
CREATE TYPE "app"."employment_type" AS ENUM ('full_time', 'part_time', 'contract', 'freelance', 'internship', 'temporary');

-- CreateEnum
CREATE TYPE "app"."job_application_status" AS ENUM ('submitted', 'viewed', 'withdrawn', 'rejected', 'accepted_offer', 'hired');

-- CreateEnum
CREATE TYPE "app"."job_application_stage" AS ENUM ('new_', 'screen', 'interview', 'offer', 'hired', 'closed');

-- CreateEnum
CREATE TYPE "app"."order_status" AS ENUM ('draft', 'pending_payment', 'paid', 'awaiting_seller', 'accepted', 'in_progress', 'delivered', 'completed', 'cancelled', 'refunded', 'disputed');

-- CreateEnum
CREATE TYPE "app"."media_asset_status" AS ENUM ('uploaded', 'processing', 'ready', 'failed', 'deleted');

-- CreateEnum
CREATE TYPE "app"."order_source_type" AS ENUM ('offering', 'gig_assignment');

-- CreateEnum
CREATE TYPE "app"."order_event_actor" AS ENUM ('system', 'webhook', 'buyer', 'professional', 'admin');

-- CreateEnum
CREATE TYPE "app"."file_role" AS ENUM ('buyer', 'professional', 'admin', 'system');

-- CreateEnum
CREATE TYPE "app"."refund_status" AS ENUM ('none', 'requested', 'partial', 'refunded', 'denied');

-- CreateEnum
CREATE TYPE "app"."review_status" AS ENUM ('pending', 'published', 'hidden', 'removed');

-- CreateEnum
CREATE TYPE "app"."dispute_status" AS ENUM ('open', 'under_review', 'resolved_refund', 'resolved_release', 'dismissed', 'closed');

-- CreateEnum
CREATE TYPE "app"."thread_context_type" AS ENUM ('order', 'gig', 'gig_response', 'gig_assignment', 'job_application', 'direct', 'support');

-- CreateEnum
CREATE TYPE "app"."notification_status" AS ENUM ('queued', 'sent', 'read', 'dismissed', 'failed');

-- CreateEnum
CREATE TYPE "app"."search_entity_type" AS ENUM ('user', 'professional_profile', 'candidate_profile', 'organization', 'offering', 'gig', 'job', 'taxonomy');

-- CreateEnum
CREATE TYPE "app"."calendar_provider" AS ENUM ('google', 'microsoft', 'cronofy', 'nylas', 'other');

-- CreateEnum
CREATE TYPE "app"."tag_source" AS ENUM ('user', 'professional', 'organization', 'ai', 'admin', 'system');

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
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "users_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."user_roles" (
    "user_id" UUID NOT NULL,
    "role" "app"."platform_role" NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "user_roles_pkey" PRIMARY KEY ("user_id","role")
);

-- CreateTable
CREATE TABLE "app"."organizations" (
    "id" UUID NOT NULL,
    "slug" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "description" TEXT,
    "logo_url" TEXT,
    "website_url" TEXT,
    "industry" TEXT,
    "city" TEXT,
    "state" TEXT,
    "country" TEXT,
    "status" "app"."organization_status" NOT NULL DEFAULT 'draft',
    "owner_user_id" UUID,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "organizations_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."organization_members" (
    "organization_id" UUID NOT NULL,
    "user_id" UUID NOT NULL,
    "role" "app"."organization_role" NOT NULL DEFAULT 'member',
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "organization_members_pkey" PRIMARY KEY ("organization_id","user_id")
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
    "onboarding_complete_at" TIMESTAMP(3),
    "default_currency" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "professional_profiles_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."candidate_profiles" (
    "id" UUID NOT NULL,
    "user_id" UUID NOT NULL,
    "headline" TEXT,
    "resume_url" TEXT,
    "portfolio_url" TEXT,
    "availability" TEXT,
    "city" TEXT,
    "state" TEXT,
    "country" TEXT,
    "status" "app"."profile_status" NOT NULL DEFAULT 'draft',
    "is_visible" BOOLEAN NOT NULL DEFAULT true,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "candidate_profiles_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."taxonomy_domains" (
    "id" UUID NOT NULL,
    "name" TEXT NOT NULL,
    "slug" TEXT NOT NULL,
    "description" TEXT,
    "display_order" INTEGER,
    "is_active" BOOLEAN NOT NULL DEFAULT true,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "taxonomy_domains_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."taxonomy_categories" (
    "id" UUID NOT NULL,
    "domain_id" UUID NOT NULL,
    "name" TEXT NOT NULL,
    "slug" TEXT NOT NULL,
    "description" TEXT,
    "icon" TEXT,
    "display_order" INTEGER,
    "is_active" BOOLEAN NOT NULL DEFAULT true,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "taxonomy_categories_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."taxonomy_tags" (
    "id" UUID NOT NULL,
    "category_id" UUID NOT NULL,
    "name" TEXT NOT NULL,
    "slug" TEXT NOT NULL,
    "description" TEXT,
    "display_order" INTEGER,
    "is_active" BOOLEAN NOT NULL DEFAULT true,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "taxonomy_tags_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."professional_categories" (
    "professional_profile_id" UUID NOT NULL,
    "category_id" UUID NOT NULL,

    CONSTRAINT "professional_categories_pkey" PRIMARY KEY ("professional_profile_id","category_id")
);

-- CreateTable
CREATE TABLE "app"."professional_tags" (
    "professional_profile_id" UUID NOT NULL,
    "tag_id" UUID NOT NULL,
    "source" "app"."tag_source" NOT NULL DEFAULT 'user',
    "confidence" DOUBLE PRECISION,
    "verified" BOOLEAN NOT NULL DEFAULT false,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "professional_tags_pkey" PRIMARY KEY ("professional_profile_id","tag_id")
);

-- CreateTable
CREATE TABLE "app"."candidate_categories" (
    "candidate_profile_id" UUID NOT NULL,
    "category_id" UUID NOT NULL,

    CONSTRAINT "candidate_categories_pkey" PRIMARY KEY ("candidate_profile_id","category_id")
);

-- CreateTable
CREATE TABLE "app"."candidate_tags" (
    "candidate_profile_id" UUID NOT NULL,
    "tag_id" UUID NOT NULL,
    "source" "app"."tag_source" NOT NULL DEFAULT 'user',
    "confidence" DOUBLE PRECISION,
    "verified" BOOLEAN NOT NULL DEFAULT false,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "candidate_tags_pkey" PRIMARY KEY ("candidate_profile_id","tag_id")
);

-- CreateTable
CREATE TABLE "app"."organization_categories" (
    "organization_id" UUID NOT NULL,
    "category_id" UUID NOT NULL,

    CONSTRAINT "organization_categories_pkey" PRIMARY KEY ("organization_id","category_id")
);

-- CreateTable
CREATE TABLE "app"."organization_tags" (
    "organization_id" UUID NOT NULL,
    "tag_id" UUID NOT NULL,
    "source" "app"."tag_source" NOT NULL DEFAULT 'user',
    "confidence" DOUBLE PRECISION,
    "verified" BOOLEAN NOT NULL DEFAULT false,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "organization_tags_pkey" PRIMARY KEY ("organization_id","tag_id")
);

-- CreateTable
CREATE TABLE "app"."offerings" (
    "id" UUID NOT NULL,
    "kind" "app"."offering_kind" NOT NULL,
    "slug" TEXT NOT NULL,
    "title" TEXT NOT NULL,
    "summary" TEXT,
    "description" TEXT,
    "status" "app"."offering_status" NOT NULL DEFAULT 'draft',
    "professional_profile_id" UUID NOT NULL,
    "domain_id" UUID NOT NULL,
    "category_id" UUID,
    "price_from_cents" INTEGER,
    "currency" TEXT NOT NULL DEFAULT 'usd',
    "is_featured" BOOLEAN NOT NULL DEFAULT false,
    "is_public" BOOLEAN NOT NULL DEFAULT true,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "offerings_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."service_details" (
    "offering_id" UUID NOT NULL,
    "delivery_mode" "app"."service_delivery_mode" NOT NULL,
    "duration_minutes" INTEGER,
    "min_start_delay_days" INTEGER,
    "booking_buffer_min" INTEGER DEFAULT 15,

    CONSTRAINT "service_details_pkey" PRIMARY KEY ("offering_id")
);

-- CreateTable
CREATE TABLE "app"."product_details" (
    "offering_id" UUID NOT NULL,
    "delivery_mode" "app"."product_delivery_mode" NOT NULL,
    "file_asset_id" UUID,
    "external_url" TEXT,

    CONSTRAINT "product_details_pkey" PRIMARY KEY ("offering_id")
);

-- CreateTable
CREATE TABLE "app"."course_details" (
    "offering_id" UUID NOT NULL,
    "delivery_mode" "app"."course_delivery_mode" NOT NULL,
    "course_length_minutes" INTEGER,
    "lesson_count" INTEGER,
    "starts_at" TIMESTAMP(3),
    "ends_at" TIMESTAMP(3),
    "enrollment_limit" INTEGER,
    "external_url" TEXT,
    "access_expires_after_days" INTEGER,

    CONSTRAINT "course_details_pkey" PRIMARY KEY ("offering_id")
);

-- CreateTable
CREATE TABLE "app"."pricing_tiers" (
    "id" UUID NOT NULL,
    "offering_id" UUID NOT NULL,
    "name" TEXT NOT NULL,
    "description" TEXT,
    "price_cents" INTEGER NOT NULL,
    "currency" TEXT NOT NULL DEFAULT 'usd',
    "display_order" INTEGER,
    "is_active" BOOLEAN NOT NULL DEFAULT true,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "pricing_tiers_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."offering_media" (
    "offering_id" UUID NOT NULL,
    "media_id" UUID NOT NULL,
    "sort_order" INTEGER NOT NULL DEFAULT 0,

    CONSTRAINT "offering_media_pkey" PRIMARY KEY ("offering_id","media_id")
);

-- CreateTable
CREATE TABLE "app"."offering_tags" (
    "offering_id" UUID NOT NULL,
    "tag_id" UUID NOT NULL,
    "source" "app"."tag_source" NOT NULL DEFAULT 'user',
    "confidence" DOUBLE PRECISION,
    "verified" BOOLEAN NOT NULL DEFAULT false,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "offering_tags_pkey" PRIMARY KEY ("offering_id","tag_id")
);

-- CreateTable
CREATE TABLE "app"."gigs" (
    "id" UUID NOT NULL,
    "poster_user_id" UUID NOT NULL,
    "title" TEXT NOT NULL,
    "description" TEXT NOT NULL,
    "status" "app"."gig_status" NOT NULL DEFAULT 'draft',
    "visibility" "app"."gig_visibility" NOT NULL DEFAULT 'public',
    "domain_id" UUID NOT NULL,
    "category_id" UUID,
    "budget_min_cents" INTEGER,
    "budget_max_cents" INTEGER,
    "currency" TEXT NOT NULL DEFAULT 'usd',
    "location" TEXT,
    "city" TEXT,
    "state" TEXT,
    "country" TEXT,
    "remote_ok" BOOLEAN NOT NULL DEFAULT true,
    "due_at" TIMESTAMP(3),
    "closes_at" TIMESTAMP(3),
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "gigs_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."gig_tags" (
    "gig_id" UUID NOT NULL,
    "tag_id" UUID NOT NULL,
    "source" "app"."tag_source" NOT NULL DEFAULT 'user',
    "confidence" DOUBLE PRECISION,
    "verified" BOOLEAN NOT NULL DEFAULT false,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "gig_tags_pkey" PRIMARY KEY ("gig_id","tag_id")
);

-- CreateTable
CREATE TABLE "app"."gig_responses" (
    "id" UUID NOT NULL,
    "gig_id" UUID NOT NULL,
    "responder_user_id" UUID,
    "professional_profile_id" UUID NOT NULL,
    "message" TEXT,
    "proposed_cents" INTEGER,
    "currency" TEXT NOT NULL DEFAULT 'usd',
    "estimated_days" INTEGER,
    "status" "app"."gig_response_status" NOT NULL DEFAULT 'submitted',
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "gig_responses_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."gig_assignments" (
    "id" UUID NOT NULL,
    "gig_id" UUID NOT NULL,
    "gig_response_id" UUID,
    "professional_profile_id" UUID NOT NULL,
    "buyer_user_id" UUID NOT NULL,
    "status" "app"."gig_assignment_status" NOT NULL DEFAULT 'proposed',
    "title" TEXT,
    "description" TEXT,
    "agreed_price_cents" INTEGER,
    "currency" TEXT NOT NULL DEFAULT 'usd',
    "starts_at" TIMESTAMP(3),
    "due_at" TIMESTAMP(3),
    "delivered_at" TIMESTAMP(3),
    "completed_at" TIMESTAMP(3),
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "gig_assignments_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."jobs" (
    "id" UUID NOT NULL,
    "organization_id" UUID NOT NULL,
    "title" TEXT NOT NULL,
    "description" TEXT NOT NULL,
    "status" "app"."job_status" NOT NULL DEFAULT 'draft',
    "visibility" "app"."job_visibility" NOT NULL DEFAULT 'public',
    "employment_type" "app"."employment_type" NOT NULL,
    "domain_id" UUID NOT NULL,
    "category_id" UUID,
    "location" TEXT,
    "city" TEXT,
    "state" TEXT,
    "country" TEXT,
    "remote_ok" BOOLEAN NOT NULL DEFAULT false,
    "compensation_min_cents" INTEGER,
    "compensation_max_cents" INTEGER,
    "currency" TEXT NOT NULL DEFAULT 'usd',
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,
    "closes_at" TIMESTAMP(3),

    CONSTRAINT "jobs_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."job_applications" (
    "id" UUID NOT NULL,
    "job_id" UUID NOT NULL,
    "candidate_profile_id" UUID NOT NULL,
    "resume_url" TEXT,
    "cover_letter" TEXT,
    "answers" JSONB,
    "invited" BOOLEAN NOT NULL DEFAULT false,
    "status" "app"."job_application_status" NOT NULL DEFAULT 'submitted',
    "stage" "app"."job_application_stage" NOT NULL DEFAULT 'new_',
    "submitted_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "viewed_at" TIMESTAMP(3),
    "interview_at" TIMESTAMP(3),
    "offer_at" TIMESTAMP(3),
    "hired_at" TIMESTAMP(3),
    "rejected_at" TIMESTAMP(3),
    "withdrawn_at" TIMESTAMP(3),

    CONSTRAINT "job_applications_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."job_tags" (
    "job_id" UUID NOT NULL,
    "tag_id" UUID NOT NULL,
    "source" "app"."tag_source" NOT NULL DEFAULT 'user',
    "confidence" DOUBLE PRECISION,
    "verified" BOOLEAN NOT NULL DEFAULT false,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "job_tags_pkey" PRIMARY KEY ("job_id","tag_id")
);

-- CreateTable
CREATE TABLE "app"."orders" (
    "id" UUID NOT NULL,
    "status" "app"."order_status" NOT NULL DEFAULT 'draft',
    "source_type" "app"."order_source_type" NOT NULL,
    "offering_id" UUID,
    "gig_assignment_id" UUID,
    "buyer_user_id" UUID NOT NULL,
    "seller_professional_profile_id" UUID NOT NULL,
    "price_cents" INTEGER,
    "currency" TEXT NOT NULL DEFAULT 'usd',
    "refund_status" "app"."refund_status" NOT NULL DEFAULT 'none',
    "stripe_checkout_session_id" TEXT,
    "stripe_payment_intent_id" TEXT,
    "stripe_transfer_id" TEXT,
    "application_fee_cents" INTEGER,
    "brief_text" TEXT,
    "delivery_note" TEXT,
    "revision_count" INTEGER NOT NULL DEFAULT 0,
    "paid_at" TIMESTAMP(3),
    "accepted_at" TIMESTAMP(3),
    "delivered_at" TIMESTAMP(3),
    "completed_at" TIMESTAMP(3),
    "cancelled_at" TIMESTAMP(3),
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "orders_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."order_files" (
    "id" UUID NOT NULL,
    "order_id" UUID NOT NULL,
    "media_id" UUID NOT NULL,
    "role" "app"."file_role" NOT NULL,
    "note" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "order_files_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."order_events" (
    "id" UUID NOT NULL,
    "order_id" UUID NOT NULL,
    "actor" "app"."order_event_actor" NOT NULL,
    "actor_id" UUID,
    "from_status" "app"."order_status",
    "to_status" "app"."order_status",
    "name" TEXT NOT NULL,
    "reason" TEXT,
    "metadata" JSONB,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "order_events_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."agreements" (
    "id" UUID NOT NULL,
    "order_id" UUID NOT NULL,
    "template_key" TEXT NOT NULL,
    "buyer_sig_url" TEXT,
    "seller_sig_url" TEXT,
    "pdf_media_id" UUID,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "signed_at" TIMESTAMP(3),

    CONSTRAINT "agreements_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."reviews" (
    "id" UUID NOT NULL,
    "order_id" UUID NOT NULL,
    "reviewer_user_id" UUID,
    "professional_profile_id" UUID,
    "rating" INTEGER NOT NULL,
    "comment" TEXT,
    "status" "app"."review_status" NOT NULL DEFAULT 'pending',
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "reviews_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."disputes" (
    "id" UUID NOT NULL,
    "order_id" UUID NOT NULL,
    "opened_by_id" UUID,
    "reason" TEXT NOT NULL,
    "status" "app"."dispute_status" NOT NULL DEFAULT 'open',
    "admin_notes" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "resolved_at" TIMESTAMP(3),

    CONSTRAINT "disputes_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."media_assets" (
    "id" UUID NOT NULL,
    "uploaded_by_user_id" UUID,
    "bucket" TEXT,
    "storage_key" TEXT NOT NULL,
    "public_url" TEXT,
    "mime_type" TEXT,
    "size_bytes" INTEGER,
    "checksum" TEXT,
    "alt_text" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "status" "app"."media_asset_status" NOT NULL DEFAULT 'uploaded',

    CONSTRAINT "media_assets_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."gig_media" (
    "gig_id" UUID NOT NULL,
    "media_id" UUID NOT NULL,
    "role" TEXT,
    "sort_order" INTEGER NOT NULL DEFAULT 0,

    CONSTRAINT "gig_media_pkey" PRIMARY KEY ("gig_id","media_id")
);

-- CreateTable
CREATE TABLE "app"."user_media" (
    "user_id" UUID NOT NULL,
    "media_id" UUID NOT NULL,
    "role" TEXT,
    "sort_order" INTEGER NOT NULL DEFAULT 0,

    CONSTRAINT "user_media_pkey" PRIMARY KEY ("user_id","media_id")
);

-- CreateTable
CREATE TABLE "app"."professional_profile_media" (
    "professional_profile_id" UUID NOT NULL,
    "media_id" UUID NOT NULL,
    "role" TEXT,
    "sort_order" INTEGER NOT NULL DEFAULT 0,

    CONSTRAINT "professional_profile_media_pkey" PRIMARY KEY ("professional_profile_id","media_id")
);

-- CreateTable
CREATE TABLE "app"."candidate_profile_media" (
    "candidate_profile_id" UUID NOT NULL,
    "media_id" UUID NOT NULL,
    "role" TEXT,
    "sort_order" INTEGER NOT NULL DEFAULT 0,

    CONSTRAINT "candidate_profile_media_pkey" PRIMARY KEY ("candidate_profile_id","media_id")
);

-- CreateTable
CREATE TABLE "app"."organization_media" (
    "organization_id" UUID NOT NULL,
    "media_id" UUID NOT NULL,
    "role" TEXT,
    "sort_order" INTEGER NOT NULL DEFAULT 0,

    CONSTRAINT "organization_media_pkey" PRIMARY KEY ("organization_id","media_id")
);

-- CreateTable
CREATE TABLE "app"."job_media" (
    "job_id" UUID NOT NULL,
    "media_id" UUID NOT NULL,
    "role" TEXT,
    "sort_order" INTEGER NOT NULL DEFAULT 0,

    CONSTRAINT "job_media_pkey" PRIMARY KEY ("job_id","media_id")
);

-- CreateTable
CREATE TABLE "app"."availability_rules" (
    "id" UUID NOT NULL,
    "professional_profile_id" UUID NOT NULL,
    "weekday" INTEGER NOT NULL,
    "start_time" TEXT NOT NULL,
    "end_time" TEXT NOT NULL,
    "timezone" TEXT NOT NULL DEFAULT 'UTC',
    "is_active" BOOLEAN NOT NULL DEFAULT true,

    CONSTRAINT "availability_rules_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."calendar_connections" (
    "id" UUID NOT NULL,
    "professional_profile_id" UUID NOT NULL,
    "provider" "app"."calendar_provider" NOT NULL,
    "external_account_id" TEXT,
    "encrypted_oauth_json" JSONB,
    "status" TEXT NOT NULL DEFAULT 'active',
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "calendar_connections_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."busy_windows" (
    "id" UUID NOT NULL,
    "professional_profile_id" UUID NOT NULL,
    "source" TEXT NOT NULL,
    "start_at" TIMESTAMP(3) NOT NULL,
    "end_at" TIMESTAMP(3) NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "busy_windows_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."threads" (
    "id" UUID NOT NULL,
    "context_type" "app"."thread_context_type" NOT NULL,
    "context_id" UUID,
    "order_id" UUID,
    "gig_id" UUID,
    "gig_response_id" UUID,
    "gig_assignment_id" UUID,
    "job_application_id" UUID,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "threads_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."thread_participants" (
    "thread_id" UUID NOT NULL,
    "user_id" UUID NOT NULL,
    "joined_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "last_read_at" TIMESTAMP(3),

    CONSTRAINT "thread_participants_pkey" PRIMARY KEY ("thread_id","user_id")
);

-- CreateTable
CREATE TABLE "app"."messages" (
    "id" UUID NOT NULL,
    "thread_id" UUID NOT NULL,
    "sender_id" UUID,
    "content" TEXT NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "edited_at" TIMESTAMP(3),
    "deleted_at" TIMESTAMP(3),

    CONSTRAINT "messages_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."message_media" (
    "message_id" UUID NOT NULL,
    "media_id" UUID NOT NULL,

    CONSTRAINT "message_media_pkey" PRIMARY KEY ("message_id","media_id")
);

-- CreateTable
CREATE TABLE "app"."notifications" (
    "id" UUID NOT NULL,
    "user_id" UUID,
    "organization_id" UUID,
    "channel" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "status" "app"."notification_status" NOT NULL DEFAULT 'queued',
    "payload" JSONB,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "read_at" TIMESTAMP(3),

    CONSTRAINT "notifications_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."search_upsert_events" (
    "id" UUID NOT NULL,
    "entity_type" "app"."search_entity_type" NOT NULL,
    "entity_id" UUID NOT NULL,
    "reason" TEXT,
    "processed" BOOLEAN NOT NULL DEFAULT false,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "processed_at" TIMESTAMP(3),

    CONSTRAINT "search_upsert_events_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "app"."processed_stripe_events" (
    "event_id" TEXT NOT NULL,
    "type" TEXT NOT NULL,
    "received_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "processed_stripe_events_pkey" PRIMARY KEY ("event_id")
);

-- CreateTable
CREATE TABLE "app"."audit_events" (
    "id" UUID NOT NULL,
    "actor_user_id" UUID,
    "entity_type" TEXT NOT NULL,
    "entity_id" UUID,
    "action" TEXT NOT NULL,
    "metadata" JSONB,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "audit_events_pkey" PRIMARY KEY ("id")
);

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
CREATE UNIQUE INDEX "organizations_slug_key" ON "app"."organizations"("slug");

-- CreateIndex
CREATE INDEX "organizations_status_idx" ON "app"."organizations"("status");

-- CreateIndex
CREATE INDEX "organizations_city_state_country_idx" ON "app"."organizations"("city", "state", "country");

-- CreateIndex
CREATE INDEX "organizations_owner_user_id_idx" ON "app"."organizations"("owner_user_id");

-- CreateIndex
CREATE INDEX "organization_members_user_id_role_idx" ON "app"."organization_members"("user_id", "role");

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
CREATE UNIQUE INDEX "candidate_profiles_user_id_key" ON "app"."candidate_profiles"("user_id");

-- CreateIndex
CREATE INDEX "candidate_profiles_status_is_visible_idx" ON "app"."candidate_profiles"("status", "is_visible");

-- CreateIndex
CREATE INDEX "candidate_profiles_country_state_city_idx" ON "app"."candidate_profiles"("country", "state", "city");

-- CreateIndex
CREATE UNIQUE INDEX "taxonomy_domains_name_key" ON "app"."taxonomy_domains"("name");

-- CreateIndex
CREATE UNIQUE INDEX "taxonomy_domains_slug_key" ON "app"."taxonomy_domains"("slug");

-- CreateIndex
CREATE INDEX "taxonomy_domains_is_active_idx" ON "app"."taxonomy_domains"("is_active");

-- CreateIndex
CREATE INDEX "taxonomy_categories_is_active_idx" ON "app"."taxonomy_categories"("is_active");

-- CreateIndex
CREATE UNIQUE INDEX "taxonomy_categories_domain_id_slug_key" ON "app"."taxonomy_categories"("domain_id", "slug");

-- CreateIndex
CREATE UNIQUE INDEX "taxonomy_categories_domain_id_name_key" ON "app"."taxonomy_categories"("domain_id", "name");

-- CreateIndex
CREATE INDEX "taxonomy_tags_is_active_idx" ON "app"."taxonomy_tags"("is_active");

-- CreateIndex
CREATE UNIQUE INDEX "taxonomy_tags_category_id_slug_key" ON "app"."taxonomy_tags"("category_id", "slug");

-- CreateIndex
CREATE UNIQUE INDEX "taxonomy_tags_category_id_name_key" ON "app"."taxonomy_tags"("category_id", "name");

-- CreateIndex
CREATE INDEX "professional_categories_category_id_idx" ON "app"."professional_categories"("category_id");

-- CreateIndex
CREATE INDEX "professional_tags_tag_id_idx" ON "app"."professional_tags"("tag_id");

-- CreateIndex
CREATE INDEX "professional_tags_source_idx" ON "app"."professional_tags"("source");

-- CreateIndex
CREATE INDEX "professional_tags_verified_idx" ON "app"."professional_tags"("verified");

-- CreateIndex
CREATE INDEX "candidate_categories_category_id_idx" ON "app"."candidate_categories"("category_id");

-- CreateIndex
CREATE INDEX "candidate_tags_tag_id_idx" ON "app"."candidate_tags"("tag_id");

-- CreateIndex
CREATE INDEX "candidate_tags_source_idx" ON "app"."candidate_tags"("source");

-- CreateIndex
CREATE INDEX "candidate_tags_verified_idx" ON "app"."candidate_tags"("verified");

-- CreateIndex
CREATE INDEX "organization_categories_category_id_idx" ON "app"."organization_categories"("category_id");

-- CreateIndex
CREATE INDEX "organization_tags_tag_id_idx" ON "app"."organization_tags"("tag_id");

-- CreateIndex
CREATE INDEX "organization_tags_source_idx" ON "app"."organization_tags"("source");

-- CreateIndex
CREATE INDEX "organization_tags_verified_idx" ON "app"."organization_tags"("verified");

-- CreateIndex
CREATE INDEX "offerings_kind_status_idx" ON "app"."offerings"("kind", "status");

-- CreateIndex
CREATE INDEX "offerings_professional_profile_id_idx" ON "app"."offerings"("professional_profile_id");

-- CreateIndex
CREATE INDEX "offerings_domain_id_idx" ON "app"."offerings"("domain_id");

-- CreateIndex
CREATE INDEX "offerings_category_id_idx" ON "app"."offerings"("category_id");

-- CreateIndex
CREATE UNIQUE INDEX "offerings_professional_profile_id_slug_key" ON "app"."offerings"("professional_profile_id", "slug");

-- CreateIndex
CREATE INDEX "pricing_tiers_offering_id_is_active_idx" ON "app"."pricing_tiers"("offering_id", "is_active");

-- CreateIndex
CREATE INDEX "offering_media_media_id_idx" ON "app"."offering_media"("media_id");

-- CreateIndex
CREATE INDEX "offering_tags_tag_id_idx" ON "app"."offering_tags"("tag_id");

-- CreateIndex
CREATE INDEX "offering_tags_source_idx" ON "app"."offering_tags"("source");

-- CreateIndex
CREATE INDEX "offering_tags_verified_idx" ON "app"."offering_tags"("verified");

-- CreateIndex
CREATE INDEX "gigs_poster_user_id_idx" ON "app"."gigs"("poster_user_id");

-- CreateIndex
CREATE INDEX "gigs_status_visibility_idx" ON "app"."gigs"("status", "visibility");

-- CreateIndex
CREATE INDEX "gigs_domain_id_idx" ON "app"."gigs"("domain_id");

-- CreateIndex
CREATE INDEX "gigs_category_id_idx" ON "app"."gigs"("category_id");

-- CreateIndex
CREATE INDEX "gigs_city_state_country_idx" ON "app"."gigs"("city", "state", "country");

-- CreateIndex
CREATE INDEX "gigs_remote_ok_idx" ON "app"."gigs"("remote_ok");

-- CreateIndex
CREATE INDEX "gig_tags_tag_id_idx" ON "app"."gig_tags"("tag_id");

-- CreateIndex
CREATE INDEX "gig_tags_source_idx" ON "app"."gig_tags"("source");

-- CreateIndex
CREATE INDEX "gig_tags_verified_idx" ON "app"."gig_tags"("verified");

-- CreateIndex
CREATE INDEX "gig_responses_professional_profile_id_status_idx" ON "app"."gig_responses"("professional_profile_id", "status");

-- CreateIndex
CREATE INDEX "gig_responses_responder_user_id_idx" ON "app"."gig_responses"("responder_user_id");

-- CreateIndex
CREATE INDEX "gig_responses_status_idx" ON "app"."gig_responses"("status");

-- CreateIndex
CREATE UNIQUE INDEX "gig_responses_gig_id_professional_profile_id_key" ON "app"."gig_responses"("gig_id", "professional_profile_id");

-- CreateIndex
CREATE UNIQUE INDEX "gig_assignments_gig_response_id_key" ON "app"."gig_assignments"("gig_response_id");

-- CreateIndex
CREATE INDEX "gig_assignments_gig_id_idx" ON "app"."gig_assignments"("gig_id");

-- CreateIndex
CREATE INDEX "gig_assignments_professional_profile_id_idx" ON "app"."gig_assignments"("professional_profile_id");

-- CreateIndex
CREATE INDEX "gig_assignments_buyer_user_id_idx" ON "app"."gig_assignments"("buyer_user_id");

-- CreateIndex
CREATE INDEX "gig_assignments_status_idx" ON "app"."gig_assignments"("status");

-- CreateIndex
CREATE INDEX "jobs_organization_id_visibility_status_idx" ON "app"."jobs"("organization_id", "visibility", "status");

-- CreateIndex
CREATE INDEX "jobs_employment_type_city_state_country_idx" ON "app"."jobs"("employment_type", "city", "state", "country");

-- CreateIndex
CREATE INDEX "jobs_domain_id_idx" ON "app"."jobs"("domain_id");

-- CreateIndex
CREATE INDEX "jobs_category_id_idx" ON "app"."jobs"("category_id");

-- CreateIndex
CREATE INDEX "job_applications_job_id_status_stage_idx" ON "app"."job_applications"("job_id", "status", "stage");

-- CreateIndex
CREATE INDEX "job_applications_candidate_profile_id_status_idx" ON "app"."job_applications"("candidate_profile_id", "status");

-- CreateIndex
CREATE UNIQUE INDEX "job_applications_job_id_candidate_profile_id_key" ON "app"."job_applications"("job_id", "candidate_profile_id");

-- CreateIndex
CREATE INDEX "job_tags_tag_id_idx" ON "app"."job_tags"("tag_id");

-- CreateIndex
CREATE INDEX "job_tags_source_idx" ON "app"."job_tags"("source");

-- CreateIndex
CREATE INDEX "job_tags_verified_idx" ON "app"."job_tags"("verified");

-- CreateIndex
CREATE UNIQUE INDEX "orders_gig_assignment_id_key" ON "app"."orders"("gig_assignment_id");

-- CreateIndex
CREATE INDEX "orders_status_idx" ON "app"."orders"("status");

-- CreateIndex
CREATE INDEX "orders_source_type_idx" ON "app"."orders"("source_type");

-- CreateIndex
CREATE INDEX "orders_offering_id_idx" ON "app"."orders"("offering_id");

-- CreateIndex
CREATE INDEX "orders_gig_assignment_id_idx" ON "app"."orders"("gig_assignment_id");

-- CreateIndex
CREATE INDEX "orders_buyer_user_id_idx" ON "app"."orders"("buyer_user_id");

-- CreateIndex
CREATE INDEX "orders_seller_professional_profile_id_idx" ON "app"."orders"("seller_professional_profile_id");

-- CreateIndex
CREATE INDEX "orders_stripe_payment_intent_id_idx" ON "app"."orders"("stripe_payment_intent_id");

-- CreateIndex
CREATE INDEX "orders_stripe_checkout_session_id_idx" ON "app"."orders"("stripe_checkout_session_id");

-- CreateIndex
CREATE INDEX "order_files_order_id_role_idx" ON "app"."order_files"("order_id", "role");

-- CreateIndex
CREATE INDEX "order_files_media_id_idx" ON "app"."order_files"("media_id");

-- CreateIndex
CREATE INDEX "order_events_order_id_created_at_idx" ON "app"."order_events"("order_id", "created_at");

-- CreateIndex
CREATE INDEX "order_events_name_idx" ON "app"."order_events"("name");

-- CreateIndex
CREATE UNIQUE INDEX "agreements_order_id_key" ON "app"."agreements"("order_id");

-- CreateIndex
CREATE UNIQUE INDEX "reviews_order_id_key" ON "app"."reviews"("order_id");

-- CreateIndex
CREATE INDEX "reviews_professional_profile_id_rating_idx" ON "app"."reviews"("professional_profile_id", "rating");

-- CreateIndex
CREATE INDEX "reviews_reviewer_user_id_idx" ON "app"."reviews"("reviewer_user_id");

-- CreateIndex
CREATE INDEX "reviews_status_idx" ON "app"."reviews"("status");

-- CreateIndex
CREATE UNIQUE INDEX "disputes_order_id_key" ON "app"."disputes"("order_id");

-- CreateIndex
CREATE INDEX "disputes_status_idx" ON "app"."disputes"("status");

-- CreateIndex
CREATE INDEX "disputes_opened_by_id_idx" ON "app"."disputes"("opened_by_id");

-- CreateIndex
CREATE INDEX "media_assets_uploaded_by_user_id_idx" ON "app"."media_assets"("uploaded_by_user_id");

-- CreateIndex
CREATE UNIQUE INDEX "media_assets_storage_key_key" ON "app"."media_assets"("storage_key");

-- CreateIndex
CREATE INDEX "gig_media_media_id_idx" ON "app"."gig_media"("media_id");

-- CreateIndex
CREATE INDEX "user_media_media_id_idx" ON "app"."user_media"("media_id");

-- CreateIndex
CREATE INDEX "professional_profile_media_media_id_idx" ON "app"."professional_profile_media"("media_id");

-- CreateIndex
CREATE INDEX "candidate_profile_media_media_id_idx" ON "app"."candidate_profile_media"("media_id");

-- CreateIndex
CREATE INDEX "organization_media_media_id_idx" ON "app"."organization_media"("media_id");

-- CreateIndex
CREATE INDEX "job_media_media_id_idx" ON "app"."job_media"("media_id");

-- CreateIndex
CREATE INDEX "availability_rules_weekday_idx" ON "app"."availability_rules"("weekday");

-- CreateIndex
CREATE INDEX "availability_rules_is_active_idx" ON "app"."availability_rules"("is_active");

-- CreateIndex
CREATE UNIQUE INDEX "availability_rules_professional_profile_id_weekday_start_ti_key" ON "app"."availability_rules"("professional_profile_id", "weekday", "start_time", "end_time");

-- CreateIndex
CREATE INDEX "calendar_connections_professional_profile_id_provider_idx" ON "app"."calendar_connections"("professional_profile_id", "provider");

-- CreateIndex
CREATE INDEX "calendar_connections_status_idx" ON "app"."calendar_connections"("status");

-- CreateIndex
CREATE INDEX "busy_windows_professional_profile_id_start_at_end_at_idx" ON "app"."busy_windows"("professional_profile_id", "start_at", "end_at");

-- CreateIndex
CREATE UNIQUE INDEX "threads_order_id_key" ON "app"."threads"("order_id");

-- CreateIndex
CREATE UNIQUE INDEX "threads_gig_id_key" ON "app"."threads"("gig_id");

-- CreateIndex
CREATE UNIQUE INDEX "threads_gig_response_id_key" ON "app"."threads"("gig_response_id");

-- CreateIndex
CREATE UNIQUE INDEX "threads_gig_assignment_id_key" ON "app"."threads"("gig_assignment_id");

-- CreateIndex
CREATE UNIQUE INDEX "threads_job_application_id_key" ON "app"."threads"("job_application_id");

-- CreateIndex
CREATE INDEX "threads_context_type_context_id_idx" ON "app"."threads"("context_type", "context_id");

-- CreateIndex
CREATE INDEX "thread_participants_user_id_idx" ON "app"."thread_participants"("user_id");

-- CreateIndex
CREATE INDEX "messages_thread_id_created_at_idx" ON "app"."messages"("thread_id", "created_at");

-- CreateIndex
CREATE INDEX "messages_sender_id_idx" ON "app"."messages"("sender_id");

-- CreateIndex
CREATE INDEX "message_media_media_id_idx" ON "app"."message_media"("media_id");

-- CreateIndex
CREATE INDEX "notifications_user_id_channel_name_idx" ON "app"."notifications"("user_id", "channel", "name");

-- CreateIndex
CREATE INDEX "notifications_organization_id_channel_name_idx" ON "app"."notifications"("organization_id", "channel", "name");

-- CreateIndex
CREATE INDEX "notifications_status_idx" ON "app"."notifications"("status");

-- CreateIndex
CREATE INDEX "search_upsert_events_entity_type_entity_id_created_at_idx" ON "app"."search_upsert_events"("entity_type", "entity_id", "created_at");

-- CreateIndex
CREATE INDEX "search_upsert_events_processed_created_at_idx" ON "app"."search_upsert_events"("processed", "created_at");

-- CreateIndex
CREATE INDEX "processed_stripe_events_type_received_at_idx" ON "app"."processed_stripe_events"("type", "received_at");

-- CreateIndex
CREATE INDEX "audit_events_actor_user_id_idx" ON "app"."audit_events"("actor_user_id");

-- CreateIndex
CREATE INDEX "audit_events_entity_type_entity_id_idx" ON "app"."audit_events"("entity_type", "entity_id");

-- CreateIndex
CREATE INDEX "audit_events_action_created_at_idx" ON "app"."audit_events"("action", "created_at");

-- AddForeignKey
ALTER TABLE "app"."user_roles" ADD CONSTRAINT "user_roles_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "app"."users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."organization_members" ADD CONSTRAINT "organization_members_organization_id_fkey" FOREIGN KEY ("organization_id") REFERENCES "app"."organizations"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."organization_members" ADD CONSTRAINT "organization_members_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "app"."users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."professional_profiles" ADD CONSTRAINT "professional_profiles_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "app"."users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."candidate_profiles" ADD CONSTRAINT "candidate_profiles_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "app"."users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."taxonomy_categories" ADD CONSTRAINT "taxonomy_categories_domain_id_fkey" FOREIGN KEY ("domain_id") REFERENCES "app"."taxonomy_domains"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."taxonomy_tags" ADD CONSTRAINT "taxonomy_tags_category_id_fkey" FOREIGN KEY ("category_id") REFERENCES "app"."taxonomy_categories"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."professional_categories" ADD CONSTRAINT "professional_categories_professional_profile_id_fkey" FOREIGN KEY ("professional_profile_id") REFERENCES "app"."professional_profiles"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."professional_categories" ADD CONSTRAINT "professional_categories_category_id_fkey" FOREIGN KEY ("category_id") REFERENCES "app"."taxonomy_categories"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."professional_tags" ADD CONSTRAINT "professional_tags_professional_profile_id_fkey" FOREIGN KEY ("professional_profile_id") REFERENCES "app"."professional_profiles"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."professional_tags" ADD CONSTRAINT "professional_tags_tag_id_fkey" FOREIGN KEY ("tag_id") REFERENCES "app"."taxonomy_tags"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."candidate_categories" ADD CONSTRAINT "candidate_categories_candidate_profile_id_fkey" FOREIGN KEY ("candidate_profile_id") REFERENCES "app"."candidate_profiles"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."candidate_categories" ADD CONSTRAINT "candidate_categories_category_id_fkey" FOREIGN KEY ("category_id") REFERENCES "app"."taxonomy_categories"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."candidate_tags" ADD CONSTRAINT "candidate_tags_candidate_profile_id_fkey" FOREIGN KEY ("candidate_profile_id") REFERENCES "app"."candidate_profiles"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."candidate_tags" ADD CONSTRAINT "candidate_tags_tag_id_fkey" FOREIGN KEY ("tag_id") REFERENCES "app"."taxonomy_tags"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."organization_categories" ADD CONSTRAINT "organization_categories_organization_id_fkey" FOREIGN KEY ("organization_id") REFERENCES "app"."organizations"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."organization_categories" ADD CONSTRAINT "organization_categories_category_id_fkey" FOREIGN KEY ("category_id") REFERENCES "app"."taxonomy_categories"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."organization_tags" ADD CONSTRAINT "organization_tags_organization_id_fkey" FOREIGN KEY ("organization_id") REFERENCES "app"."organizations"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."organization_tags" ADD CONSTRAINT "organization_tags_tag_id_fkey" FOREIGN KEY ("tag_id") REFERENCES "app"."taxonomy_tags"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."offerings" ADD CONSTRAINT "offerings_professional_profile_id_fkey" FOREIGN KEY ("professional_profile_id") REFERENCES "app"."professional_profiles"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."offerings" ADD CONSTRAINT "offerings_domain_id_fkey" FOREIGN KEY ("domain_id") REFERENCES "app"."taxonomy_domains"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."offerings" ADD CONSTRAINT "offerings_category_id_fkey" FOREIGN KEY ("category_id") REFERENCES "app"."taxonomy_categories"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."service_details" ADD CONSTRAINT "service_details_offering_id_fkey" FOREIGN KEY ("offering_id") REFERENCES "app"."offerings"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."product_details" ADD CONSTRAINT "product_details_offering_id_fkey" FOREIGN KEY ("offering_id") REFERENCES "app"."offerings"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."product_details" ADD CONSTRAINT "product_details_file_asset_id_fkey" FOREIGN KEY ("file_asset_id") REFERENCES "app"."media_assets"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."course_details" ADD CONSTRAINT "course_details_offering_id_fkey" FOREIGN KEY ("offering_id") REFERENCES "app"."offerings"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."pricing_tiers" ADD CONSTRAINT "pricing_tiers_offering_id_fkey" FOREIGN KEY ("offering_id") REFERENCES "app"."offerings"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."offering_media" ADD CONSTRAINT "offering_media_offering_id_fkey" FOREIGN KEY ("offering_id") REFERENCES "app"."offerings"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."offering_media" ADD CONSTRAINT "offering_media_media_id_fkey" FOREIGN KEY ("media_id") REFERENCES "app"."media_assets"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."offering_tags" ADD CONSTRAINT "offering_tags_offering_id_fkey" FOREIGN KEY ("offering_id") REFERENCES "app"."offerings"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."offering_tags" ADD CONSTRAINT "offering_tags_tag_id_fkey" FOREIGN KEY ("tag_id") REFERENCES "app"."taxonomy_tags"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."gigs" ADD CONSTRAINT "gigs_poster_user_id_fkey" FOREIGN KEY ("poster_user_id") REFERENCES "app"."users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."gigs" ADD CONSTRAINT "gigs_domain_id_fkey" FOREIGN KEY ("domain_id") REFERENCES "app"."taxonomy_domains"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."gigs" ADD CONSTRAINT "gigs_category_id_fkey" FOREIGN KEY ("category_id") REFERENCES "app"."taxonomy_categories"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."gig_tags" ADD CONSTRAINT "gig_tags_gig_id_fkey" FOREIGN KEY ("gig_id") REFERENCES "app"."gigs"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."gig_tags" ADD CONSTRAINT "gig_tags_tag_id_fkey" FOREIGN KEY ("tag_id") REFERENCES "app"."taxonomy_tags"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."gig_responses" ADD CONSTRAINT "gig_responses_gig_id_fkey" FOREIGN KEY ("gig_id") REFERENCES "app"."gigs"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."gig_responses" ADD CONSTRAINT "gig_responses_responder_user_id_fkey" FOREIGN KEY ("responder_user_id") REFERENCES "app"."users"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."gig_responses" ADD CONSTRAINT "gig_responses_professional_profile_id_fkey" FOREIGN KEY ("professional_profile_id") REFERENCES "app"."professional_profiles"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."gig_assignments" ADD CONSTRAINT "gig_assignments_gig_id_fkey" FOREIGN KEY ("gig_id") REFERENCES "app"."gigs"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."gig_assignments" ADD CONSTRAINT "gig_assignments_gig_response_id_fkey" FOREIGN KEY ("gig_response_id") REFERENCES "app"."gig_responses"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."gig_assignments" ADD CONSTRAINT "gig_assignments_professional_profile_id_fkey" FOREIGN KEY ("professional_profile_id") REFERENCES "app"."professional_profiles"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."jobs" ADD CONSTRAINT "jobs_organization_id_fkey" FOREIGN KEY ("organization_id") REFERENCES "app"."organizations"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."jobs" ADD CONSTRAINT "jobs_domain_id_fkey" FOREIGN KEY ("domain_id") REFERENCES "app"."taxonomy_domains"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."jobs" ADD CONSTRAINT "jobs_category_id_fkey" FOREIGN KEY ("category_id") REFERENCES "app"."taxonomy_categories"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."job_applications" ADD CONSTRAINT "job_applications_job_id_fkey" FOREIGN KEY ("job_id") REFERENCES "app"."jobs"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."job_applications" ADD CONSTRAINT "job_applications_candidate_profile_id_fkey" FOREIGN KEY ("candidate_profile_id") REFERENCES "app"."candidate_profiles"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."job_tags" ADD CONSTRAINT "job_tags_job_id_fkey" FOREIGN KEY ("job_id") REFERENCES "app"."jobs"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."job_tags" ADD CONSTRAINT "job_tags_tag_id_fkey" FOREIGN KEY ("tag_id") REFERENCES "app"."taxonomy_tags"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."orders" ADD CONSTRAINT "orders_offering_id_fkey" FOREIGN KEY ("offering_id") REFERENCES "app"."offerings"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."orders" ADD CONSTRAINT "orders_gig_assignment_id_fkey" FOREIGN KEY ("gig_assignment_id") REFERENCES "app"."gig_assignments"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."orders" ADD CONSTRAINT "orders_buyer_user_id_fkey" FOREIGN KEY ("buyer_user_id") REFERENCES "app"."users"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."orders" ADD CONSTRAINT "orders_seller_professional_profile_id_fkey" FOREIGN KEY ("seller_professional_profile_id") REFERENCES "app"."professional_profiles"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."order_files" ADD CONSTRAINT "order_files_order_id_fkey" FOREIGN KEY ("order_id") REFERENCES "app"."orders"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."order_files" ADD CONSTRAINT "order_files_media_id_fkey" FOREIGN KEY ("media_id") REFERENCES "app"."media_assets"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."order_events" ADD CONSTRAINT "order_events_order_id_fkey" FOREIGN KEY ("order_id") REFERENCES "app"."orders"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."agreements" ADD CONSTRAINT "agreements_order_id_fkey" FOREIGN KEY ("order_id") REFERENCES "app"."orders"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."agreements" ADD CONSTRAINT "agreements_pdf_media_id_fkey" FOREIGN KEY ("pdf_media_id") REFERENCES "app"."media_assets"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."reviews" ADD CONSTRAINT "reviews_order_id_fkey" FOREIGN KEY ("order_id") REFERENCES "app"."orders"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."reviews" ADD CONSTRAINT "reviews_professional_profile_id_fkey" FOREIGN KEY ("professional_profile_id") REFERENCES "app"."professional_profiles"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."disputes" ADD CONSTRAINT "disputes_order_id_fkey" FOREIGN KEY ("order_id") REFERENCES "app"."orders"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."media_assets" ADD CONSTRAINT "media_assets_uploaded_by_user_id_fkey" FOREIGN KEY ("uploaded_by_user_id") REFERENCES "app"."users"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."gig_media" ADD CONSTRAINT "gig_media_gig_id_fkey" FOREIGN KEY ("gig_id") REFERENCES "app"."gigs"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."gig_media" ADD CONSTRAINT "gig_media_media_id_fkey" FOREIGN KEY ("media_id") REFERENCES "app"."media_assets"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."user_media" ADD CONSTRAINT "user_media_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "app"."users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."user_media" ADD CONSTRAINT "user_media_media_id_fkey" FOREIGN KEY ("media_id") REFERENCES "app"."media_assets"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."professional_profile_media" ADD CONSTRAINT "professional_profile_media_professional_profile_id_fkey" FOREIGN KEY ("professional_profile_id") REFERENCES "app"."professional_profiles"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."professional_profile_media" ADD CONSTRAINT "professional_profile_media_media_id_fkey" FOREIGN KEY ("media_id") REFERENCES "app"."media_assets"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."candidate_profile_media" ADD CONSTRAINT "candidate_profile_media_candidate_profile_id_fkey" FOREIGN KEY ("candidate_profile_id") REFERENCES "app"."candidate_profiles"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."candidate_profile_media" ADD CONSTRAINT "candidate_profile_media_media_id_fkey" FOREIGN KEY ("media_id") REFERENCES "app"."media_assets"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."organization_media" ADD CONSTRAINT "organization_media_organization_id_fkey" FOREIGN KEY ("organization_id") REFERENCES "app"."organizations"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."organization_media" ADD CONSTRAINT "organization_media_media_id_fkey" FOREIGN KEY ("media_id") REFERENCES "app"."media_assets"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."job_media" ADD CONSTRAINT "job_media_job_id_fkey" FOREIGN KEY ("job_id") REFERENCES "app"."jobs"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."job_media" ADD CONSTRAINT "job_media_media_id_fkey" FOREIGN KEY ("media_id") REFERENCES "app"."media_assets"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."availability_rules" ADD CONSTRAINT "availability_rules_professional_profile_id_fkey" FOREIGN KEY ("professional_profile_id") REFERENCES "app"."professional_profiles"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."calendar_connections" ADD CONSTRAINT "calendar_connections_professional_profile_id_fkey" FOREIGN KEY ("professional_profile_id") REFERENCES "app"."professional_profiles"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."busy_windows" ADD CONSTRAINT "busy_windows_professional_profile_id_fkey" FOREIGN KEY ("professional_profile_id") REFERENCES "app"."professional_profiles"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."threads" ADD CONSTRAINT "threads_order_id_fkey" FOREIGN KEY ("order_id") REFERENCES "app"."orders"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."threads" ADD CONSTRAINT "threads_gig_id_fkey" FOREIGN KEY ("gig_id") REFERENCES "app"."gigs"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."threads" ADD CONSTRAINT "threads_gig_response_id_fkey" FOREIGN KEY ("gig_response_id") REFERENCES "app"."gig_responses"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."threads" ADD CONSTRAINT "threads_gig_assignment_id_fkey" FOREIGN KEY ("gig_assignment_id") REFERENCES "app"."gig_assignments"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."threads" ADD CONSTRAINT "threads_job_application_id_fkey" FOREIGN KEY ("job_application_id") REFERENCES "app"."job_applications"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."thread_participants" ADD CONSTRAINT "thread_participants_thread_id_fkey" FOREIGN KEY ("thread_id") REFERENCES "app"."threads"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."thread_participants" ADD CONSTRAINT "thread_participants_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "app"."users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."messages" ADD CONSTRAINT "messages_thread_id_fkey" FOREIGN KEY ("thread_id") REFERENCES "app"."threads"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."messages" ADD CONSTRAINT "messages_sender_id_fkey" FOREIGN KEY ("sender_id") REFERENCES "app"."users"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."message_media" ADD CONSTRAINT "message_media_message_id_fkey" FOREIGN KEY ("message_id") REFERENCES "app"."messages"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."message_media" ADD CONSTRAINT "message_media_media_id_fkey" FOREIGN KEY ("media_id") REFERENCES "app"."media_assets"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."notifications" ADD CONSTRAINT "notifications_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "app"."users"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "app"."notifications" ADD CONSTRAINT "notifications_organization_id_fkey" FOREIGN KEY ("organization_id") REFERENCES "app"."organizations"("id") ON DELETE SET NULL ON UPDATE CASCADE;
