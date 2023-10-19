#!/usr/bin/env bash
# bash deploy.sh cdk-hnb659fds-assets-884031308615-us-west-2 arn:aws:iam::884031308615:role/service-role/method_saml-role-lv757ro9 arn:aws:sns:us-west-2:884031308615:my-test-topic arn:aws:sns:us-west-2:884031308615:my-test-topic http://example.com https://public@sentry.example.com/1
# Disable AWS SAM Telemetry
export SAM_CLI_TELEMETRY=0
set -e

if [[ $# -lt 5 ]]
  then
    echo "No enough arguments supplied"
    echo '$1 - Deploy Asset Bucket Name (temporary place to store deploy asset)'
    echo '$2 - lambda role arn'
    echo '$3 - sns topic arn'
    echo '$4 - dpsk sns topic arn'
    echo '$5 - es host'
    echo '$6 - sentry dsn'
    exit
fi

deploy_s3_bucket=$1
lambda_role_arn=$2
sns_topic_arn=$3
dpsk_sns_topic_arn=$4
es_url=$5
sentry_dsn=$6

log_level=$LOG_LEVEL
aws_region=$AWS_REGION
cf_stack_name=$STACK_NAME
execution_timeout=$EXECUTION_TIMEOUT

# Set defaults
log_level=${log_level:-INFO}
aws_region=${aws_region:-us-west-2}
cf_stack_name=${cf_stack_name:-esimport-serverless-us-west-2}
execution_timeout=${execution_timeout:-60}

echo "Building the template file"
sam build -t template.yaml

echo "Packaging artifact to ${deploy_s3_bucket}..."
sam package --output-template-file $(pwd)/packaged.yaml \
      --s3-bucket ${deploy_s3_bucket} \
      --s3-prefix esimport/sqs_consumer \
      --region ${aws_region}

echo "Deploying to ${aws_region}..."
sam deploy --template-file $(pwd)/packaged.yaml \
    --region ${aws_region} \
    --capabilities CAPABILITY_NAMED_IAM \
    --stack-name $cf_stack_name \
    --role-arn ${DEPLOYMENT_SERVICE_ROLE_ARN} \
    --parameter-overrides \
      RoleARN=${lambda_role_arn} \
      SNSTopicARN=${sns_topic_arn} \
      DPSKSNSTopicARN=${dpsk_sns_topic_arn} \
      EsUrl=${es_url} \
      SentryDsn=${sentry_dsn} \
      ExecutionTimeout=${execution_timeout} \
      LogLevel=${log_level} \
    --debug
