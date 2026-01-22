# jenpy
# 🚀 Ephemeral Jenkins on GKE (Spot Instances)

This repository contains a fully automated **Infrastructure-as-Code (IaC)** solution to deploy a disposable Jenkins Controller on Google Kubernetes Engine (GKE) using Spot VM instances to minimize costs.

It features **Jenkins Configuration as Code (JCasC)**, meaning no manual UI setup is required. The pipelines, credentials, and cloud connections are pre-configured in the Docker image.

---

## 🏗 Architecture

* **Compute:** GKE Autopilot / Standard (Spot Instances)
* **Storage:** Persistent Volume Claim (PVC) for Jenkins Home
* **Security:** Workload Identity (No JSON Keys required for GCP access)
* **Configuration:** JCasC (YAML-based configuration)
* **Pipeline:** Automated Job DSL with GitHub webhooks

---

## 🛠 Prerequisites

Ensure you have the following tools installed locally (WSL/Linux):

* [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) (`gcloud`)
* `kubectl`
* `docker`

---

## ⚙️ Configuration

### 1. Secrets Management
**Do NOT commit secrets to Git.**
Create a `config.env` file in the root directory (ensure it is added to `.gitignore`):

```bash
# config.env
PROJECT_ID="your-gcp-project-id"
CLUSTER_NAME="jenkins-demo-cluster"
ZONE="europe-west1-b"
IMAGE_URL="europe-west1-docker.pkg.dev/your-project/jenkins-repo/jenkins-controller:v1"

2. Google Cloud Initialization
Run this once to authenticate and configure Docker credential helpers:

Bash

./scripts/00-init-gcp.sh
🔁 The Lifecycle (How to Use)
Follow this sequence to spin up, use, and destroy the environment.

1. 🏗️ Build the Controller Image
Compiles the custom Docker image with JCasC settings, Plugins, and Themes.

When to run: If you change jenkins.yaml, plugins.txt, or update variables.

Bash

./jenkins-controller/build.sh
2. ☁️ Provision Infrastructure
Creates a GKE Cluster using Spot Instances (saves ~60-90% cost).

Duration: ~5 minutes.

Bash

./scripts/01-cluster-up.sh
3. 🚀 Deploy Jenkins
Applies Kubernetes manifests (Deployment, Service, PVC, RBAC) and injects secrets.

Duration: ~2 minutes.

Bash

source config.env  # Load secrets first!
./scripts/02-deploy-k8s.sh
4. 🔑 Access Jenkins
Since the cluster is private/internal, use a secure tunnel to access the UI.

Bash

kubectl port-forward svc/jenkins-service 9090:80 -n jenkins
URL: http://127.0.0.1:9090

Job: The BigQuery-Demo pipeline will be pre-created and ready to run.

5. 🧨 Destroy (Save Money)
CRITICAL: Run this immediately after you are done to stop billing.

Bash

./scripts/99-cluster-down.sh
Destroys: Cluster, Nodes, Load Balancers, Disks.

Keeps: Artifact Registry (Images) & IAM Roles (for faster restarts).

🧠 Key Technical Decisions (Why it works)
1. "Volume Conflict" Fix
We moved JCasC configuration files to /var/jenkins_config instead of the default /var/jenkins_home.

Reason: Kubernetes mounts a blank Persistent Disk over /var/jenkins_home, which would "hide" our baked-in config files. Moving them ensures they persist.

2. Environment Variable Injection
We pass PROJECT_ID from config.env -> Deployment -> jenkins.yaml -> GlobalNodeProperties.

Reason: Jenkins Agents run in separate pods. They don't inherit the Controller's variables. Using GlobalNodeProperties ensures the Agent knows which GCP Project to talk to.

3. Connectivity (DNS)
We configured the Kubernetes Cloud URL to: http://jenkins-service.jenkins.svc.cluster.local (Port 80)

Reason: Agents need the Fully Qualified Domain Name (FQDN) to reliably find the Controller inside the cluster.

📂 Repository Structure

.
├── app/                        # Python Application Code (The "Workload")
├── jenkins-controller/         # Custom Jenkins Image Source
│   ├── Dockerfile              # Installs GCloud SDK, Plugins, Copy Configs
│   ├── jenkins.yaml            # JCasC Configuration (Clouds, Jobs, Creds)
│   ├── plugins.txt             # List of installed plugins
│   └── build.sh                # Build & Push script
├── k8s/                        # Kubernetes Manifests
│   ├── 00-namespace.yaml
│   ├── 01-pvc.yaml             # Persistent Storage
│   ├── 03-deployment.yaml      # The Controller (Injects ENV vars)
│   ├── 04-service.yaml         # Internal Load Balancer
│   └── 05-rbac.yaml            # Permissions for spawning agents
├── scripts/                    # Automation Scripts
│   ├── 00-init-gcp.sh
│   ├── 01-cluster-up.sh
│   ├── 02-deploy-k8s.sh
│   └── 99-cluster-down.sh
├── pipelines/                  # Jenkinsfiles
│   └── demo-pipeline.jenkinsfile
├── config.env                  # Secrets (IGNORED by Git)
└── README.md                   # This file

***

### 📄 File 2: `MANUAL_STEPS.md` (Reference Guide)

Use this file if you ever need to debug the JCasC automation or want to set up the job manually for learning purposes.

```markdown
# 🛠 Manual Configuration Guide

