#!/bin/bash

# Build the Docker image
docker build -t my-discord-bot .

# Run the Docker container
docker run -d --name my-discord-bot-container my-discord-bot