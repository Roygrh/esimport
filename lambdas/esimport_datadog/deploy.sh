#!/usr/bin/env bash
export SAM_CLI_TELEMETRY=0

#set -x
# Example
# bash ./deploy.sh \
#	<CloudFormation stack name> \
#	<S3 bucket to store lambda function deploy archive> \
#	<Number in minutes, that will be used to in queries to search last inserted doc > \
#	<ElasticsSearch server/cluser url> \
#	<DSN for Sentry> \
#	<Datadog API key> \
#	<Datadog host_name \
#	DEBUG


#There is a Circular dependency.
#Lambda function needs to know ElasticSearch url that can be taken after ElasticSearch stack will be created.
#But ElasticSearch stack need to know Lambda Role ARN to allow access. Role ARN will be available after CloudFormation stack with Lambda function will be created.
#So two options:
#- or use template to manually create Lambda IAM Role ARN ` "arn:aws:iam::{AWS Account id}:role/{IAM-ROLE-NAME}"`
#- or first deploy lambda function with fake EsUrl parameter, copy IAM ROLE ARN, update ElasticSearch Access policies. Then copy ElasticSearch url and updated CloudFormation lambda function stack with correct `EsUrl` parameter

if [[ $# -lt 6 ]]
  then
    echo "No enough arguments supplied"
    echo '$1 - CloudFormation stack name'
    echo '$2 - S3 bucket name to stored deploy file'
    echo '$3 - Number in minutes, for how much minutes function will be looking back to find latest document'
    echo '$4 - Url to ElasticSearch cluster/server'
    echo '$5 - Sentry DSN'
    echo '$6 - Datadog API Key'
    echo '$7 - Datadog Env, will be used as host_name param value in Datadog api call'
    echo '$8 - Optional, log level'
    exit
fi

cf_stack_name=$1
deploy_s3_bucket=$2 # bucket where archive with lambda code will be uploaded
lookback_x_minutes=$3 # number in minutes
es_url=$4 # ElasticSearch url
sentry_dsn=$5
datadog_api_key=$6
datadog_env=$7
log_level=$8

base_package='esimport_datadog'

mkdir -p package

pip install -r requirements.txt --target ./package
cp -f esimport_datadog.py ./package/


pushd package
zip -r ../${base_package}.zip ./*
popd
hash=$(sha256sum ${base_package}.zip | cut -c 1-64)
mv ${base_package}.zip ${hash}-${base_package}.zip

aws s3 cp ./${hash}-${base_package}.zip s3://${deploy_s3_bucket}/${hash}-${base_package}.zip
rm ${hash}-${base_package}.zip
rm -r package

aws cloudformation deploy \
  --capabilities CAPABILITY_NAMED_IAM \
  --stack-name ${cf_stack_name} \
  --template-file $(pwd)/standard-deploy.yaml \
  --parameter-overrides  \
    DeployS3Bucket=${deploy_s3_bucket} \
    LambdaS3Key=${hash}-${base_package}.zip \
    LookBackForXMinutes=${lookback_x_minutes} \
    EsUrl="${es_url}" \
    SentryDsn=${sentry_dsn} \
    DatadogAPIKey=${datadog_api_key} \
    DataDogEnv=${datadog_env} \
    LogLevel=${log_level}
