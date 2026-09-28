FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# System libraries required by OpenCV
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libgl1 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY ["DATASET OF COW/Backend/requirements.txt", "/app/requirements.txt"]

RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r /app/requirements.txt
# Copy backend
COPY ["DATASET OF COW/Backend", "/app/DATASET OF COW/Backend"]

# Copy trained ResNet model
COPY ["DATASET OF COW/models", "/app/DATASET OF COW/models"]

# Copy trained YOLO model
COPY ["runs/detect/train-2/weights", "/app/runs/detect/train-2/weights"]

# Backend working directory
WORKDIR /app/DATASET\ OF\ COW/Backend
# Start FastAPI
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]