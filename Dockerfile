FROM python:3.12
WORKDIR /app

COPY requirements.txt .
COPY . .

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "main.py"]