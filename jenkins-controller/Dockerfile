FROM jenkins/jenkins:lts-jdk21   
USER root

# 1. Install prerequisites
RUN apt-get update && apt-get install -y lsb-release curl gnupg

# 2. Install Google Cloud SDK & Kubectl
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | \
    gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | \
    tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
RUN apt-get update && apt-get install -y google-cloud-cli google-cloud-cli-gke-gcloud-auth-plugin kubectl

# 3. Install Plugins
COPY plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli -f /usr/share/jenkins/ref/plugins.txt

# 4. Copy JCasC Configuration (MOVED TO SAFE LOCATION)
#    We create a directory that is NOT mounted by the PVC
RUN mkdir -p /var/jenkins_config
COPY jenkins.yaml /var/jenkins_config/jenkins.yaml
ENV CASC_JENKINS_CONFIG=/var/jenkins_config/jenkins.yaml

# 5. Disable Setup Wizard
ENV JAVA_OPTS="-Djenkins.install.runSetupWizard=false"

USER jenkins