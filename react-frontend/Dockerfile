# Stage 1: Build the React Application
FROM node:18-alpine AS build

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json first to leverage Docker cache
COPY package.json package-lock.json ./

# Install dependencies cleanly
RUN npm ci

# Copy the rest of the application code
COPY . .

# Build the Vite application for production (this generates the /dist folder)
RUN npm run build

# Stage 2: Serve the application using Nginx
FROM nginx:alpine

# Copy the built assets from the 'build' stage to the Nginx HTML directory
COPY --from=build /app/dist /usr/share/nginx/html

# Copy a custom Nginx configuration file for Single Page Applications (SPAs)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Change ownership of directories so Nginx can run without root
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html && \
    chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    chown -R nginx:nginx /etc/nginx/conf.d
RUN touch /var/run/nginx.pid && \
    chown -R nginx:nginx /var/run/nginx.pid

# Switch to the non-root nginx user (built into the alpine image)
USER nginx

# Expose port 8080 (non-root users cannot bind to ports < 1024)
EXPOSE 8080

# Start Nginx when the container starts
CMD ["nginx", "-g", "daemon off;"]
