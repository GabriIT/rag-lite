# ---------- 1. build stage ----------
FROM node:20-alpine AS builder
WORKDIR /app

# 1️⃣  dependencies first (layer‑cache friendly)
COPY package.json package-lock.json* ./
RUN npm ci

# 2️⃣  rest of the code
COPY tsconfig.json vite.config.ts ./
COPY tailwind.config.cjs postcss.config.cjs ./
COPY index.html index.css ./
COPY src ./src

# optional build‑time env (uncomment if you need it)
# ARG VITE_API_BASE
# ENV VITE_API_BASE=${VITE_API_BASE:-/api}

RUN npm run build    # → dist/

# ---------- 2. runtime stage ----------
FROM nginx:1.27-alpine

# replace the default vhost completely
COPY nginx.conf /etc/nginx/conf.d/default.conf

# static assets
COPY --from=builder /app/dist /usr/share/nginx/html

# nginx will stay in foreground
CMD ["nginx", "-g", "daemon off;"]
