#!/usr/bin/env bash

# will deploy empty SNS and SQS for esimport
# Run it from the root direcotry of the project

# use us-west-2 region


aws cloudformation deploy \
    --template-file $(pwd)/cf_templates/staging_esimport_sns_sqs_without_consumers.yml \
    --stack-name esimport-sns-sqs-staging \
