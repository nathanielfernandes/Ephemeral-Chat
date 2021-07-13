# syntax=docker/dockerfile:1

FROM python:3.9

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .


CMD ["python3", "-m", "uvicorn", "main:app" , "--port", "80", "--host", "0.0.0.0"]