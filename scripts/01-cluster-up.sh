#!/bin/bash
# scripts/01-cluster-up.sh

set -e
cd "$(dirname "$0")/.."
source ./config.env

echo "🚀 Starting Phase 2: Bringing up the Infrastructure..."

# ---------------------------------------------------------
# 1. Create Google Service Account (GSA) for Jenkins
# ---------------------------------------------------------
GSA_NAME="jenkins-sa"
GSA_EMAIL="${GSA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

echo "👤 Checking Service Account: $GSA_EMAIL"
if ! gcloud iam service-accounts describe $GSA_EMAIL > /dev/null 2>&1; then
    gcloud iam service-accounts create $GSA_NAME \
        --display-name="Jenkins Service Account"
    echo "✅ Created Service Account: $GSA_EMAIL"
else
    echo "✅ Service Account exists."
fi

# ---------------------------------------------------------
# 2. Grant Permissions to the GSA
# ---------------------------------------------------------
echo "🔑 Granting IAM Roles to GSA..."

# Allow Jenkins to read/write to BigQuery (for the Python App)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$GSA_EMAIL" \
    --role="roles/bigquery.admin" > /dev/null

# Allow Jenkins to read from Artifact Registry (to pull builder images if needed)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$GSA_EMAIL" \
    --role="roles/artifactregistry.reader" > /dev/null

# ---------------------------------------------------------
# 3. Create GKE Cluster (Spot Instances + Workload Identity)
# ---------------------------------------------------------
echo "🏗️ Creating GKE Cluster: $CLUSTER_NAME (This takes ~5-8 mins)..."

# We check if cluster exists to avoid errors on re-run
if ! gcloud container clusters describe $CLUSTER_NAME --zone $ZONE > /dev/null 2>&1; then
    gcloud container clusters create $CLUSTER_NAME \
        --zone $ZONE \
        --num-nodes 1 \
        --machine-type e2-standard-2 \
        --spot \
        --workload-pool="${PROJECT_ID}.svc.id.goog" \
        --enable-ip-alias \
        --scopes "https://www.googleapis.com/auth/cloud-platform" \
        --disk-size=50 \
        --disk-type=pd-standard \
        --labels="env=demo,type=ephemeral"
    
    echo "✅ Cluster Created."
else
    echo "✅ Cluster already exists."
fi

# ---------------------------------------------------------
# 4. Get Credentials (Configure kubectl)
# ---------------------------------------------------------
echo "🔌 Getting Cluster Credentials..."
gcloud container clusters get-credentials $CLUSTER_NAME --zone $ZONE

# ---------------------------------------------------------
# 5. Configure Workload Identity Binding
# ---------------------------------------------------------
# This allows the Kubernetes Service Account (KSA) named "jenkins-sa" 
# in namespace "jenkins" to act as the Google Service Account (GSA).
echo "🔗 Binding Kubernetes SA to Google SA..."

# Variables for K8s side
K8S_NAMESPACE="jenkins"
K8S_SA_NAME="jenkins-sa"

# Allow the GSA to be impersonated by the KSA
gcloud iam service-accounts add-iam-policy-binding $GSA_EMAIL \
    --role roles/iam.workloadIdentityUser \
    --member "serviceAccount:${PROJECT_ID}.svc.id.goog[${K8S_NAMESPACE}/${K8S_SA_NAME}]" > /dev/null

echo "✅ Infrastructure is UP and Workload Identity is configured!"
echo "   - Cluster: $CLUSTER_NAME (Spot)"
echo "   - GSA: $GSA_EMAIL"
echo "   - Ready for Phase 3 (Deployment)."