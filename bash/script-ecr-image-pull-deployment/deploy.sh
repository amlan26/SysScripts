#!/bin/bash

set -e

#########################################
# CONFIG
#########################################

AWS_REGION="your-aws-region"

ECR_REGISTRY="your-account-id.dkr.ecr.your-region.amazonaws.com"
IMAGE_NAME="your-image-name"
IMAGE_REPO="${ECR_REGISTRY}/${IMAGE_NAME}"

CONTAINER_NAME="your-container-name"

HOST_PORT=8080
CONTAINER_PORT=8080


#########################################
# IMAGE TAG
#########################################

if [ -n "$1" ]; then
    IMAGE_TAG="$1"
else
    read -p "Enter image tag to deploy: " IMAGE_TAG
fi

echo ""
echo "======================================"
echo "Deploying Image"
echo "Repository : ${IMAGE_REPO}"
echo "Tag        : ${IMAGE_TAG}"
echo "======================================"

#########################################
# LOGIN TO ECR
#########################################

echo ""
echo "Logging into Amazon ECR..."

aws ecr get-login-password --region ${AWS_REGION} | \
docker login --username AWS --password-stdin ${ECR_REGISTRY}

#########################################
# PULL IMAGE
#########################################

echo ""
echo "Pulling image..."

docker pull ${IMAGE_REPO}:${IMAGE_TAG}

#########################################
# STOP OLD CONTAINER
#########################################

if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo ""
    echo "Stopping old container..."
    docker rm -f ${CONTAINER_NAME}
fi

#########################################
# START NEW CONTAINER
#########################################

echo ""
echo "Starting new container..."

docker run -d \
    --name ${CONTAINER_NAME} \
    --restart unless-stopped \
    -p ${HOST_PORT}:${CONTAINER_PORT} \
    ${IMAGE_REPO}:${IMAGE_TAG}

#########################################
# OPTIONAL CLEANUP
#########################################

echo ""
echo "Removing dangling images..."

docker image prune -f

#########################################
# SUMMARY
#########################################

echo ""
echo "======================================"
echo "Deployment Successful"
echo "Repository : ${IMAGE_REPO}"
echo "Image Tag  : ${IMAGE_TAG}"
echo "Container  : ${CONTAINER_NAME}"
echo "Port       : ${HOST_PORT}:${CONTAINER_PORT}"
echo "======================================"

docker ps --filter "name=${CONTAINER_NAME}"