FROM python:3.10-slim-bullseye

WORKDIR /app

# 1. Install system and build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    python3-pip \
    python3-setuptools \
    libffi-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    gcc \
    g++ \
    wget \
    ca-certificates \
    make \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 2. Install TA-Lib from source
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib/ && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    cd .. && \
    rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

# 3. Set environment variables for TA-Lib
ENV LD_LIBRARY_PATH=/usr/lib:$LD_LIBRARY_PATH
ENV TA_LIBRARY_PATH=/usr/lib
ENV TA_INCLUDE_PATH=/usr/include

# 4. Install pip + core packages
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir wheel setuptools numpy==1.24.3 pandas

# 5. Install TA-Lib Python wrapper
RUN pip install --no-cache-dir ta-lib==0.4.24

# 6. Copy and install other dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 7. Install Playwright (if used in your app)
RUN pip install --no-cache-dir playwright && \
    playwright install --with-deps chromium

# 8. Copy your project
COPY . /app/

# 9. Set the entrypoint
CMD ["python", "main.py"]
