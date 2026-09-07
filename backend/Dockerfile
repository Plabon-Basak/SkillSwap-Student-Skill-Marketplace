# Syntax=docker/dockerfile:1

# Backend runtime image for SkillSwap.
#
# Installs the production dependency set (base + gunicorn) and runs the Django
# app under gunicorn. Static and media files are served by the web server
# (nginx in the compose stack) from shared volumes mounted at /static and
# /media, so collectstatic is run at startup.

FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install Python dependencies first for better layer caching.
COPY requirements/ ./requirements/
RUN pip install -r requirements/production.txt

# Application code.
COPY . .

# Render media/static paths that nginx will serve from shared volumes.
RUN mkdir -p /static /media

EXPOSE 8000

# Migrate (if possible) then collect static and run the WSGI server.
CMD ["sh", "-c", "python manage.py migrate --noinput && \
    python manage.py collectstatic --noinput && \
    gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3"]
