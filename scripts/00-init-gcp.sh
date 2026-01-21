#!/bin/bash
# scripts/00-init-gcp.sh

# 1. Load config (go up one level to root)
cd "$(dirname "$0")/.."
source ./config.env

echo "🚀 Initializing GCP for Project: $PROJECT_ID"
gcloud config set project $PROJECT_ID

echo "🔌 Enabling APIs (GKE, Artifact Registry, IAM, BigQuery)..."
gcloud services enable \
    container.googleapis.com \
    artifactregistry.googleapis.com \
    iamcredentials.googleapis.com \
    cloudresourcemanager.googleapis.com \
    bigquery.googleapis.com

echo "📦 Checking/Creating Artifact Registry..."
if ! gcloud artifacts repositories describe $REPO_NAME --location=$REGION > /dev/null 2>&1; then
    gcloud artifacts repositories create $REPO_NAME \
        --repository-format=docker \
        --location=$REGION \
        --description="Jenkins Infrastructure"
    echo "✅ Repo '$REPO_NAME' created."
    sleep 20
else
    echo "✅ Repo '$REPO_NAME' already exists."
fi

echo "🔐 Configuring Docker Auth..."
gcloud auth configure-docker ${REGION}-docker.pkg.dev

echo "✅ Initialization Complete."