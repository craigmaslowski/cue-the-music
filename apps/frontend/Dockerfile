FROM node:22-slim AS builder

WORKDIR /app

# Accept API URL as build arg — baked into the Vite build
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# Install dependencies (full monorepo needed for NX + Panda CSS lib resolution)
COPY package.json package-lock.json ./
RUN npm ci

# Copy full monorepo source
COPY . .

# Generate Panda CSS styled-system and build the frontend
RUN npx panda codegen --cwd apps/frontend
RUN npx nx build @cue-the-music/frontend

FROM nginx:alpine

# Copy built assets from builder
COPY --from=builder /app/apps/frontend/dist /usr/share/nginx/html

# SPA-friendly nginx config
COPY apps/frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
