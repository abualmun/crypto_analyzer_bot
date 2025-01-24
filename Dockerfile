FROM python:3.12-slim

WORKDIR /app

# Install system-level dependencies required for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies from requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt 

# Copy the rest of your application code into the container
COPY . /app/

# Set the command to run your Telegram bot
CMD ["python", "main.py"]