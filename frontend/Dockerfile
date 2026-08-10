# LifeSci Sentinel frontend production build, served by nginx.
#
# Build context: frontend/ directory.

# ---- Stage 1: build ----
FROM node:18-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

# Optional: bake VITE_API_URL at build time if not using the same-origin proxy.
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

# ---- Stage 2: serve with nginx ----
FROM nginx:stable-alpine AS runtime

COPY nginx.conf /etc/nginx/conf.d/default.conf

COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
