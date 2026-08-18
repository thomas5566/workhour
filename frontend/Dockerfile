FROM node:24-alpine AS build

WORKDIR /app

RUN corepack enable \
    && corepack prepare pnpm@11.19.0 --activate

# Copy dependency metadata first so source edits reuse the dependency layer.
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml .npmrc ./
RUN pnpm install --frozen-lockfile

COPY index.html vite.config.js ./
COPY public ./public
COPY src ./src

# Browser traffic remains same-origin; Nginx proxies /api to FastAPI at runtime.
RUN pnpm build

FROM nginxinc/nginx-unprivileged:1.28-alpine AS runtime

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD ["wget", "--quiet", "--tries=1", "--spider", "http://127.0.0.1:8080/healthz"]
