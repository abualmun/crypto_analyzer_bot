FROM python:3.11-slim-bullseye

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    wget \
    python3-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xvzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib/ && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    cd .. && \
    rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

RUN pip install --no-cache-dir wheel setuptools
RUN pip install --no-cache-dir numpy==1.26.4 pandas
COPY requirements.txt .
RUN pip install --no-cache-dir TA-Lib
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/
CMD ["python", "main.py"]