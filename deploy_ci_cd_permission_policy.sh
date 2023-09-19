#!/usr/bin/bash

# we use this to create user, Roles & IAM policies that is used during deployment.
# After running this script, manually create access keys for user that is created from the cf template.
# Also note down the service role arn from cf stack output ElevenApiDeployServiceRole. 
# The service role is assumed by the main cf stack.
# Use the access keys & service role arn in gitlab variables.


STACK_NAME=reporting-esimport-gitlab-deploy
PROFILE=monolith-dev-admin

SamArtifactBucketEast=$1
SamArtifactBucketEast=${SamArtifactBucketEast:-lambda-artifacts-11}

SamArtifactBucketWest=$2
SamArtifactBucketWest=${SamArtifactBucketWest:-eleven-prod-lambda-artifacts}

aws cloudformation deploy \
  --capabilities CAPABILITY_NAMED_IAM \
  --template-file ecs-deployment-role-template.yaml \
  --stack-name $STACK_NAME \
  --profile $PROFILE \
  --parameter-overrides \
    SamArtifactBucketEast=$SamArtifactBucketEast \
    SamArtifactBucketWest=$SamArtifactBucketWest


printf "***Use the below Service Role ARN for deployments***\n\n"

aws cloudformation describe-stacks --profile $PROFILE --stack-name $STACK_NAME \
  --query 'Stacks[0].Outputs[?OutputKey==`ESImportDeployServiceRole`].OutputValue' --output text 

# you can also use this cli command to create access keys for the user
# set -x
# export $(printf "AWS_ACCESS_KEY_ID=%s AWS_SECRET_ACCESS_KEY=%s" \
# $(aws iam create-access-key --user-name esimport-deploy-user \
# --query "AccessKey.[AccessKeyId,SecretAccessKey]" \
# --output text))
# export AWS_SESSION_TOKEN=
