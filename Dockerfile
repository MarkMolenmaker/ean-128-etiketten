# Stage 1: Build the frontend
FROM node:18.15-alpine as frontend-builder

WORKDIR /app

# Copy frontend files
COPY vue-frontend/package.json vue-frontend/yarn.lock ./
COPY vue-frontend .

# Install dependencies and build the frontend
RUN yarn install
RUN yarn build

# Stage 2: Build the Python FastAPI app
FROM python:3.10

WORKDIR /app

# Copy Python app files
COPY main.py .
COPY code128.ttf .
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy built frontend files from the previous stage
COPY --from=frontend-builder /app/dist /app/static

# Set the entrypoint command
ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "443"]
