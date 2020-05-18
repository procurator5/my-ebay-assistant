FROM python:3.6

WORKDIR /app
COPY . /app

RUN pip install -r /app/requirement.txt
