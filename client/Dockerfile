# =============================================================================
# Stage 1: Build stage - compile all assets
# =============================================================================
FROM oven/bun:1.1.43-alpine AS builder

WORKDIR /build

# Copy only files needed for dependency installation first (better caching)
COPY package.json bun.lock* ./

# Install dependencies
RUN bun install --frozen-lockfile 2>/dev/null || bun install

# Copy source files needed for build
COPY js/ ./js/
COPY css/ ./css/
COPY html/ ./html/
COPY fonts/ ./fonts/
COPY sites/ ./sites/
COPY main.styl ./
COPY config.yaml config.dev.yaml ./
COPY sites.yaml sites.dev.yaml ./
COPY names.yaml names.dev.yaml ./
COPY build.js ./

# Build argument for dev/prod mode
ARG DEV=0
ENV GLEBOORU_DEV=${DEV}

# Run the build
RUN bun build.js && \
    chmod -R a+r /var/www

# =============================================================================
# Stage 2: Production runtime - minimal nginx image
# =============================================================================
FROM nginx:1.27-alpine AS production

# Copy built assets from builder stage
COPY --from=builder /var/www /var/www

# Copy nginx config and set default backend (can be overridden at runtime)
COPY nginx.docker.conf /etc/nginx/nginx.conf
ARG BACKEND_HOST=127.0.0.1
RUN sed -i "s|__BACKEND__|${BACKEND_HOST}|g" /etc/nginx/nginx.conf && \
    mkdir -p /tmp/nginx-cache /run/nginx && \
    chmod 777 /tmp/nginx-cache

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

# =============================================================================
# Stage 3: Development runtime - full bun environment for watch mode
# =============================================================================
FROM oven/bun:1.1.43-alpine AS development

WORKDIR /opt/app

# Install nginx in alpine (much faster than debian)
RUN apk add --no-cache nginx bash && \
    mkdir -p /var/www /run/nginx /tmp/nginx-cache && \
    chmod 777 /tmp/nginx-cache

# Copy nginx config
COPY nginx.docker.conf /etc/nginx/nginx.conf

# Copy package files and install dependencies
COPY package.json bun.lock* ./
RUN bun install --frozen-lockfile 2>/dev/null || bun install

# Copy all source files
COPY . ./

# Pre-build (will be overwritten if volume mounted)
ARG DEV=1
ENV GLEBOORU_DEV=${DEV}
RUN bun build.js && \
    chmod -R a+r /var/www

COPY docker-start.sh ./
RUN chmod +x docker-start.sh

EXPOSE 80

ENTRYPOINT ["/bin/bash"]
CMD ["./docker-start.sh"]
VOLUME ["/data"]
