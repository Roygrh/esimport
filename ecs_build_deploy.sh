#!/bin/sh

export PrivateSubnetIds=subnet-0a86b4a71bf21649c,subnet-060ed0e9a14a3461a
export VpcId=vpc-04f1aecfcb3a4fe99
export STACK_NAME=esimport
export ESImportImageTag=$CI_COMMIT_SHA
export REPOSITORY_NAME=esimport

# export AWS_ACCOUNT_ID=684643752294
# export AWS_REGION=us-west-2
export ESImportEcrRepositoryUri=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPOSITORY_NAME 
echo $ESImportImageTag
set -x
aws cloudformation deploy --template-file ecs-template.yml --stack-name $STACK_NAME --parameter-overrides VpcId=$VpcId  PrivateSubnetIds=$PrivateSubnetIds ESImportImageTag=$ESImportImageTag ESImportEcrRepositoryUri=$ESImportEcrRepositoryUri --capabilities CAPABILITY_IAM --profile eleven_admin