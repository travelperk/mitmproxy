FROM python:3.6

ENV PYTHONUNBUFFERED 1

RUN apt-get update \
  && apt-get -y install git-core

COPY ./requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

COPY . /app

RUN cd /app; pip install .

WORKDIR /app
EXPOSE 8080