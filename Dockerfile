FROM python:3.11-slim-bullseye

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    wget \
    ca-certificates \
    make \
    && rm -rf /var/lib/apt/lists/*

# Download and install TA-Lib C library
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib/ && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    cd .. && \
    rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

# Set environment variables for TA-Lib
ENV LD_LIBRARY_PATH=/usr/lib:$LD_LIBRARY_PATH
ENV TA_LIBRARY_PATH=/usr/lib
ENV TA_INCLUDE_PATH=/usr/include

# Install Python packages
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir wheel setuptools numpy==1.26.4 pandas

# Install TA-Lib Python wrapper
RUN pip install --no-cache-dir TA-Lib==0.4.24

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app/

CMD ["python", "main.py"]