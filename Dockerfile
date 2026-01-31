FROM python:3.12
WORKDIR /app

COPY requirements.txt .
COPY . .

RUN apt-get update -y
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get install -y ./google-chrome-stable_current_amd64.deb

RUN wget https://storage.googleapis.com/chrome-for-testing-public/144.0.7559.109/linux64/chromedriver-linux64.zip
RUN apt-get install -y unzip
RUN unzip chromedriver-linux64.zip

RUN mv chromedriver-linux64/chromedriver /usr/bin/chromedriver

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "main.py"]