---

### 3. `k8s/README.md`
**Scopo:** Spiegare i manifesti Kubernetes e come i vari pezzi (Storage, Network, Identity) si incastrano.

```markdown
# ☸️ Kubernetes Manifests

This directory contains the declarative YAML files used to deploy Jenkins onto GKE.
We use `envsubst` during deployment to inject dynamic variables (like Project ID and Image URL).

## 🧩 Components

| File | Kind | Purpose |
| :--- | :--- | :--- |
| `01-sa.yaml` | `ServiceAccount` | **Identity.** The bridge between Kubernetes and Google Cloud (Workload Identity). |
| `02-pvc.yaml` | `PersistentVolumeClaim` | **Storage.** Requests 10Gi of persistent disk to save Jenkins history across restarts. |
| `03-deployment.yaml` | `Deployment` | **The App.** Defines the Jenkins Controller Pod, mounts the volume, and sets resource limits. |
| `04-service.yaml` | `Service` | **Network.** Exposes Jenkins internally on ports `80` (HTTP) and `50000` (JNLP Agent connection). |
| `05-rbac.yaml` | `Role/RoleBinding` | **Permissions.** Grants Jenkins permission to start/stop Pods in the `jenkins` namespace. |

## 🛡️ Security Context

* **Non-Root:** The container runs as user `1000` (jenkins).
* **FSGroup:** The volume is mounted with group `1000` ensuring the non-root user can write data.
* **ClusterIP:** The service is **not** exposed to the public internet. Access is only possible via `kubectl port-forward`.