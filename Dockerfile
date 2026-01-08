FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --root-user-action=ignore --upgrade pip && \
    pip install --root-user-action=ignore --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY templates/ templates/

# Create data directory
RUN mkdir -p /app/data

# Environment variables
ENV CONFIG_PATH=/app/data/config.json
ENV CODES_PATH=/app/data/sent_codes.json
ENV PORT=5000

# Expose port
EXPOSE 5000

# Health check using Python instead of curl
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/')" || exit 1

# Run the application with gunicorn production server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "2", "app:app"]
