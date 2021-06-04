FROM python:3.9-slim

ENV APP_HOME /app
ENV BEEP "no"
ENV AWS_DEFAULT_REGION "ap-south-1"

RUN apt-get update && \
    apt-get install -y beep && \
    apt-get clean --quiet && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR $APP_HOME
COPY ./requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

COPY ./src/ /app/

ENTRYPOINT ["/app/covid-vaccine-slot-booking.py"]