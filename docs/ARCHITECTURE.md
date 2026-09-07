# SkillSwap Architecture

## Overview

SkillSwap is a Django REST API with a React SPA, arranged as multiple loosely
coupled Django apps. Each app owns its models, serializers, views, services
(business logic), urls, admin and tests. Cross-app coupling happens through
explicit service functions (e.g. `apps.orders.services.create_order` builds the
order, creates the messaging thread, and emits a notification) rather than
importing other apps' model internals ad hoc.

```
frontend (React SPA on :5173 / nginx :8080)
        │  JSON over HTTPS (JWT Bearer)
        ▼
backend  Django REST Framework (gunicorn :8000)
   ├── apps.users          auth, OTP, JWTs
   ├── apps.profiles       profiles, skills, rating aggregates
   ├── apps.listings       listings, categories, applications
   ├── apps.orders         orders, payments, Stripe/simulation gateway
   ├── apps.messaging      per-order threads & messages
   ├── apps.notifications  in-app notifications
   ├── apps.reviews        reviews (1–5) on completed orders
   ├── apps.moderation     reports, staff actions
   └── apps.core           health check, shared validators
        │
        ▼
PostgreSQL server
```

## Configuration

- One settings module (`config/settings.py`), 12-factor style: every value is
  read from environment variables (optional `.env` at the repo root via
  `python-dotenv`). Behavior switches on `DEBUG` and companion variables.
- `config/settings.py` references `docs/ARCHITECTURE.md` (this file) for the
  rationale; static/media roots are overridable via `STATIC_ROOT`/`MEDIA_ROOT`
  so containers can write to shared volumes.
- Security op-ins when `DEBUG=False`: HSTS, secure cookies, SSL redirect via
  `X-Forwarded-Proto`, `CSRF_TRUSTED_ORIGINS`. `DJANGO_SECRET_KEY` is required.

## Domain model & flows

### Identity (`apps.users`)
Custom `User` (`AUTH_USER_MODEL = 'users.User'`) keyed by username + email;
`email_verified` gates most marketplace actions via `IsEmailVerified`.

- **Registration** → JWT pair immediately (short-lived access, rotating
  refresh, blacklist on rotate).
- **Email verification / password reset** → OTP service
  (`apps.users.services.issue_otp/verify_otp`): single outstanding hashed code
  per user/purpose, `OTP_CODE_VALIDITY_SECONDS` expiry, `OTP_MAX_ATTEMPTS`
  brute-force cap. Mail goes through Django 6 Mailers (`MAILERS`).
- **Throttling**: per-scope rate limits (`auth_login`, `auth_register`,
  `order_checkout`, `message_send`, …). Cache-backed; documented to move to
  Redis under the `redis` compose profile.

### Profiles & skills (`apps.profiles`)
`Profile` (one-to-one with `User`) carries bio, university, avatar. Skills are a
parallel one-to-many `Skill` table owned here and serialized by
`apps.profiles.serializers.SkillSerializer` (imported by listings — one
definition, no duplicate OpenAPI components). Rating aggregates
(`rating_average`, `rating_count`) come from `apps.reviews.services`
(`rating_aggregate_for_profiles` / `rating_for_profile`).

### Marketplace (`apps.listings`)
- `Listing` has `moderation_status ∈ {draft, pending, published, rejected,
  suspended, archived}` (default published), plus `is_active`/`is_archived`.
  Public search only returns published, active listings. Provider edits refresh
  moderation status.
- `Application` lifecycle: pending → accepted/rejected/withdrawn. Accepted
  applications can be turned into orders by the applicant (optionally at a
  counter-proposed price). `apply_to_listing`, `accept_application`,
  `reject_application`, `withdraw_application` live in `services.py`.

### Orders & payments (`apps.orders`)
- `Order` states: `pending_payment → paid → in_progress → completed`, with
  `cancelled` (only before payment) and `refunded` (paid/in_progress).
- `Payment` row per order tracks `gateway`, `gateway_session_id`,
  `gateway_charge_id`, status.
- **Gateway abstraction** (`apps.orders.services`): a `StripeGateway` runs when
  `STRIPE_API_KEY` is set; otherwise a `SimulationGateway` returns a mock
  session whose "URL" is the dev-only `mock-confirm` endpoint. The
  `StripeWebhookView` verifies `Stripe-Signature` and flips the order to paid on
  `checkout.session.completed`.
