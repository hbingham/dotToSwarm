FROM ubuntu:latest
FROM python:3.5
MAINTAINER Hunter hbingham@ucsc.edu
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev
COPY ./webapp /app
WORKDIR /app
RUN pip install Flask
RUN pip install requests
RUN pip install Flask-API
RUN pip install markdown
EXPOSE 8080
CMD python /app/app.py
