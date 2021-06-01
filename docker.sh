#!/bin/bash

# Build docker image
echo "Building docker image..."
docker build -t covid-vaccine-booking .

# Run script in docker container
echo "Running script inside a docker container..."
docker run -it --rm covid-vaccine-booking

