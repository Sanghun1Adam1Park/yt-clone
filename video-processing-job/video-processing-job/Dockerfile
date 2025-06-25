# -------------------- Stage 1: Build --------------------
FROM python:3.12-slim AS builder

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
# --no-cahce-dir: do not save zipped files
# --prefix=/install download at install dir so prod. can copy easier 
# and more accurate 
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Copy project source
COPY . .

# -------------------- Stage 2: Final Image --------------------
FROM python:3.12-slim

WORKDIR /app

# Install ffmpeg runtime only (if needed at runtime)
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Copy app source code
COPY --from=builder /app /app

# Run app
CMD ["python", "app/main.py"]