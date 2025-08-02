# syntax=docker/dockerfile:1
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Rust (needed for some Python dependencies)
RUN curl https://sh.rustup.rs -sSf | bash -s -- -y --profile minimal && \
    export PATH="$PATH:/root/.cargo/bin" && \
    rustc --version && cargo --version

# Set environment so cargo is available for all RUN/CMD
ENV PATH="/root/.cargo/bin:$PATH"

# Set workdir
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# If you use .env, uncomment the next line
# COPY .env.example .env

CMD ["python", "main.py"]
