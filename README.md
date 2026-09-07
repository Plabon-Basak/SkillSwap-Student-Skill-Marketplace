# SkillSwap

A student-to-student skill marketplace. Users list the skills they can teach,
discover matching services, apply, agree on a price, pay (simulated or via
Stripe), exchange messages, and rate each other on completion — all with an
admin/moderation layer on top.

## Stack

| Layer    | Technology                                                          |
| -------- | ------------------------------------------------------------------- |
| Backend  | Django 6.1, Django REST Framework, SimpleJWT, drf-spectacular, Postgres |
| Frontend | React 19, Vite 8, TypeScript, Tailwind CSS 4, TanStack Query, React Hook Form + zod |
| Infra    | Docker Compose, nginx, GitHub Actions                                |

## Repository layout

```
.
├── backend/          # Django project (apps/, config/, requirements/)
│   └── apps/
│       ├── users/          # registration, login, OTP email verify, password reset
│       ├── profiles/       # student profiles & skills
│       ├── listings/       # services, categories, applications
│       ├── orders/         # order lifecycle + payments (Stripe/simulation)
│       ├── messaging/      # per-order conversation threads
│       ├── notifications/  # in-app notifications
│       ├── reviews/        # ratings on completed orders
│       ├── moderation/     # reports & staff moderation
│       └── core/           # health check, shared validators
├── frontend/         # React SPA (src/pages, src/api, src/components…)
├── docs/             # architecture notes
├── .github/workflows/ci.yml
└── docker-compose.yml
```

## Quick start

### 1. Environment

Copy the example env file and adjust values:

```sh
cp .env.example .env
```

The backend needs PostgreSQL. Set at least `DATABASE_PASSWORD` (and a strong
`DJANGO_SECRET_KEY` for anything except local development).

### 2. Backend (Django REST API)

```sh
cd backend
python -m venv .venv                 # once
.venv\Scripts\activate               # Windows (source .venv/bin/activate on Unix)
pip install -r requirements/dev.txt
python manage.py migrate
python manage.py runserver           # http://localhost:8000
```

The API is served under `http://localhost:8000/api/v1/`. Interactive
documentation:

- OpenAPI schema: `http://localhost:8000/api/v1/schema/`
- Swagger UI: `http://localhost:8000/api/v1/schema/swagger-ui/`
- ReDoc: `http://localhost:8000/api/v1/schema/redoc/`

### 3. Frontend (React SPA)

```sh
cd frontend
npm ci
npm run dev                          # http://localhost:5173
```

The dev server proxies nothing by itself; the SPA reads `VITE_API_URL`
(default `http://localhost:8000/api/v1`) from `src/api/client.ts`.

### 4. Docker Compose (whole stack)

Requires Docker. Postgres, backend (gunicorn) and the nginx-served frontend:

```sh
cp .env.example .env
docker compose up --build
```

- Frontend + nginx proxy: `http://localhost:8080`
- Backend API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/api/v1/schema/swagger-ui/`

### 5. Payments

With no `STRIPE_API_KEY` set, orders run in **simulation mode**: checkout
returns a mock session and the dev-only `/orders/<id>/mock-confirm/` endpoint
marks an order paid. Configure `STRIPE_API_KEY`/`STRIPE_WEBHOOK_SECRET` to use
real Stripe Checkout.

## Testing & quality

```sh
# Backend — ruff + pytest (PostgreSQL required; tests use a separate DB)
cd backend
ruff check apps config
ruff format --check apps config
pytest

# Frontend — oxlint + vitest + type-check/build
cd frontend
npm run lint
npm run test
npm run build
```

Everything above also runs in CI (`.github/workflows/ci.yml`).

## Feature highlights

- **Auth**: email/password registration, OTP email verification, JWT access +
  rotating refresh tokens, throttled login/OTP endpoints.
- **Marketplace**: searchable, filterable listings; structured applications with
  optional counter-offers; accept/reject/withdraw lifecycle.
- **Orders & payments**: price agreed from proposal or listing, cancellation
  before payment, provider workspace (start/complete), refunds, Stripe
  Checkout with signature-verified webhooks.
- **Messaging**: per-order threads with unread counts.
- **Notifications & reviews**: in-app notifications for every lifecycle event;
  1–5 star reviews on completed orders with aggregated profile ratings.
- **Moderation**: users report users/listings/messages/reviews; staff resolve or
  reject reports, suspend users, and approve/reject/suspend/remove listings.

See `docs/ARCHITECTURE.md` for the detailed design.