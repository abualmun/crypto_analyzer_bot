FROM python:3.12-slim

WORKDIR /app

# Install essential build tools, setuptools, and wheel FIRST
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    pkg-config \
    python3-distutils \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir wheel setuptools

# Install numpy and pandas explicitly and EARLY, specifying numpy version
RUN pip install --no-cache-dir numpy==1.26.4 pandas

# Copy requirements.txt AFTER installing numpy and pandas
COPY requirements.txt .

# Install the rest of the requirements from requirements.txt, EXCLUDING numpy and pandas (to avoid re-installation and potential conflicts)
RUN pip install --no-cache-dir -r requirements.txt \
    --exclude-pkg numpy --exclude-pkg pandas

# Copy the rest of your application code
COPY . /app/

CMD ["python", "main.py"]