This guide documents the manual steps to configure Jenkins if the JCasC automation is disabled or fails.

**Note:** If `jenkins.yaml` is working correctly, you do **not** need to do this. These settings are already applied automatically.

---

## 1. Configure Kubernetes Cloud Connection
*If the Agent Pods are not starting or staying "Offline".*

1.  Go to **Manage Jenkins** → **Clouds** → **kubernetes**.
2.  **Kubernetes Namespace:** `jenkins`
3.  **Jenkins URL:** `http://jenkins-service.jenkins.svc.cluster.local`
    * *Critical:* Do NOT use port `:8080` here. The Service listens on Port 80.
4.  **Jenkins Tunnel:** `jenkins-service.jenkins.svc.cluster.local:50000`
5.  **Pod Retention:** Set to `Never` (or `On Failure` for debugging).
6.  Click **Save**.

---

## 2. Add GitHub Credentials Manually
*If the pipeline cannot download the Jenkinsfile from a Private Repo.*

1.  Go to **Manage Jenkins** → **Credentials**.
2.  Click **(global)** under Domains.
3.  Click **+ Add Credentials**.
4.  Fill in the form:
    * **Kind:** `Username with password`
    * **Scope:** `Global`
    * **Username:** Your GitHub Username (e.g., `keibrunas`)
    * **Password:** Your GitHub Personal Access Token (starts with `ghp_...`)
    * **ID:** `github-access-token`
    * **Description:** `Manual GitHub Token`
5.  Click **Create**.

---

## 3. Create the Pipeline Job Manually
*If the "BigQuery-Demo" job does not appear on the dashboard.*

1.  **Dashboard** → **+ New Item**.
2.  **Name:** `BigQuery-Demo`.
3.  **Type:** Select `Pipeline`.
4.  Click **OK**.
5.  Scroll down to the **Pipeline** section:
    * **Definition:** `Pipeline script from SCM`
    * **SCM:** `Git`
    * **Repository URL:** `https://github.com/keibrunas/jenpy.git`
    * **Credentials:** Select `github-access-token` (created in step 2).
    * **Branch Specifier:** `*/main`
    * **Script Path:** `pipelines/demo-pipeline.jenkinsfile`
6.  Click **Save**.

---

## 4. Inject Environment Variables Manually
*If the Python script fails with `Project ID null`.*

1.  Go to **Manage Jenkins** → **System**.
2.  Scroll to **Global properties**.
3.  Check the box **Environment variables**.
4.  Click **Add**.
    * **Name:** `PROJECT_ID`
    * **Value:** `your-actual-gcp-project-id`
5.  Click **Save**.