- Every transition emits a notification to the counterpart party.

### Messaging (`apps.messaging`)
Threads are one-to-one with orders (`Thread.order`), participants are the
order's buyer/provider. Messages carry a 2000-char body cap and read state;
unread counts are computed from the requester's profile. Staff can read any
thread but cannot post.

### Notifications (`apps.notifications`)
`notify()` service centralizes creation. `MyNotificationsView` filters to the
caller; `NotificationReadView` / `NotificationReadAllView` handle single and
bulk mark-as-read (idempotent); `NotificationUnreadCountView` powers unread
counts and is reused by messaging.

### Reviews (`apps.reviews`)
Only the buyer of a **completed** order may review, once per order. Reviews
write to `Profile.reviews_received` aggregates used by the public profile and
profile-list endpoints.

### Moderation (`apps.moderation`)
- **Reports**: any verified user may report targets of type user/listing/
  message/review (one open report per target/reporter). `ReportSerializer` also
  resolves a human-readable `target_name`.
- **Staff tools** (all behind `IsStaff`):
  - review reports → resolve/reject with admin notes, idempotence-guarded;
  - suspend/reactivate users (`is_active`), optionally logging an
    `admin_action` report;
  - approve/reject/suspend/remove listings (updates `moderation_status`,
    `is_active`, `is_archived`).

## API conventions

- Versioned namespace `/api/v1/`; every app contributes its own urls.
- Default authentication: custom `UserJWTAuthentication` (Bearer). Default
  permission: `IsAuthenticated`; public endpoints opt out explicitly.
- Default JSON renderer only; pagination via `PageNumberPagination` (page size 20).
- **OpenAPI**: drf-spectacular generates the schema (`/api/v1/schema/`) with
  Swagger UI and ReDoc views. Serializer classes and `@extend_schema`
  annotations keep the schema accurate; enrichment lives in
  `apps.users.spectacular` (registered by an import in `apps/users/__init__.py`).

## Frontend

- Stack: React 19 + Vite + TypeScript (strict), Tailwind v4, TanStack Query,
  React Hook Form + zod, axios, react-router-dom 7.
- `src/api/` holds typed API modules per domain; `client.ts` configures a
  single axios instance with the base URL (`VITE_API_URL`) and an automatic
  refresh-token interceptor (tokens in localStorage under `skillswap.tokens`).
- `src/hooks/useAuth.tsx` provides auth state; pages live under `src/pages/`
  (auth, marketplace, checkout/orders, messaging, notifications, profile,
  reports, admin `AdminDashboard`).
- Form pages validate with zod schemas that mirror backend limits.
- Vitest + Testing Library for the small unit/smoke suite (`src/utils`,
  `src/components/common`); configured in `vite.config.ts` with a jsdom setup
  file.

## Testing

- **Backend**: `pytest` + `pytest-django` using the configured PostgreSQL
  (tests create a `test_<db>` database). Tests are per-app API + service tests,
  covering lifecycle transitions, authorization edges, throttling, OTPs, the
  Stripe gateway (mocked), refunds, moderation, and schema-relevant behaviors.
  `ruff` enforces lint + format.
- **Frontend**: `oxlint`, `vitest run`, and `tsc -b && vite build`.
- **CI** (`.github/workflows/ci.yml`): postgres service container + backend
  job (ruff, pytest, schema validation) and a frontend job (lint, test, build).

## Operations

### Docker Compose
`docker-compose.yml` defines (top-level services): `db` (Postgres 16, health
gated), `backend` (migrate → collectstatic → gunicorn), `frontend`
(multi-stage Node build → nginx SPA + `/api`, `/admin` proxy + static/media
from shared volumes), and an optional `redis` service behind the `redis`
profile. `VITE_API_URL` defaults to `/api/v1` (same-origin through nginx).

### Production notes
- Set `DEBUG=False`, a strong `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`,
  proper CORS origins, and a real SMTP mailer — all through env vars.
- In production the API should sit behind a TLS-terminating reverse proxy; the
  included nginx config is oriented at local/demo orchestration.