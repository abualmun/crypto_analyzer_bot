FROM python:3.12-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    pkg-config \
    python3-distutils \
    libta-lib-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir wheel setuptools
RUN pip install --no-cache-dir numpy==1.26.4 pandas

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/
CMD ["python", "main.py"]