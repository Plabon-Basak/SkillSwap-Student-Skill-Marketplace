"""Generate comprehensive SkillSwap project documentation as PDF."""
from fpdf import FPDF


class ProjectDoc(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)
        self.set_margins(20, 20, 20)

    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(120, 120, 120)
            self.cell(0, 8, "SkillSwap Project Documentation", align="L")
            self.cell(0, 8, f"Page {self.page_no()}", align="R", new_x="LMARGIN", new_y="NEXT")
            self.line(20, self.get_y(), 190, self.get_y())
            self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, "Generated for SkillSwap | D:\\Projects\\SkillSwap", align="C")

    def title_page(self):
        self.add_page()
        self.ln(50)
        self.set_font("Helvetica", "B", 36)
        self.set_text_color(49, 46, 129)
        self.cell(0, 20, "SkillSwap", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 16)
        self.set_text_color(80, 80, 80)
        self.cell(0, 12, "Complete Project Documentation", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(10)
        self.set_font("Helvetica", "I", 11)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, "Student-to-Student Skill Marketplace", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(30)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(100, 100, 100)
        lines = [
            "Version: 1.0.0",
            "Path: D:\\Projects\\SkillSwap",
            "Backend: Django 6.1 + DRF 3.18 + PostgreSQL",
            "Frontend: React 19 + Vite 8 + TypeScript + Tailwind 4",
            "Generated: September 2026",
        ]
        for line in lines:
            self.cell(0, 7, line, align="C", new_x="LMARGIN", new_y="NEXT")

    def toc_page(self):
        self.add_page()
        self.section_title("Table of Contents")
        toc = [
            ("1.", "Project Overview", 3),
            ("2.", "Tech Stack", 3),
            ("3.", "Project Structure & File Map", 4),
            ("4.", "How to Run the Project", 6),
            ("5.", "Environment Variables (.env)", 8),
            ("6.", "Database Schema (All Models)", 10),
            ("7.", "Authentication System (JWT + OTP)", 15),
            ("8.", "API Routes - Complete Reference", 17),
            ("9.", "Frontend Architecture", 22),
            ("10.", "Pages & Routing (21 Pages)", 23),
            ("11.", "Components Reference", 26),
            ("12.", "State Management", 28),
            ("13.", "Business Logic & State Machines", 29),
            ("14.", "Payments (Stripe + Simulation)", 32),
            ("15.", "Messaging System", 33),
            ("16.", "Notifications System", 34),
            ("17.", "Moderation & Reports", 35),
            ("18.", "How to Edit/Modify Everything", 36),
            ("19.", "Deployment (Docker)", 42),
            ("20.", "Testing", 43),
            ("21.", "Troubleshooting", 44),
        ]
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        for num, title, page in toc:
            self.set_font("Helvetica", "B", 10)
            self.cell(10, 7, num)
            self.set_font("Helvetica", "", 10)
            self.cell(140, 7, title)
            self.set_font("Helvetica", "", 10)
            self.set_text_color(100, 100, 100)
            self.cell(0, 7, str(page), align="R", new_x="LMARGIN", new_y="NEXT")
            self.set_text_color(40, 40, 40)

    def section_title(self, title):
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(49, 46, 129)
        self.ln(4)
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(49, 46, 129)
        self.line(20, self.get_y(), 80, self.get_y())
        self.ln(4)
        self.set_text_color(40, 40, 40)

    def sub_title(self, title):
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(60, 60, 60)
        self.ln(2)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)
        self.set_text_color(40, 40, 40)

    def sub_sub_title(self, title):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(80, 80, 80)
        self.cell(0, 7, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)
        self.set_text_color(40, 40, 40)

    def body(self, text):
        self.set_font("Helvetica", "", 9)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 5, text)
        self.ln(2)

    def mono_block(self, text):
        self.set_font("Courier", "", 8)
        self.set_fill_color(245, 245, 250)
        self.set_text_color(50, 50, 50)
        x = self.get_x()
        y = self.get_y()
        lines = text.split("\n")
        h = len(lines) * 4.2 + 4
        if y + h > 275:
            self.add_page()
        self.rect(20, self.get_y(), 170, h, style="F")
        self.ln(2)
        for line in lines:
            self.cell(0, 4.2, "  " + line, new_x="LMARGIN", new_y="NEXT")
        self.ln(4)
        self.set_text_color(40, 40, 40)

    def bullet(self, text, indent=0):
        self.set_font("Helvetica", "", 9)
        x = 24 + indent
        self.set_x(x)
        self.cell(4, 5, "-")
        self.multi_cell(170 - indent, 5, text)
        self.ln(1)

    def table_header(self, cols, widths):
        self.set_font("Helvetica", "B", 8)
        self.set_fill_color(49, 46, 129)
        self.set_text_color(255, 255, 255)
        for col, w in zip(cols, widths):
            self.cell(w, 7, col, border=1, fill=True, align="C")
        self.ln()
        self.set_text_color(40, 40, 40)

    def table_row(self, cols, widths, fill=False):
        self.set_font("Helvetica", "", 8)
        if fill:
            self.set_fill_color(248, 248, 252)
        max_h = 6
        for col, w in zip(cols, widths):
            self.cell(w, max_h, str(col)[:60], border=1, fill=fill, align="L")
        self.ln()


