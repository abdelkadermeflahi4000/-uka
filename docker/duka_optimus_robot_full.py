FROM python:3.11-slim

WORKDIR /app

# تثبيت التبعيات
RUN apt-get update && apt-get install -y \
    libglib2.0-0 libsm6 libxext6 libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ الكود
COPY src/ ./src/
COPY viola_omega_bridge.py .
COPY duka_optimus_robot_full.py .

# إعدادات البيئة
ENV PYTHONUNBUFFERED=1
ENV OMP_NUM_THREADS=1

CMD ["python", "duka_optimus_robot_full.py"]
