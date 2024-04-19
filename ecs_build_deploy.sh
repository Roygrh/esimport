#!/bin/bash

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <docker image name>"
fi

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

export ESImportImage=$1

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
    MssqlParameterName=$MSSQL_PARAMETER_NAME \
    DatabaseCallsWaitInSeconds=$DATABASE_CALLS_WAIT_IN_SECONDS \
    DatabaseQueryTimeout=$DATABASE_QUERY_TIMEOUT \
    LogLevel=$LOG_LEVEL \
    SnsTopicArn=$SNS_TOPIC_ARN \
    PpkSqsQueueURL=$PPK_SQS_QUEUE_URL \
    PpkSqsQueueArn=$PPK_SQS_QUEUE_ARN \
    PpkDlqQueueURL=$PPK_DLQ_QUEUE_URL \
    PpkDlqQueueArn=$PPK_DLQ_QUEUE_ARN \
    DatadogAPIKey=$DATADOG_API_KEY \
    --capabilities CAPABILITY_IAM \
    --role-arn $DEPLOYMENT_SERVICE_ROLE_ARN \
    --no-fail-on-empty-changeset
