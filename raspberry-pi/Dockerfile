FROM balenalib/raspberry-pi-python:3.9.1

WORKDIR /app

COPY requirements.txt .

COPY . .

RUN apt-get update -y && \
    apt-get install -y \
    wget \
    unzip \
    gnupg \
    ca-certificates \
    lsb-release \
    software-properties-common

# Add the repository key for Chromium
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -

# Add the Chromium repository to sources list
RUN echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list

# Install Chromium browser (arm version)
RUN apt-get update -y && \
    apt-get install -y chromium-browser

# Download ChromeDriver for arm architecture
RUN wget https://chromedriver.storage.googleapis.com/87.0.4280.88/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip && \
    mv chromedriver /usr/bin/chromedriver && \
    chmod +x /usr/bin/chromedriver

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "movie_alerts.py"]
