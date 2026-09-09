# WorkinAnts

WorkinAnts is a discovery-first professional marketplace. This repository is currently in Phase 1: foundation and project infrastructure only.

No product workflows, database models, payments, messaging, search indexing, auth flows, or dashboards are implemented in this phase.

## Phase 1 Local Setup

Create a local env file from the example and provide the required public values:

```bash
cp .env.example .env.local
```

Required variables:

```txt
NEXT_PUBLIC_APP_ENV=local
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

Allowed environments:

```txt
local
development
staging
production
```

Run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Scripts

```bash
npm run dev
npm run lint
npm run typecheck
npm run build
npm run check
```

Next.js 16 removes `next lint`, so linting uses the ESLint CLI.

## Folder Structure

```txt
/app            App Router pages, layouts, and route handlers
/components     Reusable UI components
/features       Future feature-specific modules
/integrations   Future third-party adapters
/lib            Shared application utilities
/prisma         Future Prisma schema location
/server         Server-only utilities
/types          Shared TypeScript types
```

## Environment and Secret Rule

`NEXT_PUBLIC_*` values are safe to expose to browser code. Everything else is server-only and must not be imported into Client Components or exposed through diagnostics.

Current validation fails loudly when the required Phase 1 public env vars are missing or invalid. Future integration placeholders such as Stripe, Supabase, Typesense, and Bedrock keys may appear in `.env.example`, but they are not required until the app actually uses those systems.

## Health and Debug Routes

```txt
GET /api/health
GET /api/debug/env-check
```

`/api/health` is available in all environments and returns safe service status.

`/api/debug/env-check` returns only safe diagnostics outside production. In production it returns `404`.

## Deployment Notes

Configure these variables in Vercel or any production host:

```txt
NEXT_PUBLIC_APP_ENV
NEXT_PUBLIC_APP_URL
```

Do not hardcode secrets. Supabase/Postgres will be the future source of truth, while systems such as Typesense will remain derived and rebuildable.

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
