#!/bin/bash

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <docker image name>"
fi

export PrivateSubnetIds=subnet-0fdff113201f6d53b,subnet-0670fa12cd2483df8
export VpcId=vpc-008da50ebc5dc0871
export STACK_NAME=esimport

# disabling it to get stack status
set +e
aws cloudformation describe-stacks --stack-name $STACK_NAME

if [[ $? == 0 ]]; then
    command="update-stack"
    command_wait="stack-update-complete"
else
    command="create-stack"
    command_wait="stack-create-complete"
fi

set -e

# export AWS_ACCOUNT_ID=684643752294
# export AWS_REGION=us-west-2
export ESImportImage=$1
export KEY_NAME=eleven-deploy
export MssqlHost=localhost
export MssqlUser=sa
export MssqlPassword=DistroDev@11
export SnsTopicArn=
export SentryDSN=
export PpkSqsQueueURL=
export PpkDlqQueueURL=

set -x
aws cloudformation deploy \
    --template-file ecs-template.yml \
    --stack-name $STACK_NAME \
    --parameter-overrides \
    VpcId=$VpcId \
    InstancesSbunet=$PrivateSubnetIds \
    ESImportImage=$ESImportImage \
    KeyName=$KEY_NAME \
    MssqlHost=$MssqlHost \
    MssqlUser=$MssqlUser \
    MssqlPassword=$MssqlPassword \
    SnsTopicArn=$SnsTopicArn \
    SentryDSN=$SentryDSN \
    PpkSqsQueueURL=$PpkSqsQueueURL \
    PpkDlqQueueURL=$PpkDlqQueueURL \
    --capabilities CAPABILITY_IAM
