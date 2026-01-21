#!/bin/bash
# jenkins-controller/build.sh

# Stop script immediately on error
set -e 

# Load config
cd "$(dirname "$0")/.."
source ./config.env

cd jenkins-controller

echo "🐳 Building Docker Image..."
echo "   Target: $IMAGE_URL"

# Build
docker build -t $IMAGE_URL .

# Push
echo "⬆️ Pushing to Artifact Registry..."
docker push $IMAGE_URL

echo "✅ Jenkins Image Pushed Successfully!"