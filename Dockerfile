FROM python:3.11-slim-bullseye

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

ENV LDFLAGS="-L/usr/lib -L/usr/local/lib -L/usr/lib64 -L/usr/local/lib64"
ENV CFLAGS="-I/usr/include -I/usr/local/include"

RUN pip install --no-cache-dir TA-Lib

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

CMD ["python", "main.py"]