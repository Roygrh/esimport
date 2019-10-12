# General information

`standard-deploy.yaml` CloudFormation template that will deploy 1 lambda functions, that will try to find the latest document indexed by ElasticSearch, and will report the latest timestamp to Datadog service.

Function will be triggered by CloudWatch rule. Default time interval - 3 minutes
Exception that will may happens during lambda function execution will be recorded in Sentry service

For more information read `standard-deploy.yaml` template


# Testing

Note that tests require some python libs, see `requirements.txt` and `dev-requirements.txt`.

To run integration tests use this command

`bash run-integration-tests.sh`

To run unit tests use this command

`bash run-unit-tests.sh`


# Deploy

1. ElasticSearch domain needs to be configured to allow access from Lambda function.
`elasticsearch-domain-template.yaml` has example of rights. Use this snipped from CloudFormation template as example to define appropriate Access Policy.

#- Effect: Allow
#    Principal:
#      AWS: arn:aws:iam::{AWS Account id}:role/{IAM-ROLE-NAME}
#    Action: 'es:*'
#    Resource: !Sub 'arn:aws:es:us-west-2:${AWS::AccountId}:domain/${ESDomainName}/*'


Also see deploy.sh for more information

2. To deploy lambda functions use this command

```bash
bash ./deploy.sh \
	<CloudFormation stack name> \
	<S3 bucket to store lambda function deploy archive> \
	<Number in minutes, that will be used to in queries to search last inserted doc > \
	<ElasticsSearch server/cluser url> \
	<DSN for Sentry> \
	<Datadog API key> \
	<Datadog host_name \
	<Desired LOGLEVEL>
````
