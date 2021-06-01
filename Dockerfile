FROM python:3.9.5

RUN apt-get update && apt-get install -y beep

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY src src/

CMD [ "python3", "src/covid-vaccine-slot-booking.py" ]
