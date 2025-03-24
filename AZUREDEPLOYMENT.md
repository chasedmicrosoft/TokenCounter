# Azure Deployment Guide

This document outlines how to deploy the Token Counter application to Azure using Azure Container Registry (ACR) and GitHub Actions.

## Deployment Architecture

The deployment will use the following Azure services:
- **Azure Container Registry (ACR)**: To store and manage our Docker container images
- **Azure Container Instances (ACI)**: To run our containerized application
- **Azure Key Vault** (optional): To securely store secrets

![Deployment Architecture](https://docs.microsoft.com/en-us/azure/container-instances/media/container-instances-github-action/workflow.png)

## Prerequisites

- Azure subscription
- GitHub account with access to this repository
- Azure CLI installed locally for initial setup

## Step 1: Set Up Azure Container Registry

1. Create a new Azure Container Registry:
   ```bash
   # Login to Azure
   az login

   # Create a resource group
   az group create --name TokenCounterRG --location eastus

   # Create container registry (name must be globally unique)
   az acr create --resource-group TokenCounterRG \
     --name tokencounterregistry \
     --sku Basic \
     --admin-enabled true
   ```

2. Get the ACR credentials:
   ```bash
   # Get the login server
   az acr show --name tokencounterregistry --query loginServer --output tsv

   # Get the username and password
   az acr credential show --name tokencounterregistry
   ```

## Step 2: Set Up GitHub Secrets

Add the following secrets to your GitHub repository:

1. Go to your GitHub repository → Settings → Secrets and variables → Actions
2. Add the following secrets:
   - `REGISTRY_LOGIN_SERVER`: The login server URL of your ACR (e.g., tokencounterregistry.azurecr.io)
   - `REGISTRY_USERNAME`: The username for your ACR
   - `REGISTRY_PASSWORD`: The password for your ACR
   - `API_USERNAME`: Your API username
   - `API_PASSWORD`: Your API password

## Step 3: Create GitHub Actions Workflow

Create a GitHub Actions workflow file to build and push the images to ACR:

```yaml
# .github/workflows/azure-deploy.yml
name: Build and Deploy to ACR

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Log in to Azure Container Registry
        uses: docker/login-action@v1
        with:
          registry: ${{ secrets.REGISTRY_LOGIN_SERVER }}
          username: ${{ secrets.REGISTRY_USERNAME }}
          password: ${{ secrets.REGISTRY_PASSWORD }}
      
      - name: Build and push API image
        uses: docker/build-push-action@v2
        with:
          context: .
          push: true
          tags: ${{ secrets.REGISTRY_LOGIN_SERVER }}/tokencounter-api:latest
      
      - name: Build and push frontend image
        uses: docker/build-push-action@v2
        with:
          context: ./frontend
          push: true
          tags: ${{ secrets.REGISTRY_LOGIN_SERVER }}/tokencounter-frontend:latest
```

## Step 4: Deploy to Azure Container Instances

You can deploy to ACI using either the Azure Portal, Azure CLI, or add it to your GitHub Actions workflow.

### Option 1: Deploy Using Azure CLI

```bash
# Create a container group for the API
az container create \
  --resource-group TokenCounterRG \
  --name tokencounter-api \
  --image tokencounterregistry.azurecr.io/tokencounter-api:latest \
  --registry-login-server tokencounterregistry.azurecr.io \
  --registry-username <registry-username> \
  --registry-password <registry-password> \
  --dns-name-label tokencounter-api \
  --ports 8000 \
  --environment-variables \
    ENVIRONMENT=prod \
    API_USERNAME=${{ secrets.API_USERNAME }} \
    API_PASSWORD=${{ secrets.API_PASSWORD }}

# Create a container group for the frontend
az container create \
  --resource-group TokenCounterRG \
  --name tokencounter-frontend \
  --image tokencounterregistry.azurecr.io/tokencounter-frontend:latest \
  --registry-login-server tokencounterregistry.azurecr.io \
  --registry-username <registry-username> \
  --registry-password <registry-password> \
  --dns-name-label tokencounter-frontend \
  --ports 8501 \
  --environment-variables \
    API_HOST=http://tokencounter-api.<region>.azurecontainer.io:8000 \
    API_USERNAME=${{ secrets.API_USERNAME }} \
    API_PASSWORD=${{ secrets.API_PASSWORD }}
```

### Option 2: Add Deployment to GitHub Actions Workflow

Extend your GitHub Actions workflow with ACI deployment:

```yaml
- name: Deploy API to Azure Container Instances
  uses: azure/aci-deploy@v1
  with:
    resource-group: TokenCounterRG
    dns-name-label: tokencounter-api
    image: ${{ secrets.REGISTRY_LOGIN_SERVER }}/tokencounter-api:latest
    registry-login-server: ${{ secrets.REGISTRY_LOGIN_SERVER }}
    registry-username: ${{ secrets.REGISTRY_USERNAME }}
    registry-password: ${{ secrets.REGISTRY_PASSWORD }}
    name: tokencounter-api
    location: 'eastus'
    ports: 8000
    environment-variables: |
      ENVIRONMENT=prod
      API_USERNAME=${{ secrets.API_USERNAME }}
      API_PASSWORD=${{ secrets.API_PASSWORD }}

- name: Deploy Frontend to Azure Container Instances
  uses: azure/aci-deploy@v1
  with:
    resource-group: TokenCounterRG
    dns-name-label: tokencounter-frontend
    image: ${{ secrets.REGISTRY_LOGIN_SERVER }}/tokencounter-frontend:latest
    registry-login-server: ${{ secrets.REGISTRY_LOGIN_SERVER }}
    registry-username: ${{ secrets.REGISTRY_USERNAME }}
    registry-password: ${{ secrets.REGISTRY_PASSWORD }}
    name: tokencounter-frontend
    location: 'eastus'
    ports: 8501
    environment-variables: |
      API_HOST=http://tokencounter-api.eastus.azurecontainer.io:8000
      API_USERNAME=${{ secrets.API_USERNAME }}
      API_PASSWORD=${{ secrets.API_PASSWORD }}
```

## Step 5: Access Your Deployed Application

Once deployed, your application will be available at:
- API: `http://tokencounter-api.<region>.azurecontainer.io:8000`
- Frontend: `http://tokencounter-frontend.<region>.azurecontainer.io:8501`

## Advanced Options

### Using Azure App Service

For production workloads requiring more stability, consider Azure App Service:

```bash
# Create an App Service plan
az appservice plan create --name TokenCounterPlan --resource-group TokenCounterRG --sku B1 --is-linux

# Create a web app for the API
az webapp create --resource-group TokenCounterRG --plan TokenCounterPlan --name tokencounter-api --deployment-container-image-name tokencounterregistry.azurecr.io/tokencounter-api:latest

# Create a web app for the frontend
az webapp create --resource-group TokenCounterRG --plan TokenCounterPlan --name tokencounter-frontend --deployment-container-image-name tokencounterregistry.azurecr.io/tokencounter-frontend:latest
```

### Using Azure Kubernetes Service (AKS)

For large-scale or multi-component applications, consider AKS:

```bash
# Create AKS cluster
az aks create --resource-group TokenCounterRG --name TokenCounterAKS --node-count 1 --enable-addons monitoring --generate-ssh-keys

# Connect to the cluster
az aks get-credentials --resource-group TokenCounterRG --name TokenCounterAKS
```

Then deploy using Kubernetes manifests or Helm charts.

## Cost Management

- **Azure Container Registry**: ~$5/month for Basic tier
- **Azure Container Instances**: Pay per second (~$0.0025/vCPU/hour, ~$0.0003/GB/hour)
- **Azure App Service**: ~$13/month for B1 tier

Consider stopping or deleting resources when not in use to minimize costs.

## Monitoring and Logging

- Enable Azure Monitor for your container instances to track performance and logs
- Set up alerts for critical metrics
- Use Application Insights for more detailed application monitoring

## Security Considerations

- Store sensitive information in Azure Key Vault
- Use managed identities for accessing Azure resources
- Implement network security rules to restrict access

# Generated by Copilot
