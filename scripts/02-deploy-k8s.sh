#!/bin/bash
# scripts/02-deploy-k8s.sh

set -e
cd "$(dirname "$0")/.."
source ./config.env

echo "🚀 Starting Phase 3: Deploying Jenkins to K8s..."

# 1. Get Cluster Credentials (Just to be safe)
gcloud container clusters get-credentials $CLUSTER_NAME --zone $ZONE

# 2. Create Namespace
echo "📦 Creating Namespace 'jenkins'..."
# The '|| true' ignores the error if it already exists
kubectl create namespace jenkins || true

# 3. Apply Manifests with Variable Substitution
echo "📄 Applying Manifests..."

# We use 'envsubst' to replace ${PROJECT_ID} and ${IMAGE_URL} in the YAMLs
# straight into kubectl
for file in k8s/*.yaml; do
    echo "   - Applying $(basename $file)"
    envsubst < $file | kubectl apply -f -
done

echo "✅ Deployment Complete."
echo "⏳ Waiting for Jenkins to boot (this takes ~1-2 mins)..."
kubectl rollout status deployment/jenkins -n jenkins

echo ""
echo "🎉 Jenkins is Ready!"
echo "👉 Run this command in a NEW terminal to access it:"
echo "   kubectl port-forward svc/jenkins-service 8080:80 -n jenkins"
echo "👉 Then open http://localhost:8080 in your browser."
echo " if you have the port 8080 already used kubectl port-forward svc/jenkins-service 9090:80 -n jenkins"