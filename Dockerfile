# Dockerfile for HF Spaces (Docker SDK)
# Builds React frontend and serves via FastAPI

FROM python:3.11-slim

# Install Node.js for frontend build
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Python requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend and build
COPY frontend/ ./frontend/
WORKDIR /app/frontend
# Skip Playwright browser downloads, only install production deps for build
ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
RUN npm ci --ignore-scripts && npm run build

# Back to app root
WORKDIR /app

# Copy application code
COPY api/ ./api/
COPY src/ ./src/
COPY a2a/ ./a2a/
COPY mcp-servers/ ./mcp-servers/
COPY data/ ./data/
COPY .env.example ./.env

# Create static directory and copy built frontend
RUN mkdir -p /app/static
RUN cp -r /app/frontend/dist/* /app/static/

# Expose port (HF Spaces uses 7860)
EXPOSE 7860

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Start server
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "7860"]
