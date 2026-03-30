# Stage 1: Build the React Frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ .
RUN npm run build

# Stage 2: Setup the Python Backend and Static Server
FROM python:3.10-slim
WORKDIR /app

# Install Node.js to serve the compiled static frontend files alongside FastAPI
RUN apt-get update && \
    apt-get install -y nodejs npm && \
    npm install -g serve && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api/ ./api/
COPY pipeline/ ./pipeline/

# Migrate the built Vite assets from Stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Ensure base data storage directories exist
RUN mkdir -p data/raw data/cleaned data/curated logs expectations

EXPOSE 8000 5173

# Execute FastAPI in the background and bind the static node server securely
CMD ["sh", "-c", "cd api && uvicorn main:app --host 0.0.0.0 --port 8000 & serve -s ../frontend/dist -l 5173"]
