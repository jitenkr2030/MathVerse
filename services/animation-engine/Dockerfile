FROM python:3.11-slim

# Install system dependencies for Manim
RUN apt-get update && apt-get install -y \
    build-essential \
    libcairo2-dev \
    libpango1.0-dev \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-dev \
    ffmpeg \
    latex \
    texlive-full \
    dvisvgm \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create output directory
RUN mkdir -p output

# Expose port
EXPOSE 8002

# Default command - can be overridden for specific rendering tasks
CMD ["python", "-m", "http.server", "8002"]