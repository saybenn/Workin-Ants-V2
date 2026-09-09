import "dotenv/config";
import { spawnSync } from "node:child_process";

const databaseUrl = process.env.DATABASE_URL;

if (!databaseUrl) {
  console.error("DATABASE_URL is required to run database integrity checks.");
  process.exit(1);
}

const sql = String.raw`
set search_path = app, public;

do $$
begin
  if not exists (
    select 1
    from app.professional_profiles pp
    join app.offerings o on o.professional_profile_id = pp.id
    where pp.id = '55555555-5555-4555-8555-555555555555'
  ) then
    raise exception 'Expected seed ProfessionalProfile with Offerings.';
  end if;

  if not exists (
    select 1
    from app.users u
    join app.gigs g on g.poster_user_id = u.id
    where u.id = '11111111-1111-4111-8111-111111111111'
  ) then
    raise exception 'Expected seed User with a posted Gig.';
  end if;

  if not exists (
    select 1
    from app.gigs g
    join app.gig_responses gr on gr.gig_id = g.id
    where g.id = 'dddddddd-dddd-4ddd-8ddd-dddddddddddd'
  ) then
    raise exception 'Expected seed Gig with a GigResponse.';
  end if;

  if not exists (
    select 1
    from app.gig_responses gr
    join app.gig_assignments ga on ga.gig_response_id = gr.id
    where gr.id = 'eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee'
  ) then
    raise exception 'Expected seed GigResponse connected to a GigAssignment.';
  end if;

  if not exists (
    select 1
    from app.gig_assignments ga
    join app.orders o on o.gig_assignment_id = ga.id
    where ga.id = 'ffffffff-ffff-4fff-8fff-ffffffffffff'
  ) then
    raise exception 'Expected seed GigAssignment connected to an Order.';
  end if;

  if not exists (
    select 1
    from app.organizations org
    join app.jobs j on j.organization_id = org.id
    where org.id = '77777777-7777-4777-8777-777777777777'
  ) then
    raise exception 'Expected seed Organization with a Job.';
  end if;

  if not exists (
    select 1
    from app.candidate_profiles cp
    join app.job_applications ja on ja.candidate_profile_id = cp.id
    where cp.id = '66666666-6666-4666-8666-666666666666'
  ) then
    raise exception 'Expected seed CandidateProfile with a JobApplication.';
  end if;

  if not exists (
    select 1
    from app.offerings off
    join app.orders o on o.offering_id = off.id
    where off.id = 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb1'
  ) then
    raise exception 'Expected seed Offering connected to an Order.';
  end if;

  if not exists (
    select 1 from app.offering_media where offering_id = 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb1'
  ) or not exists (
    select 1 from app.gig_media where gig_id = 'dddddddd-dddd-4ddd-8ddd-dddddddddddd'
  ) or not exists (
    select 1 from app.job_media where job_id = '12121212-1212-4121-8121-121212121212'
  ) or not exists (
    select 1 from app.user_media where user_id = '22222222-2222-4222-8222-222222222222'
  ) or not exists (
    select 1 from app.message_media where message_id = '21212121-2121-4212-8212-212121212121'
  ) then
    raise exception 'Expected media attached through explicit join tables.';
  end if;

  if not exists (select 1 from app.search_upsert_events where id = '24242424-2424-4242-8242-242424242424') then
    raise exception 'Expected SearchUpsertEvent shell record.';
  end if;

  if not exists (select 1 from app.processed_stripe_events where event_id = 'evt_seed_phase_2') then
    raise exception 'Expected ProcessedStripeEvent shell record.';
  end if;

  if not exists (select 1 from app.audit_events where id = '25252525-2525-4252-8252-252525252525') then
    raise exception 'Expected AuditEvent shell record.';
  end if;
end $$;

do $$
begin
  if exists (
    select 1
    from information_schema.columns
    where table_schema = 'app'
      and table_name = 'offerings'
      and column_name in ('user_id', 'organization_id', 'seller_org_id')
  ) then
    raise exception 'Offerings must not include User-owned or Organization-owned seller columns.';
  end if;

  if exists (
    select 1
    from information_schema.tables
    where table_schema = 'app'
      and table_name = 'gig_details'
  ) then
    raise exception 'GigDetails table must not exist.';
  end if;

  if exists (
    select 1
    from information_schema.columns
    where table_schema = 'app'
      and table_name = 'media_assets'
      and column_name in ('owner_type', 'owner_id', 'owner_user_id')
  ) then
    raise exception 'MediaAsset must not use polymorphic owner columns.';
  end if;

  if exists (
    select 1
    from information_schema.columns
    where table_schema = 'app'
      and table_name = 'orders'
      and column_name = 'seller_org_id'
  ) then
    raise exception 'Orders must not include seller_org_id.';
  end if;
end $$;

do $$
begin
  begin
    insert into app.gig_responses (
      id,
      gig_id,
      responder_user_id,
      professional_profile_id,
      message,
      proposed_cents,
      currency,
      estimated_days,
      status,
      updated_at
    ) values (
      '30303030-3030-4303-8303-303030303030',
      'dddddddd-dddd-4ddd-8ddd-dddddddddddd',
      '22222222-2222-4222-8222-222222222222',
      '55555555-5555-4555-8555-555555555555',
      'Duplicate response should fail.',
      75000,
      'usd',
      7,
      'submitted',
      now()
    );
    raise exception 'Duplicate GigResponse unexpectedly succeeded.';
  exception
    when unique_violation then
      null;
  end;

  begin
    insert into app.job_applications (
      id,
      job_id,
      candidate_profile_id,
      resume_url,
      cover_letter,
      status,
      stage
    ) values (
      '31313131-3131-4313-8313-313131313131',
      '12121212-1212-4121-8121-121212121212',
      '66666666-6666-4666-8666-666666666666',
      'https://example.com/duplicate.pdf',
      'Duplicate application should fail.',
      'submitted',
      'new_'
    );
    raise exception 'Duplicate JobApplication unexpectedly succeeded.';
  exception
    when unique_violation then
      null;
  end;

  begin
    insert into app.offerings (
      id,
      kind,
      slug,
      title,
      status,
      professional_profile_id,
      domain_id,
      category_id,
      price_from_cents,
      currency,
      updated_at
    ) values (
      '32323232-3232-4323-8323-323232323232',
      'service',
      'seed-logo-design-service',
      'Duplicate slug should fail',
      'draft',
      '55555555-5555-4555-8555-555555555555',
      '88888888-8888-4888-8888-888888888801',
      '99999999-9999-4999-8999-999999999901',
      1000,
      'usd',
      now()
    );
    raise exception 'Duplicate Offering slug unexpectedly succeeded.';
  exception
    when unique_violation then
      null;
  end;
end $$;

select 'Phase 2 database integrity checks passed.' as result;
`;

const result = spawnSync("psql", [databaseUrl, "-v", "ON_ERROR_STOP=1"], {
  input: sql,
  stdio: ["pipe", "pipe", "pipe"],
  encoding: "utf8",
  env: {
    ...process.env,
    PGSSLMODE: process.env.PGSSLMODE ?? "require",
  },
});

if (result.status !== 0) {
  console.error("Phase 2 database integrity checks failed.");
  if (result.stdout) {
    console.error(result.stdout);
  }
  if (result.stderr) {
    console.error(result.stderr);
  }
  process.exit(result.status ?? 1);
}

console.info(result.stdout.trim());
