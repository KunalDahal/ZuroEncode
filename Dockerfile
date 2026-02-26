FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy all files
COPY run.py .
COPY src/ ./src/
COPY .env .
COPY encode_bot.session* ./

RUN mkdir -p src/bin/ffmpeg src/bin/tmp src/bin/users src/bin/logs

ENV PYTHONUNBUFFERED=1

# Use run.py as entry point
CMD ["python", "run.py"]