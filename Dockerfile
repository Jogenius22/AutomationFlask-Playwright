FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Prevent apt from showing prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxcb1 \
    libxkbcommon0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatspi2.0-0 \
    xvfb \
    fonts-liberation \
    # Additional dependencies that may be needed
    procps \
    dbus-x11 \
    xauth \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy application code
COPY . .

# Make sure directories exist
RUN mkdir -p screenshots
RUN mkdir -p data

# Set permissions for the non-root user
RUN chmod +x initialize.py
RUN chmod +x run.py

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV FLASK_DEBUG=0
ENV PORT=8080
ENV CLOUD_ENV=true
ENV DISPLAY=:99

# Install Chrome extensions
COPY extensions /app/extensions
RUN chmod -R 755 /app/extensions

# Run as non-root user for security
RUN useradd -m appuser
RUN chown -R appuser:appuser /app
USER appuser

# Start Xvfb and the application
CMD Xvfb :99 -screen 0 1280x720x16 & gunicorn --bind :$PORT app:app --timeout 600 