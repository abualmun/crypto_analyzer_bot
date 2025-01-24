FROM python:3.12-slim
WORKDIR /app

# Install essential build tools, setuptools, and wheel
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    pkg-config \
    python3-distutils \
    && rm -rf /var/lib/apt/lists/*

# Install wheel and setuptools
RUN pip install --no-cache-dir wheel setuptools

# Install numpy and pandas explicitly
RUN pip install --no-cache-dir numpy==1.26.4 pandas

# Copy requirements.txt
COPY requirements.txt .

# Install the rest of the requirements
# Make sure numpy and pandas are not in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . /app/

CMD ["python", "main.py"]