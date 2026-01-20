# # Use official Python 3.9 slim image
# FROM python:3.9-slim

# # Set environment variables
# ENV PYTHONDONTWRITEBYTECODE=1 \
#     PYTHONUNBUFFERED=1 \
#     PYTHONPATH=/app \
#     PIP_NO_CACHE_DIR=1 \
#     PIP_DISABLE_PIP_VERSION_CHECK=1

# # Set work directory
# WORKDIR /app

# # Install system dependencies
# RUN apt-get update \
#     && apt-get install -y --no-install-recommends \
#         gcc \
#         python3-dev \
#         libpq-dev \
#         curl \
#     && rm -rf /var/lib/apt/lists/*

# # Copy requirements first for better caching
# COPY requirements.txt .

# # Install Python dependencies
# RUN pip install --upgrade pip \
#     && pip install -r requirements.txt

# # Copy project
# COPY . .

# # Collect static files
# RUN python manage.py collectstatic --noinput

# # Create non-root user
# RUN useradd --create-home --shell /bin/bash app \
#     && chown -R app:app /app
# USER app

# # Expose port dynamically (Render will set PORT env var)
# EXPOSE $PORT

# # Health check using dynamic port
# HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
#     CMD curl -f http://localhost:$PORT/ || exit 1

# # Run gunicorn with dynamic port binding
# CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 Expense_Tracker.wsgi:application"]



# Use official Python 3.11 slim (recommended for wheels). 3.9 works, but 3.11 builds are smoother.

# ---------------------------------------------------------------------------------------------
# FROM python:3.11-slim

# ENV PYTHONDONTWRITEBYTECODE=1 \
#     PYTHONUNBUFFERED=1 \
#     PYTHONPATH=/app \
#     PIP_NO_CACHE_DIR=1 \
#     PIP_DISABLE_PIP_VERSION_CHECK=1

# WORKDIR /app

# RUN apt-get update \
#     && apt-get install -y --no-install-recommends \
#        gcc python3-dev libpq-dev curl \
#     && rm -rf /var/lib/apt/lists/*

# # Copy requirements first for caching
# COPY requirements.txt .

# RUN pip install --upgrade pip setuptools wheel \
#     && pip install --no-cache-dir -r requirements.txt

# # Copy project
# COPY . .

# # (Optional) You can keep this; start.sh also collects static so it's redundant but harmless
# # RUN python manage.py collectstatic --noinput

# # Non-root user
# RUN useradd --create-home --shell /bin/bash app \
#     && chown -R app:app /app
# USER app

# # EXPOSE must be a literal number; Render will still pass $PORT at runtime to Gunicorn
# EXPOSE 8000

# # Healthcheck: hit the /health endpoint we added
# HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
#   CMD curl -f http://localhost:$PORT/health || exit 1

# # Use start.sh to run migrate + collectstatic + gunicorn
# CMD ["./start.sh"]


FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8000

WORKDIR /app

# System deps for psycopg and healthcheck curl
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       gcc python3-dev libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY requirements.txt .

RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Ensure start script is executable
RUN chmod +x ./start.sh

# Non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose default; Render injects $PORT
EXPOSE 8000

# Healthcheck: hit the lightweight /healthz endpoint; default to 8000 if $PORT not set
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD curl -fsS http://127.0.0.1:${PORT:-8000}/healthz || exit 1

# Entrypoint: migrations, static, then gunicorn
CMD ["./start.sh"]

# ---------------------------------------------------------------------------------------------