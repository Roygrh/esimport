#!/usr/bin/env bash

if [[ $# -lt 2 ]]
  then
    echo "No enough arguments supplied"
    echo '$1 - CloudFormation stack name'
    echo '$2 - S3 bucket name'
    exit
fi

cf_stack_name=$1
s3_bucket=$2


aws cloudformation deploy \
  --stack-name ${cf_stack_name} \
  --template-file $(pwd)/s3-for-snapshots.yaml \
  --parameter-overrides  \
    BucketName=${s3_bucket} \
