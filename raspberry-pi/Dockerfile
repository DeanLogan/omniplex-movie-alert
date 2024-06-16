FROM python:3.9.1

WORKDIR /app

COPY requirements.txt .

COPY . .

RUN apt-get update -y

RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

RUN apt-get install -y ./google-chrome-stable_current_amd64.deb

RUN wget https://storage.googleapis.com/chrome-for-testing-public/126.0.6478.61/linux64/chromedriver-linux64.zip

RUN apt-get install -y unzip

RUN unzip chromedriver-linux64.zip

RUN mv chromedriver-linux64/chromedriver /usr/bin/chromedriver

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "movie_alerts.py"]
