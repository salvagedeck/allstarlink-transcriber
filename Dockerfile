# Stage 1: Build frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend . .
RUN npm run build


# Stage 2: Build iaxclient from source
FROM alpine:latest AS iaxclient-builder

RUN apk add --no-cache \
    git \
    gcc \
    musl-dev \
    make \
    autoconf \
    automake \
    libtool \
    libaudiofile-dev \
    alsa-lib-dev

# Clone and build iaxclient for AllStarLink 3.0
RUN git clone https://github.com/iaxclient/iaxclient.git /tmp/iaxclient && \
    cd /tmp/iaxclient && \
    ./configure --enable-audio --disable-video && \
    make && \
    cp iaxclient /usr/local/bin/iaxclient && \
    chmod +x /usr/local/bin/iaxclient


# Stage 3: Build runtime container (Alpine Linux)
FROM alpine:latest

# Install system dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    ffmpeg \
    curl \
    ca-certificates \
    libc6-compat \
    libsndfile \
    alsa-lib \
    gcc \
    musl-dev \
    python3-dev

# Copy pre-built iaxclient from builder stage
COPY --from=iaxclient-builder /usr/local/bin/iaxclient /usr/local/bin/iaxclient
RUN chmod +x /usr/local/bin/iaxclient

# Set up Python application
WORKDIR /app

# Copy backend files
COPY backend /app/backend
WORKDIR /app/backend

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend build artifacts
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV ALLSTARLINK_NODE=9001
ENV ALLSTARLINK_HOST=localhost
ENV ALLSTARLINK_PORT=4569
ENV ALLSTARLINK_USER=guest
ENV ALLSTARLINK_PASSWORD=guest
ENV WHISPER_MODEL=small
ENV AUDIO_CHUNK_SECONDS=10
ENV FRONTEND_PATH=/app/frontend/dist
ENV UI_THEME=dark

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/status || exit 1

# Run application
CMD ["python3", "/app/backend/main.py"]
