# 🎮 Jenkins Controller (Custom Image)

This directory contains the source code to build a **Custom, Immutable Jenkins Controller**.
Instead of starting with a blank Jenkins and configuring it manually via the UI, we bake the entire configuration, security settings, and tooling directly into the Docker image using **JCasC (Jenkins Configuration as Code)**.

---

## 📂 File Index

| File | Purpose |
| :--- | :--- |
| `Dockerfile` | **The Recipe.** Installs OS tools (`kubectl`, `gcloud`), plugins, and copies config files. |
| `jenkins.yaml` | **The Brain.** Defines system settings (Security, Clouds, Views) in YAML format. |
| `plugins.txt` | **The Extensions.** A precise list of plugins and versions to install. |
| `build.sh` | **The Factory.** Automates the `docker build` and `docker push` process to Artifact Registry. |

---

## 🏗️ Technical Deep Dive

### 1. The "Config Volume" Strategy (Crucial)
A common problem when containerizing Jenkins is the **Storage Overwrite Conflict**.
* **Problem:** Kubernetes mounts a Persistent Volume (PVC) at `/var/jenkins_home` to save build history. This mount **hides/overwrites** any file you placed in that folder during the `docker build` process.
* **Solution:** inside the `Dockerfile`, we copy `jenkins.yaml` to a **safe, separate location**:
    ```dockerfile
    COPY jenkins.yaml /var/jenkins_config/jenkins.yaml
    ENV CASC_JENKINS_CONFIG=/var/jenkins_config/jenkins.yaml
    ```
    We then tell Jenkins (via the `CASC_JENKINS_CONFIG` env var) to look for its configuration there. This ensures the config exists even after the PVC is mounted.

### 2. Plugin Management (`plugins.txt`)
We do not install plugins via the UI ("Manage Jenkins" -> "Plugins").
Instead, we use the `jenkins-plugin-cli` tool inside the Dockerfile.
* **Benefit:** Dependency resolution is handled at build time. If a plugin conflicts, the build fails, not the production server.
* **Key Plugins:**
    * `kubernetes`: Allows spawning dynamic agents.
    * `configuration-as-code`: Enables reading `jenkins.yaml`.
    * `job-dsl`: Allows creating pipelines automatically from Git.
    * `google-oauth-plugin`: Handles authentication with GCP.

### 3. JCasC (`jenkins.yaml`) Analysis
This file replaces the "Manage Jenkins" screen.

* **Security:**
    * Creates the first admin user (username: `admin`).
    * Disables the "Unlock Jenkins" setup wizard (`disableSetupWizard: true`).
* **Cloud Definition:**
    * Configures the connection to the Kubernetes API.
    * Defines `jenkins-tunnel` so agents can talk back to the controller.
* **Job Seeding:**
    * It points to the Git repository. On startup, it scans the `pipelines/` folder and automatically creates the jobs (`BigQuery-Demo`, `Pull-Request-Check`, etc.).

---

## 🛠 Build Process

When you run `./build.sh`, the following pipeline executes locally:

```mermaid
graph TD
    A[Start Build] --> B[Pull Base Image jenkins/jenkins:lts]
    B --> C[Install OS Tools (gcloud, kubectl)]
    C --> D[Install Plugins (jenkins-plugin-cli)]
    D --> E[Copy JCasC Config to /var/jenkins_config]
    E --> F[Docker Push to Artifact Registry]
    F --> G[Ready for K8s Deployment]

```

### Why install `gcloud` and `kubectl`?

You might notice the `Dockerfile` installs the Google Cloud SDK.
**Why?** Even though the *Agents* do the heavy lifting, the *Controller* sometimes needs to perform orchestration tasks or verify cloud connectivity. Having these tools pre-installed makes debugging significantly easier (`kubectl exec` into the controller allows you to inspect the cluster immediately).

---

## 🚀 How to Modify

### Scenario A: Adding a Plugin

1. Add the plugin ID to `plugins.txt`.
2. Run `./build.sh`.
3. Restart the pod (`kubectl rollout restart deployment jenkins -n jenkins`).

### Scenario B: Changing System Config

1. Edit `jenkins.yaml` (e.g., add a global environment variable).
2. Run `./build.sh`.
3. Restart the pod.

### Scenario C: Updating Pipelines

**No rebuild needed!**
Since pipelines are defined in `jenkins.yaml` as "SCM" (Source Control Management), just push your changes to the Git repository. Jenkins will pick up the new pipeline logic on the next run.