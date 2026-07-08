FROM python:3.11-alpine

WORKDIR /app

COPY . /app

RUN pip install pybit requests python-dotenv django

CMD ["python3", "manage.py", "cryptoMonitor"]