FROM python:3.11-slim

WORKDIR /curator_support

COPY . .

RUN apt-get update
RUN echo "Y" | apt-get install gcc

RUN pip install .
