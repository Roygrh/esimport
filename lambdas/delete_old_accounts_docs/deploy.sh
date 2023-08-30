#!/usr/bin/env bash

# Disable AWS SAM Telemetry
export SAM_CLI_TELEMETRY=0

if [[ $# -lt 2 ]]
  then
    echo "No enough arguments supplied"
    echo '$1 - Stack name (for Cloudformation)'
    echo '$2 - Deploy Asset Bucket Name'
    echo '$3 - ElasticSearch host'
    echo '$4 - Log Level'
    echo '$5 - Aws region'
    exit
fi

cf_stack_name=$1
deploy_s3_bucket=$2 
es_url=$3
log_level=$4
aws_region=$5

# Set defaults
log_level=${log_level:-INFO}
aws_region=${aws_region:-us-west-2}

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
          IndexName="accounts" \
    --debug
