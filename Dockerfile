FROM python:3.11-slim-bullseye

WORKDIR /app

# Install system-level dependencies, including TA-Lib C library and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    pkg-config \
    python3-distutils \
    libta-lib-dev \  # Install TA-Lib C library development files
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir wheel setuptools

# Install numpy and pandas explicitly and EARLY (optional, but can keep for clarity)
RUN pip install --no-cache-dir numpy==1.26.4 pandas

# Copy requirements.txt BEFORE explicit TA-Lib install (slight change in order)
COPY requirements.txt .

# Explicitly set LDFLAGS and CFLAGS before installing Python TA-Lib wrapper
ENV LDFLAGS="-L/usr/lib -L/usr/local/lib -L/usr/lib64 -L/usr/local/lib64"  # Common library paths
ENV CFLAGS="-I/usr/include -I/usr/local/include"  # Common include paths

# Install Python TA-Lib wrapper explicitly in a separate step, AFTER setting LDFLAGS and CFLAGS
RUN pip install --no-cache-dir TA-Lib

# Install the rest of the requirements from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . /app/

CMD ["python", "main.py"]