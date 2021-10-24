FROM python:3.6

ENV PYTHONUNBUFFERED 1

WORKDIR /app/san_2

ADD . /app/san_2

COPY ./requirements.txt /app/san_2/requirements.txt

RUN pip install -r requirements.txt 

COPY . /app/san_2
