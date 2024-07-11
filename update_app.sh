#!/bin/bash

# Pull the latest changes from your repository
git pull origin main

# Build and start the services with Docker Compose
docker compose up --build -d

# Remove dangling images
docker image prune -f
