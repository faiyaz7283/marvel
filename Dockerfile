FROM python:3.8-buster
COPY src/ /src
RUN pip install -e /src
