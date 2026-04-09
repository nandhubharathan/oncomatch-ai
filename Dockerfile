# ──────────────────────────────────────────────────────────────────────────────
# OncoMatch-AI Professional — Dockerfile
# Purpose: Single-container deployment for any Docker-compatible cloud host
#          including Hugging Face Spaces (Docker SDK), Railway, Render, etc.
# ──────────────────────────────────────────────────────────────────────────────

FROM python:3.10-slim

# Set non-interactive environment for apt-get and conda installs
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_PORT=7860
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# ── System dependencies for RDKit build tools ────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libxrender1 \
    libxext6 \
    libglib2.0-0 \
    libsm6 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ── Create non-root user (required for Hugging Face Spaces) ──────────────────
RUN useradd -m -u 1000 appuser
WORKDIR /app

# ── Copy requirements and install Python packages ────────────────────────────
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ── Copy application source ───────────────────────────────────────────────────
COPY . .

# ── Pre-generate the dataset during image build ──────────────────────────────
RUN python data_generator.py

# ── Set permissions ───────────────────────────────────────────────────────────
RUN chown -R appuser:appuser /app
USER appuser

# ── Health check ─────────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=30s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:7860/_stcore/health || exit 1

# ── Expose port ──────────────────────────────────────────────────────────────
EXPOSE 7860

# ── Launch Streamlit app ──────────────────────────────────────────────────────
CMD ["streamlit", "run", "app.py", \
     "--server.port=7860", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--server.enableCORS=false", \
     "--server.enableXsrfProtection=false"]
