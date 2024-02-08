#!/usr/bin/env bash

# Disable AWS SAM Telemetry
export SAM_CLI_TELEMETRY=0
set -e

if [[ $# -lt 8 ]]; then
  echo "No enough arguments supplied"
  echo '$1 - Stack name (for Cloudformation)'
  echo '$2 - S3 bucket name to store the artifact file'
  echo '$3 - Number in minutes, for how long this Lambda function will be looking back to find latest document'
  echo '$4 - Url to ElasticSearch cluster/server'
  echo '$5 - Datadog API Key'
  echo '$6 - AWS Region to deploy to. Will also be used as host_name param value in Datadog api call as well'
  echo '$7 - RoleARN to be assumed by lambda'
  echo '$8 - Service role arn that cloudformation uses to perform deployment'
  exit
fi

cf_stack_name=$1
deploy_s3_bucket=$2
lookback_x_minutes=$3
es_url=$4
datadog_api_key=$5
aws_region=$6
role_arn=$7
DEPLOYMENT_SERVICE_ROLE_ARN=$8

echo "Building the template file"
sam build -t template.yaml

echo "Packaging artifact to ${deploy_s3_bucket}..."
sam package \
  --output-template-file $(pwd)/packaged.yaml \
  --s3-bucket ${deploy_s3_bucket} \
  --s3-prefix esimport/esimport_datadog \
  --region ${aws_region}

echo "Deploying to ${aws_region}..."
sam deploy --template-file $(pwd)/packaged.yaml \
  --region ${aws_region} \
  --capabilities CAPABILITY_NAMED_IAM \
  --stack-name ${cf_stack_name} \
  --parameter-overrides \
  DataDogEnv=${aws_region} \
  DatadogAPIKey=${datadog_api_key} \
  RoleARN=${role_arn} \
  EsUrl=${es_url} \
  LookBackForXMinutes=${lookback_x_minutes} \
  --debug \
  --role-arn ${DEPLOYMENT_SERVICE_ROLE_ARN} \
  --no-fail-on-empty-changeset
