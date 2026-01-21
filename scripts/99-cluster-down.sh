#!/bin/bash
# scripts/99-cluster-down.sh

cd "$(dirname "$0")/.."
source ./config.env

echo "🧨 Starting Destruction of Environment..."
echo "   Cluster: $CLUSTER_NAME"
echo "   Zone:    $ZONE"

# 1. Delete the GKE Cluster
#    (This automatically deletes the Load Balancers and Nodes)
echo "🗑️ Deleting GKE Cluster (This takes ~5 mins)..."
gcloud container clusters delete $CLUSTER_NAME \
    --zone $ZONE \
    --quiet

# 2. Cleanup orphaned Disks
#    Sometimes PVCs leave disks behind. We find disks with the cluster name and kill them.
echo "🧹 Checking for orphaned disks..."
# List disks that contain the cluster name in their description/name
DISKS=$(gcloud compute disks list --filter="name~$CLUSTER_NAME" --format="value(name)" --zone $ZONE)

if [ -n "$DISKS" ]; then
    echo "   Found orphaned disks: $DISKS"
    gcloud compute disks delete $DISKS --zone $ZONE --quiet
    echo "   ✅ Disks deleted."
else
    echo "   ✅ No orphaned disks found."
fi

# 3. (Optional) Remove the Service Account?
#    Usually we KEEP the Artifact Registry and Service Account 
#    so the next "Up" is faster.
echo "✅ Cluster destroyed. Costs stopped."
echo "   (Artifact Registry and IAM Service Account were preserved for next time)."