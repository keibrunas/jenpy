---

### 2. `jenkins-controller/README.md`
**Scopo:** Dettagliare come è costruita l'immagine custom e la filosofia JCasC.

```markdown
# 🎮 Jenkins Controller Image

This directory defines the **Custom Docker Image** for the Jenkins Controller.
Instead of configuring Jenkins manually via the UI (which is fragile), we bake the configuration directly into the image using **Jenkins Configuration as Code (JCasC)**.

## 🏗 Build Process

The `Dockerfile` performs the following steps:
1.  **Base:** Starts from `jenkins/jenkins:lts-jdk17`.
2.  **Tools:** Installs `gcloud` CLI and `kubectl` so the Controller can manage the cluster.
3.  **Plugins:** Installs all plugins defined in `plugins.txt` via `jenkins-plugin-cli`.
4.  **Config:** Copies `jenkins.yaml` to a safe location (`/var/jenkins_config`) to prevent volume overwrites.

## 📄 Key Files

### `jenkins.yaml` (JCasC)
The "Brain" of the setup. It automatically configures:
* **Clouds:** Kubernetes integration (URL, Namespace, Templates).
* **Security:** Disables the Setup Wizard, creates users, sets permissions.
* **Jobs:** Uses Job DSL to auto-seed pipelines from the Git repository.

### `plugins.txt`
A list of essential plugins pre-installed in the image, including:
* `kubernetes`: To spawn dynamic agents.
* `configuration-as-code`: To read `jenkins.yaml`.
* `google-oauth-plugin`: For GCP authentication.
* `workflow-aggregator`: For Pipeline support.

## 🚀 Usage

To build and push a new version of the controller:

```bash
# From the project root
./jenkins-controller/build.sh