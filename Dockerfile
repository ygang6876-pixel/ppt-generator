FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends nodejs npm chromium fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt package.json package-lock.json ./
RUN pip install --no-cache-dir -r requirements.txt \
    && npm ci

COPY . .

ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium
ENV FLASK_ENV=production
ENV PPT_GENERATOR_HOST=0.0.0.0
ENV PPT_GENERATOR_PORT=5000

EXPOSE 5000

CMD ["python", "app.py"]
