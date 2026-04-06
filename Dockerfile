FROM python:3.11-slim

WORKDIR /app

# تثبيت اعتمادات النظام
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libgomp1 && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY monitoring/ ./monitoring/
COPY tests/ ./tests/

# تشغيل بـ Real-Time Priority (إن أمكن)
ENV OMP_NUM_THREADS=1
ENV MKL_NUM_THREADS=1
ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "src.realtime_pipeline"]
