#!/usr/bin/env bash

# Disable AWS SAM Telemetry
export SAM_CLI_TELEMETRY=0

if [[ $# -lt 2 ]]
  then
    echo "No enough arguments supplied"
    echo '$1 - Deploy Asset Bucket Name (temporary place to store deploy asset)'
    echo '$2 - ElasticSearch host'
    echo '$3 - Datadog API key'
    echo '$4 - Stack name (for Cloudformation) (optional)'
    echo '$5 - Log Level (optional)'
    echo '$6 - Aws region (optional)'
    exit
fi

deploy_s3_bucket=$1
es_url=$2
datadog_api_key=$3
cf_stack_name=$4
log_level=$5
aws_region=$6

# Set defaults
log_level=${log_level:-INFO}
aws_region=${aws_region:-us-west-2}
cf_stack_name=${cf_stack_name:-esimport-delete-old-accounts-docs}

echo "Building the template file"
sam build -t template.yaml 

echo "Packaging artifact to ${deploy_s3_bucket}..."
sam package --output-template-file $(pwd)/packaged.yaml \
      --s3-bucket ${deploy_s3_bucket} \
      --s3-prefix esimport/delete_old_account_docs

echo "Deploying to ${aws_region}..."
sam deploy --template-file $(pwd)/packaged.yaml \
    --region ${aws_region} \
    --capabilities CAPABILITY_NAMED_IAM \
    --stack-name $cf_stack_name \
    --parameter-overrides \
          EsUrl=${es_url} \
          LogLevel=${log_level} \
          DatadogApiKey=${datadog_api_key} \
          IndexName="accounts" \
    --debug
