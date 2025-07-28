# Lightweight Docker image - NO RUST COMPILATION
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install only runtime dependencies (NO build tools)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Note: Using fallback implementations in signature_service.py instead of Rust wrapper
# The Rust wrapper requires compilation for the target platform

# Verify supabase installation
RUN python -c "from supabase import create_client, Client; print('Supabase package installed successfully')"

# Copy application code
COPY app/ ./app/
COPY .env .

# Create non-root user
RUN useradd --create-home --shell /bin/bash astrade && \
    chown -R astrade:astrade /app
USER astrade

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] 