FROM python:3.9.1

WORKDIR /app

COPY requirements.txt .

COPY . .

RUN apt update -y

RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

RUN apt install ./google-chrome-stable_current_amd64.deb -y

RUN wget https://storage.googleapis.com/chrome-for-testing-public/125.0.6422.141/linux64/chromedriver-linux64.zip

RUN apt install unzip -y

RUN unzip chromedriver-linux64.zip

RUN mv chromedriver-linux64/chromedriver /usr/bin/chromedriver

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "movie_alerts.py"]