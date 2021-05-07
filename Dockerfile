FROM python:3.8-slim-buster

WORKDIR /app
COPY . .
RUN pip3 install -r requirements.txt

WORKDIR /app/src
CMD [ "python", "covid-vaccine-slot-booking.py"]