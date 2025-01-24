FROM python:3.12-slim-bullseye
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    pkg-config \
    python3-distutils \
    wget \
    && cd /tmp \
    && wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz \
    && tar -xvzf ta-lib-0.4.0-src.tar.gz \
    && cd ta-lib/ \
    && ./configure --prefix=/usr \
    && make \
    && make install \
    && cd .. \
    && rm -rf ta-lib-0.4.0-src.tar.gz ta-lib/ \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir wheel setuptools
RUN pip install --no-cache-dir numpy==1.26.4 pandas==1.5.3 

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/
CMD ["python", "main.py"]