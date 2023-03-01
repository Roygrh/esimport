#!/bin/bash
set -ex

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <Cross Account AWS Account Id>"
    exit 0
fi

export VedorAccountId=""
export REPOSITORY_NAME=esimport

if [[ -z "$VedorAccountId" ]]; then
    VedorAccountId=$(aws sts get-caller-identity --query 'Account' --output text)
fi

export CrossAccountId=$1

sed -i "s/aws_cross_account_number/$CrossAccountId/g" ecr_repository_policy.json

aws ecr set-repository-policy --registry-id $VedorAccountId \
    --repository-name $REPOSITORY_NAME --policy-text file://ecr_repository_policy.json



