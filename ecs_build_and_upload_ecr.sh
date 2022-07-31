#!/bin/sh


export REPOSITORY_NAME=ecsimport
export ESImportEcrRepositoryUri=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPOSITORY_NAME 
export IMAGE_TAG=$ESImportEcrRepositoryUri:$CI_COMMIT_SHA
docker build -t $IMAGE_TAG .
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
docker push $IMAGE_TAG