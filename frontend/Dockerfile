# ---------- 1. build stage ----------
FROM node:20-alpine AS builder

WORKDIR /app

# copy dependency manifests *first* to leverage layer-cache
COPY package.json package-lock.json* ./

# install exactly what package-lock.json specifies
RUN npm ci

# copy the rest of the front-end source
COPY tsconfig.json vite.config.ts ./
COPY tailwind.config.js postcss.config.js ./
COPY index.html index.css ./
COPY src ./src

# if you want the API base injected at *build* time:
# ARG VITE_API_BASE
# ENV VITE_API_BASE=${VITE_API_BASE:-/api}

# build → dist/
RUN npm run build

# ---------- 2. runtime stage ----------
FROM nginx:1.27-alpine

# recommended: make Nginx a bit more secure & quiet
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf

COPY --from=builder /app/dist /usr/share/nginx/html

# Fallback index for client-side routing (vite preview does this too)
RUN printf 'try_files $uri /index.html;\n' \
    >> /etc/nginx/conf.d/default.conf

# Dokku will set CMD itself, but it doesn’t hurt:
CMD ["nginx", "-g", "daemon off;"]
