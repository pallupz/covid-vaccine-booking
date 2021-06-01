#!/bin/bash

# Build docker image
docker build -t covid-vaccine-booking .

# Run script in docker container
docker run -it --rm covid-vaccine-booking