def build():
    pdf = ProjectDoc()
    pdf.set_title("SkillSwap - Complete Project Documentation")
    pdf.set_author("SkillSwap Team")

    # ========== TITLE & TOC ==========
    pdf.title_page()
    pdf.toc_page()

    # ========== 1. PROJECT OVERVIEW ==========
    pdf.add_page()
    pdf.section_title("1. Project Overview")
    pdf.body(
        "SkillSwap is a student-to-student skill marketplace platform. "
        "It allows university students to offer and purchase skills/services "
        "from each other. Think of it as a campus-focused Fiverr/Upwork."
    )
    pdf.sub_title("Core Features")
    features = [
        "User registration with email verification (OTP codes)",
        "Student profiles with skills, bio, university info, avatar",
        "Service listings with categories, pricing, delivery time",
        "Application system (students apply to buy a service)",
        "Order management with payment (Stripe or simulation mode)",
        "Messaging threads per order (real-time chat)",
        "Star rating reviews on completed orders",
        "In-app notifications for all lifecycle events",
        "Content moderation (reports, staff suspension, listing review)",
        "Admin dashboard for staff moderation",
        "JWT authentication with token rotation and blacklisting",
        "Full REST API with OpenAPI/Swagger documentation",
    ]
    for f in features:
        pdf.bullet(f)

    pdf.sub_title("User Roles")
    pdf.bullet("Guest: Browse marketplace, view public profiles/listings")
    pdf.bullet("Student (email-verified): Create listings, apply, order, pay, message, review")
    pdf.bullet("Staff/Admin: Moderate listings, resolve reports, suspend users")

    # ========== 2. TECH STACK ==========
    pdf.add_page()
    pdf.section_title("2. Tech Stack")

    pdf.sub_title("Backend")
    cols = ["Component", "Technology", "Version"]
    widths = [45, 75, 40]
    pdf.table_header(cols, widths)
    rows = [
        ("Framework", "Django", "6.1.1"),
        ("API", "Django REST Framework", "3.18.0"),
        ("Database", "PostgreSQL (psycopg3)", "16 / 3.3.5"),
        ("Auth", "djangorestframework-simplejwt", "5.5.1"),
        ("API Docs", "drf-spectacular (OpenAPI 3)", "0.28.0"),
        ("Payments", "Stripe SDK", "15.6.1"),
        ("Images", "Pillow", "12.3.0"),
        ("CORS", "django-cors-headers", "4.9.0"),
        ("Env Vars", "python-dotenv", "1.2.3"),
        ("Server (prod)", "gunicorn", "23.0.0"),
        ("Linting", "ruff", "0.16.6"),
        ("Testing", "pytest + pytest-django", "9.1.1"),
        ("Python", "Python", "3.13"),
    ]
    for i, r in enumerate(rows):
        pdf.table_row(r, widths, fill=(i % 2 == 0))

    pdf.ln(4)
    pdf.sub_title("Frontend")
    pdf.table_header(cols, widths)
    rows = [
        ("Framework", "React", "19.x"),
        ("Build Tool", "Vite", "8.x"),
        ("Language", "TypeScript", "6.0"),
        ("Routing", "react-router-dom", "7.x"),
        ("Server State", "@tanstack/react-query", "5.x"),
        ("Forms", "react-hook-form + zod", "7.x / 3.x"),
        ("HTTP Client", "axios", "1.x"),
        ("Styling", "Tailwind CSS", "4.x"),
        ("Testing", "Vitest + Testing Library", "latest"),
        ("Linting", "oxlint", "latest"),
    ]
    for i, r in enumerate(rows):
        pdf.table_row(r, widths, fill=(i % 2 == 0))

    # ========== 3. PROJECT STRUCTURE ==========
    pdf.add_page()
    pdf.section_title("3. Project Structure & File Map")

    pdf.sub_title("Top-Level Directory")
    pdf.mono_block(
        "D:\\Projects\\SkillSwap\\\n"
        "  .env                  # Environment variables (secrets)\n"
        "  .env.example          # Template for .env\n"
        "  docker-compose.yml    # Docker orchestration\n"
        "  README.md             # Project readme\n"
        "  docs/ARCHITECTURE.md  # Architecture docs\n"
        "  .github/workflows/    # CI pipeline\n"
        "  backend/              # Django backend\n"
        "  frontend/             # React frontend"
    )

    pdf.sub_title("Backend Structure")
    pdf.mono_block(
        "backend/\n"
        "  manage.py                 # Django CLI entry point\n"
        "  pyproject.toml            # pytest + ruff config\n"
        "  Dockerfile                # Production container\n"
        "  requirements/\n"
        "    base.txt                # Runtime dependencies\n"
        "    dev.txt                 # Dev dependencies (pytest, ruff)\n"
        "    production.txt          # Production (gunicorn)\n"
        "  config/\n"
        "    settings.py             # ALL settings (single file)\n"
        "    urls.py                 # Root URL router\n"
        "    wsgi.py / asgi.py       # Server entry points\n"
        "  apps/\n"
        "    core/                   # Health check, validators\n"
        "    users/                  # User model, JWT auth, OTP\n"
        "    profiles/               # Student profiles, skills\n"
        "    listings/               # Service listings, applications\n"
        "    orders/                 # Orders, payments, Stripe\n"
        "    messaging/              # Chat threads & messages\n"
        "    notifications/          # In-app notifications\n"
        "    reviews/                # Star ratings\n"
        "    moderation/             # Reports, staff actions"
    )

    pdf.sub_title("Each Django App Contains")
    pdf.mono_block(
        "apps/<app>/\n"
        "  models.py          # Database models (tables)\n"
        "  views.py           # API endpoint handlers\n"
        "  serializers.py     # Data validation & serialization\n"
        "  services.py        # Business logic (the real logic)\n"
        "  urls.py            # URL patterns for this app\n"
        "  admin.py           # Django admin panel config\n"
        "  permissions.py     # Custom permission classes\n"
        "  tests.py or test_api.py  # Tests"
    )

    pdf.sub_title("Frontend Structure")
    pdf.mono_block(
        "frontend/\n"
        "  package.json          # Dependencies & scripts\n"
        "  vite.config.ts        # Vite build config\n"
        "  tsconfig.json         # TypeScript config\n"
        "  Dockerfile            # Multi-stage build (node->nginx)\n"
        "  nginx.conf            # Production web server config\n"
        "  src/\n"
        "    main.tsx            # App entry point & providers\n"
        "    App.tsx             # All route definitions\n"
        "    index.css           # Tailwind + custom theme\n"
        "    types/index.ts      # TypeScript type definitions\n"
        "    api/\n"
        "      client.ts         # Axios instance + interceptors\n"
        "    services/           # API service modules\n"
        "      auth.ts           # Login, register, OTP, password\n"
        "      profiles.ts       # Profile CRUD, skills\n"
        "      listings.ts       # Listings, applications\n"
        "      orders.ts         # Orders, checkout\n"
        "      messaging.ts      # Threads, messages\n"
        "      notifications.ts  # Notifications\n"
        "      reviews.ts        # Reviews\n"
        "      reports.ts        # Reports + admin moderation\n"
        "    hooks/\n"
        "      useAuth.tsx       # Auth context provider\n"
        "    routes/\n"
        "      guards.tsx        # ProtectedRoute, AdminRoute\n"
        "    pages/              # 21 page components\n"
        "    components/\n"
        "      common/           # Button, Field, Avatar, etc.\n"
        "      layout/           # Navbar, Layout\n"
        "      listings/         # ListingCard\n"
        "    lib/\n"
        "      queryClient.ts    # React Query config\n"
        "    utils/\n"
        "      format.ts         # Formatting helpers"
    )

    # ========== 4. HOW TO RUN ==========
    pdf.add_page()
    pdf.section_title("4. How to Run the Project")

    pdf.sub_title("Option A: Docker (Recommended)")
    pdf.body("This runs everything (database, backend, frontend) in containers:")
    pdf.mono_block(
        "# 1. Copy and configure environment variables\n"
        "copy .env.example .env\n"
        "# Edit .env with your settings\n\n"
        "# 2. Start everything\n"
        "docker compose up --build\n\n"
        "# 3. Access:\n"
        "#   Frontend: http://localhost:8080\n"
        "#   Backend:  http://localhost:8000\n"
        "#   API Docs: http://localhost:8000/api/v1/schema/swagger-ui/\n"
        "#   Admin:    http://localhost:8000/admin/"
    )

    pdf.sub_title("Option B: Manual (Development)")
    pdf.sub_sub_title("Prerequisites")
    pdf.bullet("Python 3.13+")
    pdf.bullet("Node.js 22+")
    pdf.bullet("PostgreSQL 16+")
    pdf.bullet("Redis (optional, for caching)")

    pdf.sub_sub_title("Backend Setup")
    pdf.mono_block(
        "# 1. Navigate to backend\n"
        "cd backend\n\n"
        "# 2. Create virtual environment\n"
        "python -m venv .venv\n"
        ".venv\\Scripts\\activate  # Windows\n"
        "# source .venv/bin/activate  # Mac/Linux\n\n"
        "# 3. Install dependencies\n"
        "pip install -r requirements/dev.txt\n\n"
        "# 4. Configure .env (in project root)\n"
        "# Set DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD\n"
        "# Set DJANGO_SECRET_KEY\n\n"
        "# 5. Create database\n"
        "psql -U postgres -c \"CREATE DATABASE skillswap_db;\"\n\n"
        "# 6. Run migrations\n"
        "python manage.py migrate\n\n"
        "# 7. Create admin user\n"
        "python manage.py createsuperuser\n\n"
        "# 8. Start backend server\n"
        "python manage.py runserver\n"
        "# Runs at http://localhost:8000"
    )

    pdf.sub_sub_title("Frontend Setup")
    pdf.mono_block(
        "# 1. Navigate to frontend\n"
        "cd frontend\n\n"
        "# 2. Install dependencies\n"
        "npm install\n\n"
        "# 3. Start dev server\n"
        "npm run dev\n"
        "# Runs at http://localhost:5173"
    )

    pdf.sub_title("Available Scripts")
    pdf.sub_sub_title("Backend (from backend/)")
    pdf.mono_block(
        "python manage.py runserver          # Dev server\n"
        "python manage.py migrate            # Apply migrations\n"
        "python manage.py makemigrations     # Create new migrations\n"
        "python manage.py createsuperuser    # Create admin\n"
        "python manage.py spectacular --validate  # Validate API schema\n"
        "pytest                             # Run tests\n"
        "ruff check .                       # Lint code\n"
        "ruff format .                      # Format code"
    )

    pdf.sub_sub_title("Frontend (from frontend/)")
    pdf.mono_block(
        "npm run dev        # Dev server (Vite)\n"
        "npm run build      # Production build\n"
        "npm run preview    # Preview production build\n"
        "npm run lint       # Run oxlint\n"
        "npx vitest         # Run tests"
    )

    # ========== 5. ENVIRONMENT VARIABLES ==========
    pdf.add_page()
    pdf.section_title("5. Environment Variables (.env)")
    pdf.body(
        "All configuration is in a single .env file at the project root. "
        "Copy .env.example to .env and edit."
    )

    cols = ["Variable", "Default", "Description"]
    widths = [55, 40, 75]
    pdf.table_header(cols, widths)
    env_vars = [
        ("DJANGO_SECRET_KEY", "(dev fallback)", "Django secret (REQUIRED in prod)"),
        ("DEBUG", "True", "Debug mode"),
        ("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1", "Comma-separated hosts"),
        ("DATABASE_NAME", "skillswap_db", "PostgreSQL database name"),
        ("DATABASE_USER", "postgres", "PostgreSQL username"),
        ("DATABASE_PASSWORD", "change-me", "PostgreSQL password"),
        ("DATABASE_HOST", "localhost", "PostgreSQL host"),
        ("DATABASE_PORT", "5432", "PostgreSQL port"),
        ("JWT_SECRET_KEY", "(uses SECRET_KEY)", "JWT signing key"),
        ("JWT_ACCESS_TOKEN_MINUTES", "30", "Access token lifetime"),
        ("JWT_REFRESH_TOKEN_DAYS", "30", "Refresh token lifetime"),
        ("CORS_ALLOWED_ORIGINS", "http://localhost:5173", "CORS origins"),
        ("EMAIL_BACKEND", "console.EmailBackend", "Email backend"),
        ("EMAIL_HOST", "(empty)", "SMTP host"),
        ("EMAIL_PORT", "587", "SMTP port"),
        ("EMAIL_HOST_USER", "(empty)", "SMTP username"),
        ("EMAIL_HOST_PASSWORD", "(empty)", "SMTP password"),
        ("DEFAULT_FROM_EMAIL", "SkillSwap <no-reply@...>", "Sender email"),
        ("OTP_CODE_VALIDITY_SECONDS", "600", "OTP validity (10 min)"),
        ("STRIPE_API_KEY", "(empty)", "Stripe key (empty=simulation)"),
        ("STRIPE_WEBHOOK_SECRET", "(empty)", "Stripe webhook secret"),
        ("STRIPE_SUCCESS_URL", "http://localhost:5173/...", "Stripe redirect"),
        ("STRIPE_CANCEL_URL", "http://localhost:5173/...", "Stripe redirect"),
        ("VITE_API_URL", "/api/v1", "Frontend API base URL"),
        ("REDIS_URL", "redis://localhost:6379/0", "Redis (optional)"),
    ]
    for i, r in enumerate(env_vars):
        pdf.table_row(r, widths, fill=(i % 2 == 0))

    pdf.ln(4)
    pdf.sub_title("Important Notes")
    pdf.bullet("When STRIPE_API_KEY is empty, the app uses SimulationGateway (mock payments)")
    pdf.bullet("When EMAIL_BACKEND is 'console', emails print to terminal (no real email)")
    pdf.bullet("DEBUG=True enables media file serving and allows all hosts")
    pdf.bullet("VITE_API_URL is read at build time for the frontend")

    # ========== 6. DATABASE SCHEMA ==========
    pdf.add_page()
    pdf.section_title("6. Database Schema (All Models)")
    pdf.body(
        "The database has 12 models across 9 Django apps. All use PostgreSQL. "
        "Migrations are in each app's migrations/ folder."
    )

    # --- User ---
    pdf.sub_title("6.1 User (apps.users)")
    pdf.body("Extends Django's AbstractUser. Custom user model.")
    cols = ["Field", "Type", "Notes"]
    widths = [45, 45, 80]
    pdf.table_header(cols, widths)
    rows = [
        ("id", "BigAutoField", "Primary key (auto)"),
        ("username", "CharField(150)", "Unique, inherited"),
        ("email", "EmailField", "Unique, used for login"),
        ("password", "CharField(128)", "Hashed, inherited"),
        ("first_name", "CharField(150)", "Inherited"),
        ("last_name", "CharField(150)", "Inherited"),
        ("email_verified", "BooleanField", "Default: False"),
        ("is_active", "BooleanField", "False = suspended"),
        ("is_staff", "BooleanField", "Admin panel access"),
        ("date_joined", "DateTimeField", "Auto-set on creation"),
    ]
    for i, r in enumerate(rows):
        pdf.table_row(r, widths, fill=(i % 2 == 0))

    # --- OneTimePassword ---
    pdf.ln(3)
    pdf.sub_title("6.2 OneTimePassword (apps.users)")
    pdf.body("Stores hashed OTP codes for email verification and password reset.")
    pdf.table_header(cols, widths)
    rows = [
        ("id", "BigAutoField", "Primary key"),
        ("user", "FK -> User", "CASCADE"),
        ("purpose", "CharField(32)", "email_verification | password_reset"),
        ("hashed_code", "CharField(128)", "make_password() hash"),
        ("expires_at", "DateTimeField", "Expiry timestamp"),
        ("attempts", "PositiveIntegerField", "Default: 0, max 5"),
        ("is_used", "BooleanField", "Default: False"),
        ("created_at", "DateTimeField", "Auto-set"),
    ]
    for i, r in enumerate(rows):
        pdf.table_row(r, widths, fill=(i % 2 == 0))
    pdf.body("Constraint: Only one active (is_used=False) OTP per user per purpose.")

    # --- Skill ---
    pdf.add_page()
    pdf.sub_title("6.3 Skill (apps.profiles)")
    pdf.body("Global skill tags that users and listings can reference.")
    pdf.table_header(cols, widths)
    rows = [
        ("id", "BigAutoField", "Primary key"),
        ("name", "CharField(80)", "Unique"),
        ("slug", "SlugField(100)", "Auto-generated from name"),
        ("created_at", "DateTimeField", "Auto-set"),
    ]
    for i, r in enumerate(rows):
        pdf.table_row(r, widths, fill=(i % 2 == 0))

    # --- Profile ---
    pdf.ln(3)
    pdf.sub_title("6.4 Profile (apps.profiles)")
    pdf.body("One-to-one with User. Contains student-specific data.")
    pdf.table_header(cols, widths)
    rows = [
        ("id", "BigAutoField", "Primary key"),
        ("user", "OneToOne -> User", "CASCADE, related_name='profile'"),
        ("avatar", "ImageField", "upload_to='avatars/', optional"),
        ("university", "CharField(150)", "Blank OK"),
        ("department", "CharField(150)", "Blank OK"),
        ("is_student", "BooleanField", "Default: True"),
        ("bio", "TextField(500)", "Blank OK"),
        ("location", "CharField(120)", "Blank OK"),
        ("experience_years", "SmallInt", "Default: 0"),
        ("skills", "M2M -> Skill", "related_name='profiles'"),
        ("is_searchable", "BooleanField", "Default: True (privacy)"),
        ("is_verified_student", "BooleanField", "Staff-only badge"),
        ("created_at", "DateTimeField", "Auto-set"),
        ("updated_at", "DateTimeField", "Auto-updated"),
    ]
    for i, r in enumerate(rows):
        pdf.table_row(r, widths, fill=(i % 2 == 0))
    pdf.body("Property: display_name returns 'First Last' or username.")

    # --- Category ---
    pdf.add_page()
    pdf.sub_title("6.5 Category (apps.listings)")
    pdf.table_header(cols, widths)
    rows = [
        ("id", "BigAutoField", "Primary key"),
        ("name", "CharField(80)", "Unique"),
        ("slug", "SlugField(100)", "Auto-generated"),
        ("description", "CharField(300)", "Blank OK"),
        ("is_active", "BooleanField", "Default: True"),
        ("created_at", "DateTimeField", "Auto-set"),
    ]
    for i, r in enumerate(rows):
        pdf.table_row(r, widths, fill=(i % 2 == 0))

    # --- Listing ---
    pdf.ln(3)
    pdf.sub_title("6.6 Listing (apps.listings)")
    pdf.body("A service/skill listing offered by a student.")
    pdf.table_header(cols, widths)
    rows = [
        ("id", "BigAutoField", "Primary key"),
        ("provider", "FK -> Profile", "CASCADE (the seller)"),
        ("category", "FK -> Category", "SET_NULL, nullable"),
        ("title", "CharField(120)", "Required"),
        ("slug", "SlugField(130)", "Unique, auto from title"),
        ("description", "TextField(2000)", "Blank OK"),
        ("price", "Decimal(8,2)", "Required"),
        ("currency", "CharField(3)", "Default: 'USD'"),
        ("delivery_time_days", "SmallInt", "Nullable"),
        ("is_remote", "BooleanField", "Default: True"),
        ("location", "CharField(120)", "Blank OK"),
        ("skills", "M2M -> Skill", "Tags for the listing"),
        ("cover_image", "ImageField", "upload_to='listings/'"),
        ("is_active", "BooleanField", "Default: True"),
        ("is_archived", "BooleanField", "Soft delete flag"),
        ("moderation_status", "CharField", "draft/pending/published/rejected/suspended/archived"),
        ("created_at", "DateTimeField", "Auto-set"),
        ("updated_at", "DateTimeField", "Auto-updated"),
    ]
    for i, r in enumerate(rows):
        pdf.table_row(r, widths, fill=(i % 2 == 0))
    pdf.body("Method: archive() sets is_active=False, is_archived=True (soft delete). Slug auto-handles collisions with -2, -3 suffixes.")

    # --- Application ---
    pdf.add_page()
    pdf.sub_title("6.7 Application (apps.listings)")
    pdf.body("A student's request to buy a listing service.")
    pdf.table_header(cols, widths)
    rows = [
        ("id", "BigAutoField", "Primary key"),
        ("listing", "FK -> Listing", "CASCADE"),
        ("applicant", "FK -> Profile", "CASCADE (the buyer)"),
        ("message", "TextField(500)", "Optional message to seller"),
        ("proposed_price", "Decimal(8,2)", "Counter-offer, nullable"),
        ("status", "CharField(12)", "pending/accepted/rejected/withdrawn"),
        ("responded_at", "DateTimeField", "Nullable"),
        ("created_at", "DateTimeField", "Auto-set"),
        ("updated_at", "DateTimeField", "Auto-updated"),
    ]
    for i, r in enumerate(rows):
        pdf.table_row(r, widths, fill=(i % 2 == 0))
    pdf.body("Constraint: Only one pending application per applicant per listing.")

    # --- Order ---
    pdf.ln(3)
    pdf.sub_title("6.8 Order (apps.orders)")
    pdf.body("Created when an application is accepted. Goes through a state machine.")
    pdf.table_header(cols, widths)
    rows = [
        ("id", "BigAutoField", "Primary key"),
        ("application", "OneToOne -> Application", "PROTECT"),
        ("buyer", "FK -> Profile", "CASCADE"),
        ("provider", "FK -> Profile", "CASCADE"),
        ("listing", "FK -> Listing", "SET_NULL, nullable"),
        ("price", "Decimal(8,2)", "Snapshot of agreed price"),
        ("currency", "CharField(3)", "Default: 'USD'"),
        ("note", "TextField(500)", "Buyer's note, optional"),
        ("status", "CharField(20)", "pending_payment/paid/in_progress/..."),
        ("paid_at", "DateTimeField", "Nullable"),
        ("started_at", "DateTimeField", "Nullable"),
        ("completed_at", "DateTimeField", "Nullable"),
        ("cancelled_at", "DateTimeField", "Nullable"),
    ]
    for i, r in enumerate(rows):
        pdf.table_row(r, widths, fill=(i % 2 == 0))

    # --- Payment ---
    pdf.add_page()
    pdf.sub_title("6.9 Payment (apps.orders)")
    pdf.table_header(cols, widths)
    rows = [
        ("id", "BigAutoField", "Primary key"),
        ("order", "OneToOne -> Order", "PROTECT"),
        ("amount", "Decimal(8,2)", "Payment amount"),
        ("currency", "CharField(3)", "Default: 'USD'"),
        ("status", "CharField(10)", "created/paid/refunded/failed"),
        ("gateway", "CharField(20)", "Default: 'stripe'"),
        ("gateway_session_id", "CharField(255)", "Stripe session ID"),
        ("gateway_charge_id", "CharField(255)", "Stripe charge ID"),
    ]
    for i, r in enumerate(rows):
        pdf.table_row(r, widths, fill=(i % 2 == 0))

    # --- Thread & Message ---
    pdf.ln(3)
    pdf.sub_title("6.10 Thread (apps.messaging)")
    pdf.body("One conversation per order, between buyer and provider.")
    pdf.table_header(cols, widths)
    rows = [
        ("id", "BigAutoField", "Primary key"),
        ("order", "OneToOne -> Order", "CASCADE"),
        ("buyer", "FK -> Profile", "CASCADE"),
        ("provider", "FK -> Profile", "CASCADE"),
        ("last_message_at", "DateTimeField", "Nullable, for sorting"),
    ]
    for i, r in enumerate(rows):
        pdf.table_row(r, widths, fill=(i % 2 == 0))

    pdf.sub_title("6.11 Message (apps.messaging)")
    pdf.table_header(cols, widths)
    rows = [
        ("id", "BigAutoField", "Primary key"),
        ("thread", "FK -> Thread", "CASCADE"),
        ("sender", "FK -> Profile", "CASCADE"),
        ("body", "TextField(2000)", "Message text"),
        ("is_read", "BooleanField", "Default: False"),
        ("read_at", "DateTimeField", "Nullable"),
    ]
    for i, r in enumerate(rows):
        pdf.table_row(r, widths, fill=(i % 2 == 0))

    # --- Notification ---
    pdf.add_page()
    pdf.sub_title("6.12 Notification (apps.notifications)")
    pdf.body("Generic in-app notifications for all lifecycle events.")
    pdf.table_header(cols, widths)
    rows = [
        ("id", "BigAutoField", "Primary key"),
        ("recipient", "FK -> User", "CASCADE"),
        ("actor", "FK -> User", "CASCADE, nullable"),
        ("verb", "CharField(64)", "e.g. new_order, order_paid"),
        ("target_type", "CharField(50)", "order, application, thread..."),
        ("target_id", "BigAutoField", "ID of the target object"),
        ("data", "JSONField", "Arbitrary payload"),
        ("is_read", "BooleanField", "Default: False"),
        ("read_at", "DateTimeField", "Nullable"),
    ]
    for i, r in enumerate(rows):
        pdf.table_row(r, widths, fill=(i % 2 == 0))

    # --- Review ---
    pdf.ln(3)
    pdf.sub_title("6.13 Review (apps.reviews)")
    pdf.body("One review per completed order, by buyer on provider.")
    pdf.table_header(cols, widths)
    rows = [
        ("id", "BigAutoField", "Primary key"),
        ("order", "OneToOne -> Order", "CASCADE"),
        ("reviewer", "FK -> Profile", "CASCADE (buyer)"),
        ("reviewee", "FK -> Profile", "CASCADE (provider)"),
        ("rating", "SmallInt", "1-5, validated"),
        ("comment", "TextField(1000)", "Optional text"),
    ]
    for i, r in enumerate(rows):
        pdf.table_row(r, widths, fill=(i % 2 == 0))

    # --- Report ---
    pdf.ln(3)
    pdf.sub_title("6.14 Report (apps.moderation)")
    pdf.body("Polymorphic reports against users, listings, messages, or reviews.")
    pdf.table_header(cols, widths)
    rows = [
        ("id", "BigAutoField", "Primary key"),
        ("reporter", "FK -> User", "CASCADE"),
        ("target_type", "CharField(16)", "user/listing/message/review"),
        ("target_id", "BigAutoField", "ID of reported object"),
        ("reason", "CharField(120)", "Short reason"),
        ("description", "TextField(2000)", "Detailed explanation"),
        ("status", "CharField(12)", "pending/reviewing/resolved/rejected"),
        ("admin_notes", "TextField(2000)", "Staff notes"),
        ("reviewed_by", "FK -> User", "SET_NULL, nullable"),
    ]
    for i, r in enumerate(rows):
        pdf.table_row(r, widths, fill=(i % 2 == 0))

    # ========== 7. AUTHENTICATION ==========
    pdf.add_page()
    pdf.section_title("7. Authentication System (JWT + OTP)")

    pdf.sub_title("7.1 JWT Token Flow")
    pdf.body(
        "The app uses JSON Web Tokens (JWT) via djangorestframework-simplejwt. "
        "Tokens are stored in the browser's localStorage under 'skillswap.tokens'."
    )
    pdf.mono_block(
        "LOGIN FLOW:\n"
        "1. User sends email/username + password to POST /api/v1/auth/login/\n"
        "2. Backend validates credentials (generic error on failure)\n"
        "3. Backend returns { access, refresh, user }\n"
        "4. Frontend stores tokens in localStorage with expiry timestamp\n"
        "5. Access token sent as 'Authorization: Bearer <token>' header\n\n"
        "TOKEN REFRESH:\n"
        "1. Access tokens expire after 30 minutes\n"
        "2. Axios interceptor detects 401 response\n"
        "3. Interceptor sends refresh token to POST /api/v1/auth/refresh/\n"
        "4. Gets new access + refresh tokens (rotation)\n"
        "5. Retries original request with new access token\n"
        "6. Old refresh token is blacklisted\n\n"
        "LOGOUT:\n"
        "1. Frontend sends refresh token to POST /api/v1/auth/logout/\n"
        "2. Backend blacklists the refresh token\n"
        "3. Frontend clears localStorage\n"
        "4. User is redirected to home page"
    )

    pdf.sub_title("7.2 Email Verification (OTP)")
    pdf.mono_block(
        "VERIFICATION FLOW:\n"
        "1. User registers -> account created, email_verified=False\n"
        "2. User requests OTP: POST /api/v1/auth/email/verification/request/\n"
        "3. Backend generates 6-digit code, hashes it, stores hash, emails code\n"
        "4. User enters code: POST /api/v1/auth/email/verification/verify/\n"
        "5. Backend verifies with constant-time check (Django's check_password)\n"
        "6. On success: email_verified=True, user can use marketplace\n\n"
        "SECURITY:\n"
        "- Only hashed OTP codes stored (bcrypt-like via make_password)\n"
        "- Max 5 verification attempts per code\n"
        "- Code expires after 10 minutes (configurable)\n"
        "- Only one active OTP per user per purpose\n"
        "- New OTP supersedes previous unused ones"
    )

    pdf.sub_title("7.3 Password Reset (OTP)")
    pdf.body(
        "Same OTP mechanism as email verification, but for password reset. "
        "Request endpoint returns 204 regardless of email existence (prevents enumeration)."
    )

    pdf.sub_title("7.4 Suspension Enforcement")
    pdf.body(
        "When a user is suspended (is_active=False), the custom JWT authentication "
        "class (UserJWTAuthentication) rejects their tokens with 'This account has been suspended.' "
        "This works even for existing valid tokens."
    )

    pdf.sub_title("7.5 Permission Classes")
    pdf.bullet("IsAuthenticated: Standard DRF (must be logged in)")
    pdf.bullet("IsEmailVerified: Must be logged in AND email_verified=True")
    pdf.bullet("IsProviderOrStaff: Only the listing owner or staff can modify")
    pdf.bullet("IsStaff: Must be logged in AND is_staff=True")
    pdf.bullet("AllowAny: No authentication required")

    # ========== 8. API ROUTES ==========
    pdf.add_page()
    pdf.section_title("8. API Routes - Complete Reference")
    pdf.body(
        "All routes are under /api/v1/. Interactive docs at "
        "/api/v1/schema/swagger-ui/ when the server is running."
    )

    pdf.sub_title("8.1 Core")
    cols2 = ["Method", "URL", "Auth", "Description"]
    w2 = [18, 65, 30, 57]
    pdf.table_header(cols2, w2)
    pdf.table_row(("GET", "/api/v1/health/", "None", "Health check"), w2)

    pdf.sub_title("8.2 Authentication")
    pdf.table_header(cols2, w2)
    auth_rows = [
        ("POST", "/auth/register/", "None", "Register new user"),
        ("POST", "/auth/login/", "None", "Login (email or username)"),
        ("POST", "/auth/refresh/", "None", "Refresh JWT token"),
        ("POST", "/auth/logout/", "Auth", "Blacklist refresh token"),
        ("GET", "/auth/me/", "Auth", "Get current user"),
        ("POST", "/auth/email/verification/request/", "Auth", "Request OTP"),
        ("POST", "/auth/email/verification/verify/", "Auth", "Verify OTP"),
        ("POST", "/auth/password-reset/request/", "None", "Request reset OTP"),
        ("POST", "/auth/password-reset/verify/", "None", "Reset password with OTP"),
    ]
    for i, r in enumerate(auth_rows):
        pdf.table_row(r, w2, fill=(i % 2 == 0))

    pdf.sub_title("8.3 Profiles")
    pdf.table_header(cols2, w2)
    prof_rows = [
        ("GET", "/profiles/me/", "Verified", "Read own profile"),
        ("POST", "/profiles/me/", "Verified", "Create own profile"),
        ("PATCH", "/profiles/me/", "Verified", "Update own profile"),
        ("GET", "/profiles/", "None", "List public profiles"),
        ("GET", "/profiles/<username>/", "None", "Public profile detail"),
        ("GET", "/skills/", "None", "Browse all skills"),
    ]
    for i, r in enumerate(prof_rows):
        pdf.table_row(r, w2, fill=(i % 2 == 0))

    pdf.sub_title("8.4 Listings")
    pdf.table_header(cols2, w2)
    list_rows = [
        ("GET", "/listings/", "None", "Search listings (many filters)"),
        ("POST", "/listings/", "Verified", "Create listing"),
        ("GET", "/listings/mine/", "Verified", "My listings"),
        ("GET", "/listings/<slug>/", "Provider", "Listing detail"),
        ("PATCH", "/listings/<slug>/", "Provider", "Update listing"),
        ("DELETE", "/listings/<slug>/", "Provider", "Archive listing"),
        ("GET", "/listings/<slug>/applications/", "Provider", "View applications"),
        ("POST", "/listings/<slug>/applications/", "Verified", "Apply to listing"),
        ("GET", "/applications/mine/", "Verified", "My applications"),
        ("GET", "/applications/<pk>/", "Verified", "Application detail"),
        ("PATCH", "/applications/<pk>/", "Verified", "Accept/reject/withdraw"),
        ("GET", "/categories/", "None", "List active categories"),
    ]
    for i, r in enumerate(list_rows):
        pdf.table_row(r, w2, fill=(i % 2 == 0))

    pdf.add_page()
    pdf.sub_title("8.5 Orders")
    pdf.table_header(cols2, w2)
    order_rows = [
        ("GET", "/orders/", "Verified", "List orders (filter by role)"),
        ("POST", "/orders/", "Verified", "Create order"),
        ("GET", "/orders/<pk>/", "Verified", "Order detail"),
        ("PATCH", "/orders/<pk>/", "Verified", "Cancel/start/complete"),
        ("POST", "/orders/<pk>/checkout/", "Verified", "Open payment session"),
        ("POST", "/orders/<pk>/mock-confirm/", "Auth", "Dev: mark as paid"),
        ("POST", "/stripe/webhook/", "None", "Stripe webhook"),
    ]
    for i, r in enumerate(order_rows):
        pdf.table_row(r, w2, fill=(i % 2 == 0))

    pdf.sub_title("8.6 Messaging")
    pdf.table_header(cols2, w2)
    msg_rows = [
        ("GET", "/threads/mine/", "Verified", "My threads"),
        ("GET", "/threads/unread-count/", "Verified", "Unread count"),
        ("GET", "/threads/<pk>/", "Verified", "Thread + mark read"),
        ("GET", "/threads/<pk>/messages/", "Verified", "Messages in thread"),
        ("POST", "/threads/<pk>/messages/", "Verified", "Send message"),
    ]
    for i, r in enumerate(msg_rows):
        pdf.table_row(r, w2, fill=(i % 2 == 0))

    pdf.sub_title("8.7 Notifications")
    pdf.table_header(cols2, w2)
    notif_rows = [
        ("GET", "/notifications/mine/", "Verified", "List notifications"),
        ("GET", "/notifications/unread-count/", "Verified", "Unread count"),
        ("POST", "/notifications/read-all/", "Verified", "Mark all read"),
        ("POST", "/notifications/<pk>/read/", "Verified", "Mark one read"),
    ]
    for i, r in enumerate(notif_rows):
        pdf.table_row(r, w2, fill=(i % 2 == 0))

    pdf.sub_title("8.8 Reviews")
    pdf.table_header(cols2, w2)
    rev_rows = [
        ("POST", "/reviews/", "Verified", "Write review"),
        ("GET", "/profiles/<username>/reviews/", "None", "Public reviews"),
    ]
    for i, r in enumerate(rev_rows):
        pdf.table_row(r, w2, fill=(i % 2 == 0))

    pdf.sub_title("8.9 Moderation")
    pdf.table_header(cols2, w2)
    mod_rows = [
        ("GET", "/reports/", "Verified", "My reports or all (staff)"),
        ("POST", "/reports/create/", "Verified", "File a report"),
        ("GET", "/reports/<pk>/", "Verified", "Report detail"),
        ("POST", "/reports/<pk>/", "Staff", "Resolve/reject report"),
        ("POST", "/moderation/users/<pk>/", "Staff", "Suspend/reactivate user"),
        ("GET", "/moderation/listings/", "Staff", "Moderation queue"),
        ("POST", "/moderation/listings/<pk>/", "Staff", "Moderate listing"),
    ]
    for i, r in enumerate(mod_rows):
        pdf.table_row(r, w2, fill=(i % 2 == 0))

    pdf.sub_title("8.10 Rate Limits (Throttling)")
    pdf.body("API endpoints are rate-limited to prevent abuse:")
    cols3 = ["Endpoint", "Limit"]
    w3 = [90, 80]
    pdf.table_header(cols3, w3)
    throttle_rows = [
        ("auth_login", "10 requests/minute"),
        ("auth_register", "5 requests/minute"),
        ("auth_otp_request", "3 requests/minute"),
        ("auth_otp_verify", "10 requests/minute"),
        ("listing_create", "10 requests/minute"),
        ("application_create", "20 requests/minute"),
        ("order_create", "20 requests/minute"),
        ("order_checkout", "10 requests/minute"),
        ("message_send", "60 requests/minute"),
        ("review_create", "10 requests/minute"),
    ]
    for i, r in enumerate(throttle_rows):
        pdf.table_row(r, w3, fill=(i % 2 == 0))

    # ========== 9. FRONTEND ARCHITECTURE ==========
    pdf.add_page()
    pdf.section_title("9. Frontend Architecture")

    pdf.sub_title("9.1 Provider Tree")
    pdf.body("The app wraps components in this order (in main.tsx):")
    pdf.mono_block(
        "StrictMode\n"
        "  -> QueryClientProvider (React Query)\n"
        "    -> BrowserRouter (React Router)\n"
        "      -> AuthProvider (Auth Context)\n"
        "        -> App (Route definitions)"
    )

    pdf.sub_title("9.2 Key Architecture Decisions")
    pdf.bullet("No component library - all UI is hand-rolled with Tailwind CSS")
    pdf.bullet("Server state via React Query (no Redux/Zustand)")
    pdf.bullet("Auth state via React Context (useAuth hook)")
    pdf.bullet("URL state via useSearchParams for shareable filters")
    pdf.bullet("Forms via react-hook-form + zod validation")
    pdf.bullet("Single Axios instance with automatic token refresh interceptor")
    pdf.bullet("Custom classNames() utility instead of clsx")

    pdf.sub_title("9.3 API Client (src/api/client.ts)")
    pdf.body(
        "Central Axios instance. Base URL from VITE_API_URL env var "
        "(default http://localhost:8000/api/v1). Handles:"
    )
    pdf.bullet("Request interceptor: attaches Bearer token if not expired")
    pdf.bullet("Response interceptor: auto-refreshes on 401, retries request")
    pdf.bullet("Deduplication: single refresh promise for concurrent requests")
    pdf.bullet("Auth expiry event: dispatches 'skillswap:auth-expired' window event")

    pdf.sub_title("9.4 Service Modules (src/services/)")
    pdf.body("Each backend app has a matching frontend service module:")
    pdf.bullet("auth.ts: register, login, logout, OTP verification, password reset")
    pdf.bullet("profiles.ts: CRUD, search, skills list")
    pdf.bullet("listings.ts: CRUD, applications, my listings")
    pdf.bullet("orders.ts: list, detail, create, transition, checkout, mock-confirm")
    pdf.bullet("messaging.ts: threads, messages, send, unread count")
    pdf.bullet("notifications.ts: list, unread count, mark read")
    pdf.bullet("reviews.ts: create, for profile")
    pdf.bullet("reports.ts: create, list, detail, review + admin moderation")

    # ========== 10. PAGES & ROUTING ==========
    pdf.add_page()
    pdf.section_title("10. Pages & Routing (21 Pages)")

    pdf.body("All routes defined in src/App.tsx. Routes wrapped in Layout (Navbar + Footer).")
    pdf.ln(2)

    cols4 = ["Path", "Page Component", "Access"]
    w4 = [55, 55, 60]
    pdf.table_header(cols4, w4)
    routes = [
        ("/", "HomePage", "Public"),
        ("/login", "LoginPage", "Public (redirect if authed)"),
        ("/register", "RegisterPage", "Public"),
        ("/forgot-password", "ForgotPasswordPage", "Public"),
        ("/reset-password", "ResetPasswordPage", "Public"),
        ("/marketplace", "MarketplacePage", "Public"),
        ("/listing/:slug", "ListingDetailPage", "Public"),
        ("/profile/:username", "PublicProfilePage", "Public"),
        ("/email-verification", "EmailVerificationPage", "Protected"),
        ("/profile", "ProfilePage", "Protected"),
        ("/profile/edit", "ProfileEditPage", "Protected"),
        ("/listings/mine", "MyListingsPage", "Protected"),
        ("/listings/new", "ListingFormPage", "Protected"),
        ("/listings/:slug/edit", "ListingFormPage", "Protected"),
        ("/listings/:slug/applications", "ListingApplicationsPage", "Protected"),
        ("/orders", "OrdersPage", "Protected"),
        ("/orders/:id", "OrderDetailPage", "Protected"),
        ("/messages", "MessagesPage", "Protected"),
        ("/messages/:threadId", "ConversationPage", "Protected"),
        ("/notifications", "NotificationsPage", "Protected"),
        ("/applications", "MyApplicationsPage", "Protected"),
        ("/reports", "ReportsPage", "Protected"),
        ("/admin", "AdminDashboard", "Admin (is_staff)"),
        ("/admin/reports", "ReportsPage (admin)", "Admin"),
        ("/admin/listings", "AdminDashboard", "Admin"),
    ]
    for i, r in enumerate(routes):
        pdf.table_row(r, w4, fill=(i % 2 == 0))

    pdf.ln(4)
    pdf.sub_title("Route Guards")
    pdf.bullet("ProtectedRoute: Redirects to /login if not authenticated; to /email-verification if email not verified")
    pdf.bullet("AdminRoute: Requires is_staff=True, otherwise redirects to /")

    pdf.sub_title("Page Details")
    pdf.sub_sub_title("HomePage")
    pdf.body("Hero banner with CTA buttons. Shows up to 8 newest listings in a grid. Feature section explaining Learn/Earn/Connect.")

    pdf.sub_sub_title("LoginPage")
    pdf.body("Form: identifier (email or username) + password. Redirects to previous page on success. Links to register and forgot password.")

    pdf.sub_sub_title("RegisterPage")
    pdf.body("Form: first_name, last_name, username (min 3), email, password (min 8), confirm_password. After registration, redirects to /login.")

    pdf.sub_sub_title("MarketplacePage")
    pdf.body("Full filter sidebar: search, category, price range, remote delivery, sort. URL-persisted filters. Paginated results (12 per page).")

    pdf.sub_sub_title("ListingDetailPage")
    pdf.body("Shows listing info, provider card with ratings, reviews. Right sidebar: price, apply form (verified users), edit button (owner), report widget.")

    pdf.sub_sub_title("ListingFormPage")
    pdf.body("Handles both create (/listings/new) and edit (/listings/:slug/edit). Fields: title, description, category, skills (comma-separated), price, currency, delivery time, remote, location, cover image.")

    pdf.add_page()
    pdf.sub_sub_title("OrderDetailPage")
    pdf.body("Full order detail with status, dates, parties. Actions: Pay (buyer), Cancel (either), Start Work (provider), Mark Delivered (provider). Review box for completed orders.")

    pdf.sub_sub_title("ConversationPage")
    pdf.body("Chat interface with polling (5-second interval). Messages shown as bubbles. Auto-scrolls to bottom on new messages.")

    pdf.sub_sub_title("ProfilePage / ProfileEditPage")
    pdf.body("View: shows all profile data, skills, links. Edit: form for all fields including avatar upload and skill tags.")

    pdf.sub_sub_title("AdminDashboard")
    pdf.body("Staff-only. Shows pending listing count, status filter, and listing moderation actions (Approve/Reject/Suspend/Remove).")

    # ========== 11. COMPONENTS ==========
    pdf.add_page()
    pdf.section_title("11. Components Reference")

    pdf.sub_title("11.1 Layout Components")
    pdf.sub_sub_title("Navbar (src/components/layout/Navbar.tsx)")
    pdf.body("Desktop: horizontal nav with Marketplace, Orders, Messages, Notifications (with unread badge), 'Sell a skill' button. Mobile: horizontal scrollable row. Shows username + logout when authenticated.")

    pdf.sub_sub_title("Layout (src/components/layout/Layout.tsx)")
    pdf.body("Renders Navbar + main container (max-w-7xl) + Outlet (child routes) + Footer.")

    pdf.sub_title("11.2 Common Components (src/components/common/)")
    pdf.sub_sub_title("Button")
    pdf.body("Variants: primary (indigo), secondary (gray), outline, danger (red), ghost. Sizes: sm, md, lg. Loading state with spinner.")

    pdf.sub_sub_title("Field / Input / Textarea / Select")
    pdf.body("Form field wrapper with label, error message (role='alert'), hint text. Input/Textarea/Select accept 'invalid' prop for red border styling.")

    pdf.sub_sub_title("Avatar")
    pdf.body("Displays image or initials. Sizes: sm, md, lg, xl. Helper mediaUrl() prefixes relative paths with API base URL.")

    pdf.sub_sub_title("Pagination")
    pdf.body("Previous/Page X of Y/Next buttons. Returns null if totalPages <= 1.")

    pdf.sub_sub_title("Stars / RatingInput")
    pdf.body("Stars: displays rating as filled star SVGs + count. RatingInput: interactive 5-star radiogroup for entering ratings.")

    pdf.sub_sub_title("Feedback Components")
    pdf.body("Card (white bordered container), PageHeader (title + subtitle + action buttons), Alert (info/success/warning/error), Spinner, LoadingState, ErrorState (with retry), EmptyState, Badge (gray/green/amber/red/blue/purple), statusColor() helper.")

    pdf.sub_title("11.3 Listing Components")
    pdf.sub_sub_title("ListingCard (src/components/listings/ListingCard.tsx)")
    pdf.body("Card with 4:3 cover image (fallback to category initial), category label, title, description preview, price, delivery time, provider name. Links to /listing/{slug}.")

    # ========== 12. STATE MANAGEMENT ==========
    pdf.add_page()
    pdf.section_title("12. State Management")

    pdf.sub_title("12.1 Server State (React Query)")
    pdf.body(
        "All API data is managed by TanStack React Query. QueryClient created in "
        "src/lib/queryClient.ts with defaults: retry=1, refetchOnWindowFocus=false, "
        "staleTime=30s."
    )
    pdf.mono_block(
        "QUERY KEY PATTERNS:\n"
        "['listings', 'featured']          - Home page listings\n"
        "['listings', 'search', {filters}] - Marketplace search\n"
        "['listings', 'mine']              - My listings\n"
        "['listing', slug]                 - Single listing detail\n"
        "['categories']                    - Category list\n"
        "['applications', slug]            - Applications for listing\n"
        "['applications', 'mine']          - My applications\n"
        "['orders', {role, page}]          - Orders list\n"
        "['order', id]                     - Single order\n"
        "['threads']                       - Message threads\n"
        "['thread', id]                    - Single thread\n"
        "['messages', threadId]            - Messages (5s poll)\n"
        "['notifications']                 - Notifications list\n"
        "['notifications', 'unread']       - Unread count (30s poll)\n"
        "['me']                            - Current user profile\n"
        "['profile', username]             - Public profile\n"
        "['reviews', 'profile', username]  - Profile reviews\n"
        "['reports', {admin, status}]      - Reports list\n"
        "['admin', 'listings', status]     - Admin listing queue"
    )

    pdf.sub_title("12.2 Auth State (React Context)")
    pdf.body("AuthProvider in src/hooks/useAuth.tsx provides:")
    pdf.bullet("user: Current user object (or null)")
    pdf.bullet("isAuthenticated: Boolean (user !== null)")
    pdf.bullet("isLoading: Boolean (checking auth on mount)")
    pdf.bullet("login(identifier, password): Stores tokens + sets user")
    pdf.bullet("logout(): Clears tokens + nulls user")
    pdf.bullet("refetchUser(): Re-fetches /auth/me/ to refresh user data")

    pdf.sub_title("12.3 Local State")
    pdf.body("Component-level useState/useForm for ephemeral UI: form values, filter inputs, toggle states, feedback messages, error states.")

    pdf.sub_title("12.4 URL State")
    pdf.body("MarketplacePage uses useSearchParams for filter state (q, category, minPrice, maxPrice, remote, sort, page) so filters are shareable/bookmarkable.")

    # ========== 13. BUSINESS LOGIC ==========
    pdf.add_page()
    pdf.section_title("13. Business Logic & State Machines")

    pdf.sub_title("13.1 Application Lifecycle")
    pdf.mono_block(
        "STATES: pending -> accepted/rejected/withdrawn\n\n"
        "FLOW:\n"
        "1. Buyer applies to listing -> status: pending\n"
        "2. Provider accepts -> status: accepted (notifies buyer)\n"
        "   OR Provider rejects -> status: rejected (notifies buyer)\n"
        "   OR Buyer withdraws -> status: withdrawn (notifies provider)\n\n"
        "RULES:\n"
        "- Cannot apply to own listing\n"
        "- Only one pending application per buyer per listing\n"
        "- Cannot apply if already accepted for this listing"
    )

    pdf.sub_title("13.2 Order Lifecycle (State Machine)")
    pdf.mono_block(
        "STATES: pending_payment -> paid -> in_progress -> completed\n"
        "        cancelled (from pending_payment)\n"
        "        refunded (from paid or in_progress)\n\n"
        "FLOW:\n"
        "1. Buyer creates order from accepted application\n"
        "   -> status: pending_payment, creates Payment + Thread\n"
        "2. Buyer pays (checkout) -> status: paid\n"
        "   (or: either party cancels -> status: cancelled)\n"
        "3. Provider starts work -> status: in_progress\n"
        "   (or: admin refunds -> status: refunded)\n"
        "4. Provider marks delivered -> status: completed\n"
        "   (or: admin refunds -> status: refunded)\n"
        "5. After completion: buyer can leave a review\n\n"
        "TRANSITIONS (service functions):\n"
        "cancel_order(order, cancelled_by) -> requires pending_payment\n"
        "mark_order_paid(order) -> requires pending_payment\n"
        "start_order(order) -> requires paid\n"
        "complete_order(order) -> requires in_progress\n"
        "refund_order(order) -> requires paid or in_progress (admin only)"
    )

    pdf.sub_title("13.3 Listing Moderation States")
    pdf.mono_block(
        "STATES: draft -> pending -> published -> rejected/suspended/archived\n\n"
        "Staff actions:\n"
        "- approve: pending -> published\n"
        "- reject: pending -> rejected\n"
        "- suspend: published -> suspended\n"
        "- remove: any -> archived"
    )

    pdf.sub_title("13.4 Notification Events")
    pdf.body("Every lifecycle transition emits notifications via the notify() service:")
    pdf.bullet("Order: created, paid, started, completed, cancelled, refunded")
    pdf.bullet("Application: accepted, rejected, withdrawn")
    pdf.bullet("Message: new_message")
    pdf.bullet("Review: new_review")
    pdf.bullet("Report: filed, resolved")
    pdf.bullet("Moderation: listing approved/rejected/suspended/removed")

    pdf.sub_title("13.5 Cross-App Communication Pattern")
    pdf.body(
        "Services only import service functions from other apps (never models directly). "
        "The notify() function is the central event bus. This keeps apps loosely coupled."
    )

    # ========== 14. PAYMENTS ==========
    pdf.add_page()
    pdf.section_title("14. Payments (Stripe + Simulation)")

    pdf.sub_title("14.1 Gateway Abstraction")
    pdf.body(
        "The orders/services.py module has a gateway() factory that returns either "
        "StripeGateway (when STRIPE_API_KEY is set) or SimulationGateway (when empty)."
    )

    pdf.sub_title("14.2 SimulationGateway (Development)")
    pdf.mono_block(
        "MODE: simulation\n"
        "1. create_checkout_session(order) returns mock session\n"
        "   -> URL points to /orders/{id}/mock-confirm/ (dev-only endpoint)\n"
        "2. Buyer clicks 'Pay now' -> frontend calls mock-confirm endpoint\n"
        "3. Order status changes to 'paid'\n\n"
        "No real money changes hands. Perfect for testing."
    )

    pdf.sub_title("14.3 StripeGateway (Production)")
    pdf.mono_block(
        "MODE: stripe\n"
        "1. create_checkout_session(order) creates real Stripe Checkout Session\n"
        "   -> Returns Stripe-hosted URL for payment\n"
        "2. Buyer redirected to Stripe, completes payment\n"
        "3. Stripe sends webhook to POST /api/v1/stripe/webhook/\n"
        "4. Webhook handler verifies Stripe-Signature header\n"
        "5. Looks up order via metadata.order_id\n"
        "6. Calls mark_order_paid(order)\n\n"
        "REQUIRES:\n"
        "- STRIPE_API_KEY (Stripe secret key)\n"
        "- STRIPE_WEBHOOK_SECRET (webhook signing secret)\n"
        "- STRIPE_SUCCESS_URL / STRIPE_CANCEL_URL (redirect URLs)"
    )

    # ========== 15. MESSAGING ==========
    pdf.section_title("15. Messaging System")
    pdf.sub_title("15.1 Thread Creation")
    pdf.body(
        "A Thread is automatically created when an Order is created (via create_thread_for_order). "
        "It's a get_or_create (idempotent) - one thread per order. "
        "Connects buyer and provider of the order."
    )

    pdf.sub_title("15.2 Message Flow")
    pdf.mono_block(
        "1. User opens conversation page (/messages/:threadId)\n"
        "2. Messages loaded, thread marked as read (mark_thread_read)\n"
        "3. Messages poll every 5 seconds (refetchInterval: 5_000)\n"
        "4. User types message, clicks Send\n"
        "5. POST /api/v1/threads/{id}/messages/ with body\n"
        "6. Backend creates Message, notifies other participant\n"
        "7. Frontend invalidates query cache, messages refresh"
    )

    pdf.sub_title("15.3 Read Status")
    pdf.body(
        "mark_thread_read() bulk-updates all messages in a thread where "
        "the current user is the recipient (sender != current user) and "
        "is_read=False. Sets is_read=True and read_at timestamp."
    )

    # ========== 16. NOTIFICATIONS ==========
    pdf.add_page()
    pdf.section_title("16. Notifications System")
    pdf.sub_title("16.1 Notification Model")
    pdf.body(
        "Generic notifications with verb (e.g. 'new_order'), target_type/target_id "
        "(polymorphic reference), actor (who triggered it), and data (JSON payload). "
        "Notifications are created by the notify() service function."
    )

    pdf.sub_title("16.2 Frontend Integration")
    pdf.bullet("Navbar polls unread count every 30 seconds")
    pdf.bullet("NotificationsPage lists all notifications with mark-as-read")
    pdf.bullet("notificationHref() maps target_type to URL (order->/orders, listing->/listing, etc.)")
    pdf.bullet("Unread notifications have highlighted background")
    pdf.bullet("Clicking a notification marks it as read and navigates to target")

    # ========== 17. MODERATION ==========
    pdf.section_title("17. Moderation & Reports")

    pdf.sub_title("17.1 Reporting")
    pdf.body(
        "Any verified user can report a user, listing, message, or review. "
        "Reports have a reason and description. Only one open report per reporter per target."
    )

    pdf.sub_title("17.2 Staff Actions")
    pdf.bullet("View all reports (filterable by status and target type)")
    pdf.bullet("Resolve or reject reports with admin notes")
    pdf.bullet("Suspend or reactivate users (sets is_active=False)")
    pdf.bullet("Moderate listings: approve, reject, suspend, or remove")
    pdf.bullet("Listing moderation queue with status filtering")

    # ========== 18. HOW TO EDIT ==========
    pdf.add_page()
    pdf.section_title("18. How to Edit/Modify Everything")

    pdf.sub_title("18.1 Adding a New Database Field")
    pdf.mono_block(
        "STEP 1: Edit the model\n"
        "  File: backend/apps/<app>/models.py\n"
        "  Add your field to the model class\n\n"
        "STEP 2: Create migration\n"
        "  Command: python manage.py makemigrations\n"
        "  This creates a new file in apps/<app>/migrations/\n\n"
        "STEP 3: Apply migration\n"
        "  Command: python manage.py migrate\n\n"
        "STEP 4: Update serializer\n"
        "  File: backend/apps/<app>/serializers.py\n"
        "  Add the field to the relevant serializer class\n\n"
        "STEP 5: Update frontend types\n"
        "  File: frontend/src/types/index.ts\n"
        "  Add the field to the TypeScript interface"
    )

    pdf.sub_title("18.2 Adding a New API Endpoint")
    pdf.mono_block(
        "STEP 1: Create the view\n"
        "  File: backend/apps/<app>/views.py\n"
        "  Add a new class-based or function-based view\n\n"
        "STEP 2: Add URL pattern\n"
        "  File: backend/apps/<app>/urls.py\n"
        "  Add: path('your-endpoint/', YourView.as_view(), name='name')\n\n"
        "STEP 3: Create/update serializer if needed\n"
        "  File: backend/apps/<app>/serializers.py\n\n"
        "STEP 4: Add to frontend service\n"
        "  File: frontend/src/services/<app>.ts\n"
        "  Add a new exported function calling client.get/post/etc.\n\n"
        "STEP 5: Use in a page/component\n"
        "  File: frontend/src/pages/<Page>.tsx\n"
        "  Use useQuery/useMutation with your new service function"
    )

    pdf.sub_title("18.3 Adding a New Frontend Page")
    pdf.mono_block(
        "STEP 1: Create the page component\n"
        "  File: frontend/src/pages/YourPage.tsx\n"
        "  Export default function YourPage() { ... }\n\n"
        "STEP 2: Add route\n"
        "  File: frontend/src/App.tsx\n"
        "  Import YourPage and add:\n"
        "  <Route path=\"/your-path\" element={<ProtectedRoute><YourPage /></ProtectedRoute>} />\n\n"
        "STEP 3: Add navigation link\n"
        "  File: frontend/src/components/layout/Navbar.tsx\n"
        "  Add a <Link> in the desktop and/or mobile nav sections"
    )

    pdf.sub_title("18.4 Adding a New Django App")
    pdf.mono_block(
        "STEP 1: Create the app\n"
        "  Command: cd backend && python manage.py startapp your_app apps.your_app\n\n"
        "STEP 2: Register in settings\n"
        "  File: backend/config/settings.py\n"
        "  Add 'apps.your_app' to INSTALLED_APPS\n\n"
        "STEP 3: Create models, views, serializers, services, urls\n"
        "  Follow the pattern of existing apps:\n"
        "  - models.py for database tables\n"
        "  - services.py for business logic\n"
        "  - serializers.py for data validation\n"
        "  - views.py for API handlers\n"
        "  - urls.py for URL patterns\n\n"
        "STEP 4: Include URLs in root router\n"
        "  File: backend/config/urls.py\n"
        "  Add: path('api/v1/', include('apps.your_app.urls'))\n\n"
        "STEP 5: Create and run migrations\n"
        "  Command: python manage.py makemigrations your_app\n"
        "  Command: python manage.py migrate"
    )

    pdf.add_page()
    pdf.sub_title("18.5 Modifying the Auth System")
    pdf.mono_block(
        "TO ADD A NEW PERMISSION:\n"
        "  File: backend/apps/<app>/permissions.py (or users/permissions.py)\n"
        "  Create a class extending BasePermission:\n"
        "    class MyPermission(BasePermission):\n"
        "        def has_permission(self, request, view):\n"
        "            return request.user.some_condition\n\n"
        "TO MODIFY JWT SETTINGS:\n"
        "  File: backend/config/settings.py\n"
        "  Edit the SIMPLE_JWT dict:\n"
        "  - ACCESS_TOKEN_LIFETIME: how long access tokens last\n"
        "  - REFRESH_TOKEN_LIFETIME: how long refresh tokens last\n"
        "  - ROTATE_REFRESH_TOKENS: issue new refresh on use\n"
        "  - BLACKLIST_AFTER_ROTATION: invalidate old refresh\n\n"
        "TO ADD A NEW AUTH ENDPOINT:\n"
        "  1. Add view in apps/users/views.py\n"
        "  2. Add URL in apps/users/urls.py\n"
        "  3. Add serializer in apps/users/serializers.py\n"
        "  4. Add service function in apps/users/services.py"
    )

    pdf.sub_title("18.6 Modifying the Payment System")
    pdf.mono_block(
        "TO ADD A NEW PAYMENT PROVIDER:\n"
        "  File: backend/apps/orders/services.py\n\n"
        "  1. Create a new gateway class:\n"
        "     class PayPalGateway:\n"
        "         mode = 'paypal'\n"
        "         def create_checkout_session(order): ...\n"
        "         def handle_webhook(request): ...\n\n"
        "  2. Update the gateway() factory function:\n"
        "     def gateway():\n"
        "         if settings.PAYPAL_CLIENT_ID:\n"
        "             return PayPalGateway()\n"
        "         elif settings.STRIPE_API_KEY:\n"
        "             return StripeGateway()\n"
        "         return SimulationGateway()\n\n"
        "  3. Add env vars in settings.py and .env.example\n"
        "  4. Add webhook URL in config/urls.py"
    )

    pdf.sub_title("18.7 Modifying the Frontend Theme")
    pdf.mono_block(
        "FILE: frontend/src/index.css\n\n"
        "The primary color palette is defined in @theme block:\n"
        "  @theme {\n"
        "    --color-primary-50: #eef2ff;\n"
        "    --color-primary-100: #e0e7ff;\n"
        "    ...\n"
        "    --color-primary-900: #312e81;\n"
        "  }\n\n"
        "To change the primary color:\n"
        "1. Go to https://tailwindcss.com/docs/customizing-colors\n"
        "2. Pick a new color palette\n"
        "3. Replace the --color-primary-* values\n"
        "4. All components using primary-* classes will update automatically"
    )

    pdf.sub_title("18.8 Adding a New Notification Type")
    pdf.mono_block(
        "1. In the relevant service function, add a notify() call:\n"
        "   from apps.notifications.services import notify\n"
        "   notify(\n"
        "       recipient=other_user,\n"
        "       verb='your_verb',\n"
        "       actor=request_user,\n"
        "       target_type='model_name',\n"
        "       target_id=obj.id,\n"
        "       data={'key': 'value'},\n"
        "   )\n\n"
        "2. In frontend NotificationsPage.tsx, add a case in notificationHref():\n"
        "   case 'your_verb': return `/target/${n.target_id}`\n\n"
        "3. Optionally add the verb to the badge color mapping in statusColor()"
    )

    pdf.sub_title("18.9 Adding a New Filter to Marketplace")
    pdf.mono_block(
        "BACKEND:\n"
        "1. File: backend/apps/listings/views.py -> ListingListCreateView\n"
        "2. Add query param parsing in get_queryset()\n"
        "3. Add .filter() call on the queryset\n\n"
        "FRONTEND:\n"
        "1. File: frontend/src/pages/MarketplacePage.tsx\n"
        "2. Add to searchParams reading\n"
        "3. Add filter UI element in the sidebar\n"
        "4. Add to the query key and API call\n"
        "5. Add to updateParams() for URL persistence"
    )

    pdf.sub_title("18.10 Common Editing Patterns")
    pdf.bullet("Changing text/labels: Edit the component in frontend/src/pages/ or components/")
    pdf.bullet("Changing API response shape: Edit serializer in backend/apps/<app>/serializers.py")
    pdf.bullet("Adding validation: Add validators to serializer fields or model clean() method")
    pdf.bullet("Changing page layout: Edit the JSX in the page component (Tailwind classes)")
    pdf.bullet("Adding admin features: Create views with IsStaff permission, add URLs")
    pdf.bullet("Changing order status flow: Edit service functions in orders/services.py")

    # ========== 19. DEPLOYMENT ==========
    pdf.add_page()
    pdf.section_title("19. Deployment (Docker)")

    pdf.sub_title("19.1 Docker Compose Services")
    pdf.mono_block(
        "docker-compose.yml defines 4 services:\n\n"
        "1. db (PostgreSQL 16 Alpine)\n"
        "   - Port: 5432\n"
        "   - Volume: postgres_data (persistent)\n"
        "   - Health check: pg_isready\n\n"
        "2. backend (Django + gunicorn)\n"
        "   - Port: 8000\n"
        "   - Depends on: db (healthy)\n"
        "   - Volumes: staticfiles, media\n\n"
        "3. frontend (React build + nginx)\n"
        "   - Port: 8080\n"
        "   - Depends on: backend\n"
        "   - Proxies /api/ and /admin/ to backend\n"
        "   - Serves static/media from shared volumes\n\n"
        "4. redis (Redis 7 Alpine) [optional]\n"
        "   - Port: 6379\n"
        "   - Profile: redis (docker compose --profile redis up)"
    )

    pdf.sub_title("19.2 Production Build")
    pdf.mono_block(
        "BACKEND DOCKERFILE:\n"
        "- Base: python:3.13-slim\n"
        "- Installs production requirements\n"
        "- CMD: migrate -> collectstatic -> gunicorn (3 workers)\n\n"
        "FRONTEND DOCKERFILE (multi-stage):\n"
        "- Build stage: Node 22, npm ci, npm run build\n"
        "- Runtime stage: nginx 1.27\n"
        "- Copies dist/ to nginx html directory\n"
        "- nginx.conf handles SPA routing + API proxying"
    )

    pdf.sub_title("19.3 CI Pipeline (.github/workflows/ci.yml)")
    pdf.body("Two parallel jobs:")
    pdf.bullet("Backend: Python 3.13, PostgreSQL service, ruff lint/format, pytest, schema validation")
    pdf.bullet("Frontend: Node 22, npm ci, oxlint, vitest, TypeScript check, Vite build")

    # ========== 20. TESTING ==========
    pdf.section_title("20. Testing")

    pdf.sub_title("20.1 Backend Tests")
    pdf.mono_block(
        "# Run all tests\n"
        "cd backend && pytest\n\n"
        "# Run specific app tests\n"
        "pytest apps/users/test_api.py\n\n"
        "# Run with verbose output\n"
        "pytest -v\n\n"
        "# Run specific test\n"
        "pytest apps/users/test_api.py::TestLogin::test_success"
    )
    pdf.body("Tests use pytest-django with a test database (automatically created and destroyed).")

    pdf.sub_title("20.2 Frontend Tests")
    pdf.mono_block(
        "# Run all tests\n"
        "cd frontend && npx vitest run\n\n"
        "# Run in watch mode\n"
        "npx vitest\n\n"
        "# Run specific test file\n"
        "npx vitest run src/utils/format.test.ts"
    )
    pdf.body("Tests use Vitest with jsdom environment and Testing Library for component tests.")

    # ========== 21. TROUBLESHOOTING ==========
    pdf.add_page()
    pdf.section_title("21. Troubleshooting")

    pdf.sub_title("Common Issues")
    pdf.sub_sub_title("Backend won't start")
    pdf.bullet("Check PostgreSQL is running: pg_isready")
    pdf.bullet("Check .env DATABASE_* variables match your PostgreSQL setup")
    pdf.bullet("Run migrations: python manage.py migrate")
    pdf.bullet("Check for port conflicts: something else on port 8000?")

    pdf.sub_sub_title("Frontend can't connect to backend")
    pdf.bullet("Ensure backend is running on port 8000")
    pdf.bullet("Check VITE_API_URL in frontend (.env or default)")
    pdf.bullet("Check CORS_ALLOWED_ORIGINS includes http://localhost:5173")
    pdf.bullet("Check browser console for CORS errors")

    pdf.sub_sub_title("Email OTP not received")
    pdf.bullet("In development, emails print to console (terminal output)")
    pdf.bullet("Check the terminal running the backend for OTP codes")
    pdf.bullet("To use real email, configure EMAIL_HOST, EMAIL_PORT, etc. in .env")

    pdf.sub_sub_title("Payment simulation not working")
    pdf.bullet("Ensure STRIPE_API_KEY is empty in .env (uses simulation mode)")
    pdf.bullet("Use the 'Pay now' button -> 'Mock confirm' in development")
    pdf.bullet("Check that /orders/<id>/mock-confirm/ endpoint is accessible")

    pdf.sub_sub_title("Database migration errors")
    pdf.mono_block(
        "# If migrations conflict:\n"
        "python manage.py makemigrations --merge\n\n"
        "# If you need to reset (DESTRUCTIVE - deletes all data):\n"
        "python manage.py migrate <app> zero\n"
        "python manage.py migrate"
    )

    pdf.sub_sub_title("Docker issues")
    pdf.mono_block(
        "# Full rebuild:\n"
        "docker compose down -v  # Removes volumes too\n"
        "docker compose up --build\n\n"
        "# View logs:\n"
        "docker compose logs backend\n"
        "docker compose logs frontend\n"
        "docker compose logs db"
    )

    pdf.sub_title("Getting Help")
    pdf.bullet("API Documentation: http://localhost:8000/api/v1/schema/swagger-ui/")
    pdf.bullet("Django Admin: http://localhost:8000/admin/")
    pdf.bullet("Architecture docs: docs/ARCHITECTURE.md")
    pdf.bullet("CI status: Check GitHub Actions tab")

    # Save
    pdf.output("D:\\Projects\\SkillSwap\\SkillSwap_Complete_Documentation.pdf")
    print("PDF generated: D:\\Projects\\SkillSwap\\SkillSwap_Complete_Documentation.pdf")
    print(f"Total pages: {pdf.page_no()}")


if __name__ == "__main__":
    build()
