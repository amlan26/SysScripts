# 🚀 Docker Deployment Script

A simple Bash script to pull a Docker image from **Amazon ECR** and deploy it as a running container on your server.

---

## 📁 Suggested Project Structure

```
deploy-toolkit/
├── deploy.sh          # this script
└── README.md          # this file
```

---

## 📋 What This Script Does

| Step | Action |
|------|--------|
| 1️⃣ | Asks for (or accepts) the **image tag** to deploy |
| 2️⃣ | Logs in to **Amazon ECR** using AWS CLI credentials |
| 3️⃣ | Pulls the specified image from your ECR repository |
| 4️⃣ | Stops & removes the old running container (if any) |
| 5️⃣ | Starts a fresh container with the new image |
| 6️⃣ | Cleans up dangling Docker images |
| 7️⃣ | Prints a deployment summary + running container status |

---

## ⚙️ Configuration

These values are hardcoded at the top of `deploy.sh` — update them to match your environment:

| Variable | Description | Placeholder Value |
|---|---|---|
| `AWS_REGION` | AWS region where your ECR lives | `your-aws-region` |
| `ECR_REGISTRY` | Your ECR registry URL | `your-account-id.dkr.ecr.your-region.amazonaws.com` |
| `IMAGE_NAME` | ECR repository/image name | `your-image-name` |
| `CONTAINER_NAME` | Name given to the running container | `your-container-name` |
| `HOST_PORT` | Port exposed on the host machine | `8080` |
| `CONTAINER_PORT` | Port the app listens on inside the container | `8080` |

---

## ✅ Prerequisites

Before running this script, make sure you have:

- 🐳 **Docker** installed and running on the host
- ☁️ **AWS CLI v2** installed and configured (`aws configure`)
- 🔑 IAM permissions to `ecr:GetAuthorizationToken`, `ecr:BatchGetImage`, `ecr:GetDownloadUrlForLayer`
- 🔐 Network/security group access to pull from ECR and expose the app port

---

## ▶️ Usage

### Make it executable (first time only)
```bash
chmod +x deploy.sh
```

### Pass the tag as an argument
```bash
./deploy.sh <image-tag>
```

### Or let the script prompt you
```bash
./deploy.sh
# Enter image tag to deploy:
```

---

## ⚠️ Notes & Caveats

- This script causes **brief downtime** — the old container is fully removed *before* the new one starts. For zero-downtime deploys, consider a blue-green setup or an orchestrator (ECS, Kubernetes, Docker Swarm).
- The script exits immediately on any failure due to `set -e` — check the console output carefully if a deploy fails.
- No environment variables, volumes, or `.env` files are passed into the container in this version — add `-e` / `--env-file` / `-v` flags to `docker run` if your app needs them.
- No health check step is included after container startup — consider adding a `curl` check against a `/health` endpoint before declaring success.

---

## 🛠️ Possible Improvements

- [ ] Add environment variable / secrets injection (`--env-file .env`)
- [ ] Add a post-deploy health check with automatic rollback
- [ ] Add Slack/Telegram notification on deploy success or failure
- [ ] Support multiple environments (staging/prod) via a config flag
- [ ] Add logging to a deploy history file

---
