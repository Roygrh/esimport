#!/usr/bin/env bash

#set -x

# Example
#bash ./deploy.sh \
#	<CloudFormation stack name> \
#	<S3 Bucket Name> \
#	18 \
#	http://admin:asdf@localhost:9200,http://admin:asdf@localhost:92001 \
#	<Sentry dsn> \
#	devices,accounts,sessions \
#	<Snapshot repo name>
#	DEBUG


if [[ $# -lt 6 ]]
  then
    echo "No enough arguments supplied"
    echo '$1 - CloudFormation stack name'
    echo '$2 - S3 bucket name to stored deploy file'
    echo '$3 - Number in months, that represent retention policy'
    echo '$4 - Urls to ElasticSearch clusters/servers, delimited by commas'
    echo '$5 - Sentry DSN'
    echo '$6 - Indices prefixes that will be processed, strings delimited by commas'
    echo '$7 - Repo name'
    echo '$7 - Optional, log level'
    exit
fi

cf_stack_name=$1
deploy_s3_bucket=$2 # bucket where archive with lambda code will be uploaded
retention_policy=$3 # number in months
es_urls=$4 # ElasticSearch urls delimited by comma
sentry_dsn=$5
indices_prefixes=$6
repo_name=$7
log_level=$8

base_package='esimport_retention'

mkdir -p package

pip install -r requirements.txt --target ./package
cp -f esimport_retention_core.py ./package/
cp -f esimport_snapshot_creation.py ./package/
cp -f esimport_snapshot_verifier.py ./package/
cp -f esimport_retention.py ./package/

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
    EsRetentionPolicyMonths=${retention_policy} \
    EsUrls="${es_urls}" \
    SentryDsn=${sentry_dsn} \
    IndicesPrefixes=${indices_prefixes} \
    RepoName=${repo_name} \
    LogLevel=${log_level}
