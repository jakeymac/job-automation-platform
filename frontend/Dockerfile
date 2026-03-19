# Build stage
FROM node:20-alpine AS build

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm install

# Copy source
COPY . .

# Build the app
RUN npm run build

# Production stage (Nginx)
FROM nginx:alpine

# Copy built files
COPY --from=build /app/dist /usr/share/nginx/html

# 👇 ADD THIS LINE
COPY nginx.conf /etc/nginx/conf.d/default.conf
# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
