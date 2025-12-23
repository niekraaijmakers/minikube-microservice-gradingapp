FROM python:3.11-slim

WORKDIR /app

# Install curl for egress testing/debugging
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app.py .
COPY templates/ templates/
COPY static/ static/

# Environment variables
ENV SERVICE_PORT=5000
ENV STUDENT_SERVICE_URL=http://student-service:5001
ENV GRADE_SERVICE_URL=http://grade-service:5002
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

# Run with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "4", "app:app"]

