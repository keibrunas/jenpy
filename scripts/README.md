---

### 5. `scripts/README.md`
**Scopo:** Documentare gli script di "colla" bash, sottolineando l'ordine di esecuzione.

```markdown
# 📜 Automation Scripts

These Bash scripts handle the lifecycle of the infrastructure, from bootstrapping to destruction.

## ⚠️ Pre-requisites
All scripts assume you have a `config.env` file in the project root (see main README).
Run these scripts from the project root, e.g., `./scripts/01-cluster-up.sh`.

## 🛠 Script Index

### `00-init-gcp.sh`
**Bootstrap.**
* Selects the GCP Project.
* Enables required APIs (GKE, Artifact Registry, BigQuery).
* Creates the Artifact Registry repository.
* Configures Docker authentication.

### `01-cluster-up.sh`
**Provisioning.**
* Creates a GKE Standard Cluster.
* **Cost Saving:** Uses Spot Instances (`--spot`) for worker nodes.
* Enables Workload Identity.
* Sets up the Kubernetes Service Account binding.

### `02-deploy-k8s.sh`
**Deployment.**
* Connects `kubectl` to the cluster.
* Creates the `jenkins` namespace.
* Uses `envsubst` to inject variables into YAML manifests.
* Applies manifests to the cluster.
* Waits for the rollout to complete.

### `99-cluster-down.sh`
**Cleanup.**
* Deletes the GKE Cluster.
* **Note:** It does NOT delete the Artifact Registry images or the GCP Project itself.

## 🔍 Implementation Details
* All scripts use `set -e` to fail immediately if any command errors out.
* They automatically navigate to the project root using `cd "$(dirname "$0")/.."`.