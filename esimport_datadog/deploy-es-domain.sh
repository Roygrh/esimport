#!/usr/bin/env bash

if [[ $# -lt 3 ]]
  then
    echo "No enough arguments supplied"
    echo '$1 - CloudFormation stack name'
    echo '$2 - ES domain name'
    echo '$3 - LambdaRoleArn, optional, needs to grant permission for lambda functions to get access ES Domain '
    exit
fi

cf_stack_name=$1
es_domain=$2
role_arn=${3:-''}


aws cloudformation deploy \
  --stack-name ${cf_stack_name} \
  --capabilities CAPABILITY_NAMED_IAM \
  --template-file $(pwd)/elasticsearch-domain-template.yaml \
  --parameter-overrides  \
    ESDomainName=${es_domain} \
    LambdaRoleArn=${role_arn}
