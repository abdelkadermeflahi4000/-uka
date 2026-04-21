# 🚀 Đuka Protocol - Multi-Stage Dockerfile
# Optimized for production with minimal image size

# ==============================================================================
# Stage 1: Builder (install dependencies)
# ==============================================================================
FROM python:3.11-slim as builder

WORKDIR /app

# Install system build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ==============================================================================
# Stage 2: Runtime (minimal production image)
# ==============================================================================
FROM python:3.11-slim as runtime

WORKDIR /app

# Install runtime system dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY src/ ./src/
COPY monitoring/ ./monitoring/
COPY tests/ ./tests/
COPY app.py app_optimus.py run_đuka.py ./

# Real-time optimization environment variables
ENV OMP_NUM_THREADS=1
ENV MKL_NUM_THREADS=1
ENV PYTHONUNBUFFERED=1
ENV CUDA_VISIBLE_DEVICES=-1

# Expose ports for API and monitoring
EXPOSE 8000 8080 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Default command: Run the real-time pipeline
CMD ["python", "-m", "src.realtime_pipeline"]

# ==============================================================================
# Alternative commands (override with docker-compose or docker run):
# - Gradio Demo: CMD ["python", "app.py"]
# - Optimus Demo: CMD ["python", "app_optimus.py"]
# - Full cycle: CMD ["python", "run_đuka.py"]
# ==============================================================================

