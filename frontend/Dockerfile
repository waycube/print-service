# -----------------------------
# 1️⃣ Build stage
# -----------------------------
FROM node:20-alpine AS build

WORKDIR /app

# Copy package files first (better layer caching)
COPY package.json package-lock.json ./

RUN npm install

# Copy rest of project
COPY . .

# Build the Vite app
RUN npm run build


# -----------------------------
# 2️⃣ Production stage
# -----------------------------
FROM nginx:alpine

# Remove default nginx config
RUN rm -rf /usr/share/nginx/html/*

# Copy built files from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Optional: custom nginx config for SPA routing
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]