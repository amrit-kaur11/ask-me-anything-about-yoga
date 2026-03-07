# Build stage
FROM node:18-alpine as build

WORKDIR /app

# Install dependencies (use clean install for stability)
COPY frontend/package*.json ./
RUN npm ci

# Copy source code
COPY frontend/ ./

# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
