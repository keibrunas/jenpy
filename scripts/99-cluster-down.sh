#!/bin/bash
# scripts/99-cluster-down.sh

cd "$(dirname "$0")/.."
source ./config.env

echo "🧨 Starting Destruction of Environment..."
echo "   Cluster: $CLUSTER_NAME"
echo "   Zone:    $ZONE"

# 1. Graceful Cleanup (Sempre raccomandato)
if gcloud container clusters describe $CLUSTER_NAME --zone $ZONE > /dev/null 2>&1; then
    echo "🧹 Gracefully removing K8s workloads..."
    gcloud container clusters get-credentials $CLUSTER_NAME --zone $ZONE 2>/dev/null
    # Elimina namespace e aspetta conferma
    kubectl delete namespace jenkins --ignore-not-found=true --wait=true
else
    echo "   ⚠️ Cluster not reachable, skipping graceful cleanup."
fi

# 2. Delete the GKE Cluster (with "|| true" to ignore Not Found errors)
echo "🗑️ Deleting GKE Cluster..."
gcloud container clusters delete $CLUSTER_NAME \
    --zone $ZONE \
    --quiet 2>/dev/null || echo "   ⚠️ Cluster not found (already deleted)."

# 3. Cleanup Labeled Disks (Il metodo sicuro)
echo "🏷️  Checking for orphaned disks with label 'managed-by=jenkins-script'..."    
# Security filter to delete only disks linked to Jenkins and not in use:
# - labels.managed-by=jenkins-script: Prende SOLO i nostri dischi
# - -users:*: Removes only the incative ones (avoiding to remove a disk still in use)
TARGET_DISKS=$(gcloud compute disks list \
    --filter="labels.managed-by=jenkins-script AND -users:*" \
    --zones $ZONE \
    --format="value(name)" 2>/dev/null)

if [ -n "$TARGET_DISKS" ]; then
    echo "   Found disks to clean:"
    echo "$TARGET_DISKS"
    gcloud compute disks delete $TARGET_DISKS --zone $ZONE --quiet
    echo "   ✅ Labeled disks deleted."
else
    echo "   ✅ No orphaned labeled disks found."
fi

echo "✅ Environment destroyed. Zero hidden costs."