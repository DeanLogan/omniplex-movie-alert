# Use the official Ubuntu latest base image
FROM ubuntu:latest

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary libraries
RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-venv \
    ffmpeg \
    wget \
    libx11-6 \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Download and install geckodriver
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-linux64.tar.gz && \
    tar -xvzf geckodriver-v0.34.0-linux64.tar.gz && \
    rm geckodriver-v0.34.0-linux64.tar.gz && \
    chmod +x geckodriver && \
    mv geckodriver /usr/local/bin/

RUN apt-get update && apt-get install -y wget bzip2 libxtst6 libgtk-3-0 libx11-xcb-dev libdbus-glib-1-2 libxt6 libpci-dev && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y firefox

# Set the working directory to /app
WORKDIR /app

# Copy the Python script and requirements file
COPY movie_alerts.py .
COPY requirements.txt .

# Create a Python virtual environment and install Python dependencies
RUN python3 -m venv venv && \
    . venv/bin/activate && \
    pip install -r requirements.txt

# Set the entrypoint command
ENTRYPOINT ["xvfb-run", "--", "/app/venv/bin/python3", "movie-alerts.py"]