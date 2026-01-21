#!/bin/bash
# scripts/99-cluster-down.sh

cd "$(dirname "$0")/.."
source ./config.env

echo "🧨 Starting Destruction of Environment..."
echo "   Cluster: $CLUSTER_NAME"
echo "   Zone:    $ZONE"

# 1. Delete the GKE Cluster (with "|| true" to ignore Not Found errors)
echo "🗑️ Deleting GKE Cluster..."
gcloud container clusters delete $CLUSTER_NAME \
    --zone $ZONE \
    --quiet 2>/dev/null || echo "   ⚠️ Cluster not found (already deleted)."

# 2. Cleanup orphaned Disks
echo "🧹 Checking for orphaned disks..."
# We suppress the warning logs with 2>/dev/null
DISKS=$(gcloud compute disks list \
    --filter="name~$CLUSTER_NAME" \
    --zones $ZONE \
    --format="value(name)" 2>/dev/null)

if [ -n "$DISKS" ]; then
    echo "   Found orphaned disks: $DISKS"
    gcloud compute disks delete $DISKS --zone $ZONE --quiet
    echo "   ✅ Disks deleted."
else
    echo "   ✅ No orphaned disks found."
fi

echo "✅ Environment destroyed. Costs stopped."