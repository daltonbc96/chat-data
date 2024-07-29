#!/bin/bash

echo "Pulling the latest changes from the repository..."
git pull origin main
git lfs pull


echo "Building and starting the services with Docker Compose..."
docker compose up --build -d

echo "Removing dangling images..."
docker image prune -f

echo "Update process completed."
