FROM python:3.13-slim

# Install FFmpeg (used automatically by your 'else:' block in main.py)
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your FastAPI app (main.py, config.py, routers/, data/, static/)
COPY . .

# Run on 0.0.0.0 so Windows 11 can access the container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

