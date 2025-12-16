# 1. Use a specific version for stability
FROM python:3.10-slim

# 2. Prevent Python from buffering logs (important for Docker logs)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# 3. Set Working Directory
WORKDIR /app 

# 4. Install system dependencies
RUN apt-get update && apt-get install -y \ 
    build-essential \ 
    gcc \ 
    # wget is useful, but only if you use it in scripts
    && rm -rf /var/lib/apt/lists/* # 5. Leverage Docker Cache: Install requirements first
# This speeds up rebuilds if you only change code and not packages
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip wheel setuptools && \ 
    pip install --no-cache-dir -r requirements.txt 

# 6. Copy the rest of the application
COPY . .

# 7. Expose Port (Matching your FastAPI/Config defaults)
EXPOSE 8000

# 8. Gunicorn Command
# -w 4: 4 workers is a good middle ground for RAG
# --timeout 600: Good for long LLM responses
# --bind 0.0.0.0:8000: Matches EXPOSE and your config
CMD ["gunicorn", "main:app", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "-w", "4", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "600", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]

# Set the entrypoint to run Gunicorn with UvicornWorker
# CMD ["gunicorn", "main:app", "-k", "uvicorn.workers.UvicornWorker", "-w", "16", "--threads", "2", "--bind", "0.0.0.0:5000", "--access-logfile", "-", "--error-logfile", "-", "--log-level", "info", "--timeout", "600"]



