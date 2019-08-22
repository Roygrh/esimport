#!/usr/bin/env bash

set -e

s3_bucket_name='int-tests-esimport-snapshot-bucket'
s3_bucket_region='us-west-2'
s3_stack_name='esimport-int-test-snapshot-bucket'

bash ./deploy-s3-bucket.sh\
	${s3_stack_name} \
	${s3_bucket_name}


es_stack_name='esimport-int-test-es-domain'
bash ./deploy-es-domain.sh \
	${es_stack_name} \
	int-tests-es-domain \
	${s3_bucket_name}


es_url=$(aws cloudformation describe-stacks --stack-name ${es_stack_name} \
--query 'Stacks[0].Outputs[?OutputKey==`ESUrl`].OutputValue | [0]' \
--output text)
s3_access_role_arn=$(aws cloudformation describe-stacks --stack-name ${es_stack_name} \
--query 'Stacks[0].Outputs[?OutputKey==`S3AccessRoleARN`].OutputValue | [0]' \
--output text)

# setting env variables

export ES_URLS=${es_url}
export SNAPSHOT_REPO_NAME='int-test-repo-name'
export ES_RETENTION_INDICES_PREFIXES='a-a-a,b-b-b,c-c-c'
export SENTRY_DSN=''
export ES_RETENTION_POLICY_MONTHS=18
export S3_BUCKET_NAME=${s3_bucket_name}
export S3_BUCKET_REGION=${s3_bucket_region}
export S3_ACCESS_ROLE_ARN=${s3_access_role_arn}

python -m pytest tests -x\
	--cov=esimport_retention_core\
	--cov=esimport_snapshot_creation\
	--cov=esimport_snapshot_verifier\
	--cov=esimport_retention\
	--cov-report=term-missing


# CloudFormation stack that define S3 will not be deleted if there are objects in bucket exists - emptying bucket
aws s3 rm s3://${s3_bucket_name} --recursive

aws cloudformation delete-stack --stack-name ${s3_stack_name}
aws cloudformation delete-stack --stack-name ${es_stack_name}

aws cloudformation wait stack-delete-complete --stack-name ${es_stack_name}
aws cloudformation wait stack-delete-complete --stack-name ${s3_stack_name}

