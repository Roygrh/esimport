#!/usr/bin/env bash

# Disable AWS SAM Telemetry
export SAM_CLI_TELEMETRY=0
set -e

if [[ $# -lt 2 ]]
  then
    echo "No enough arguments supplied"
    echo '$1 - Deploy Asset Bucket Name (temporary place to store deploy asset)'
    echo '$2 - ElasticSearch host'
    echo '$3 - Datadog API key'
    exit
fi

deploy_s3_bucket=$1
es_url=$2
datadog_api_key=$3
log_level=$LOG_LEVEL
aws_region=$AWS_REGION
cf_stack_name=$STACK_NAME
es_cluster_east_arn=$ES_CLUSTER_EAST_ARN
es_cluster_west_arn=$ES_CLUSTER_WEST_ARN

# Set defaults
log_level=${log_level:-DEBUG}
aws_region=${aws_region:-us-west-2}
cf_stack_name=${cf_stack_name:-esimport-delete-old-accounts-docs}
index_name=${index_name:-accounts}
# the default below is for reporting_staging ES cluster
es_cluster_east_arn=${ES_CLUSTER_EAST_ARN:-arn:aws:es:*:265848155493:domain/*}
es_cluster_west_arn=${ES_CLUSTER_WEST_ARN:-arn:aws:es:*:265848155493:domain/*}

echo "Building the template file"
sam build -t template.yaml 

echo "Packaging artifact to ${deploy_s3_bucket}..."
sam package --output-template-file $(pwd)/packaged.yaml \
      --s3-bucket ${deploy_s3_bucket} \
      --s3-prefix esimport/delete_old_account_docs \
      --region ${aws_region}

echo "Deploying to ${aws_region}..."
sam deploy --template-file $(pwd)/packaged.yaml \
    --region ${aws_region} \
    --capabilities CAPABILITY_NAMED_IAM \
    --stack-name $cf_stack_name \
    --parameter-overrides \
          EsUrl=${es_url} \
          LogLevel=${log_level} \
          DatadogApiKey=${datadog_api_key} \
          IndexName=${index_name} \
          EsClusterEastArn=${es_cluster_east_arn} \
          EsClusterWestArn=${es_cluster_west_arn} \
    --debug
