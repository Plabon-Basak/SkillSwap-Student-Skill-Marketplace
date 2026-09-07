# Syntax=docker/dockerfile:1

# Frontend image for SkillSwap.
#
# Stage 1 builds the static bundle with Node/Vite.
# Stage 2 serves it with nginx and proxies /api and /admin to the backend.

FROM node:22-alpine AS build

WORKDIR /app

# Vite inlines VITE_* variables at build time. Pass it through compose so the
# default SPA client points at the nginx proxy (/api/v1).
ARG VITE_API_URL=/api/v1
ENV VITE_API_URL=$VITE_API_URL

# Install dependencies first for better layer caching.
COPY package.json package-lock.json ./
RUN npm ci

# Application source.
COPY . .

# Skip type declaration-emit regression from old tsc, run the real build.
RUN npm run build

# --- Runtime stage ---
FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
