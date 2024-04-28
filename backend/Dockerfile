FROM python:3.11-slim

WORKDIR /curator_support

COPY . .

RUN apt-get update

RUN pip install .

RUN pip install rasa --ignore-requires-python
RUN pip install SQLAlchemy==2.0.23
