#!/bin/bash

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

if [ -z "$CI_COMMIT_SHA" ]; then
    export CI_COMMIT_SHA=$(git rev-parse HEAD)
fi


export ESImportImage=884031308615.dkr.ecr.us-west-2.amazonaws.com/esimport:$CI_COMMIT_SHA

VPC_ID="vpc-001169ce38d56981f"
InstancesSbunet="subnet-02c9d072f283310f8,subnet-036642058507434da,subnet-0d40abed2e503a4e2"
KEY_NAME="api-161"
MSSQL_DSN="asdf"
MSSQL_HOST="asdf"
MSSQL_USER="asdf"
MSSQL_PASSWORD="asdf"
SNS_TOPIC_ARN="arn:aws:sqs:us-west-2:884031308615:myqueue"
SENTRY_DSN="https://2e44068b182c457e938c436dc0ef9e04:64e8791e9b5045e3bd96cca2b190b50f@o4504016114352128.ingest.sentry.io/4504016119595008"
PPK_SQS_QUEUE_URL="https://sqs.us-west-2.amazonaws.com/884031308615/myqueue"
PPK_SQS_QUEUE_ARN="arn:aws:sqs:us-west-2:884031308615:myqueue"
PPK_DLQ_QUEUE_URL="https://sqs.us-west-2.amazonaws.com/884031308615/myqueue"
PPK_DLQ_QUEUE_ARN="arn:aws:sqs:us-west-2:884031308615:myqueue"

set -x
aws cloudformation deploy \
    --template-file ecs-template.yml \
    --stack-name $STACK_NAME \
    --parameter-overrides \
    VpcId=$VPC_ID \
    InstancesSbunet=$InstancesSbunet \
    ESImportImage=$ESImportImage \
    KeyName=$KEY_NAME \
    MSSQLDSN=$MSSQL_DSN \
    MssqlHost=$MSSQL_HOST \
    MssqlUser=$MSSQL_USER \
    MssqlPassword=$MSSQL_PASSWORD \
    SnsTopicArn=$SNS_TOPIC_ARN \
    SentryDSN=$SENTRY_DSN \
    PpkSqsQueueURL=$PPK_SQS_QUEUE_URL \
    PpkSqsQueueArn=$PPK_SQS_QUEUE_ARN \
    PpkDlqQueueURL=$PPK_DLQ_QUEUE_URL \
    PpkDlqQueueArn=$PPK_DLQ_QUEUE_ARN \
    InstanceType="t3.medium" \
    --capabilities CAPABILITY_IAM
