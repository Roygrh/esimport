#!/bin/sh


# export AWS_ACCOUNT_ID=684643752294
export AWS_REGION=us-west-2

export AWS_PAGER=""

export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query 'Account' --output text)

if [ -z "$CI_COMMIT_SHA" ]; then
    export CI_COMMIT_SHA=$(git rev-parse HEAD)
fi


export REPOSITORY_NAME=esimport
export ESImportEcrRepositoryUri=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPOSITORY_NAME 
export IMAGE_TAG=$ESImportEcrRepositoryUri:$CI_COMMIT_SHA
docker build -t $IMAGE_TAG .
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
docker push $IMAGE_TAG

