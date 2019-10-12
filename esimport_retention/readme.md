# General information

`standard-deploy.yaml` CloudFormation template that will deploy 3 lambda functions:
1. To create snapshot for indices that dedicated to data from previous month.
2. To verify state of snapshots that were create from indices dedicated to data from previous month.
3. Remove indices which older than defined retention policy (in months), but only if snapshots exists for such indices.

Each functions will be triggered by cron defined schedule
1. Snapshot creation on the 5th day in each month
2. Snapshot verifier on the 6th day in each month
3. Old indices deletion on 15th day in each month

Exception that will may happens during lambda function execution will be recorded in Sentry service

For more information read `standard-deploy.yaml` template

There is also exists cli tool `esimport_snapshot_cli.py` that can be used for manual testing and operations like registering snapshot repository.
For available commands see tool helps `python -m esimport_snapshot_cli -h`


# Testing

Note that tests require some python libs, see `requirements.txt` and `dev-requirements.txt`.

To run integration tests use this command

`bash run-integration-tests.sh`

It will take a long time

To run unit tests use this command

```bash
python -m pytest tests/unit_tests -x\
    --cov=esimport_retention_core \
    --cov-report=term-missing
```

# Deploy

There is a Circular dependency.
Lambda function needs to know ElasticSearch urls that can be taken after ElasticSearch stack/stacks will be created.
But ElasticSearch stack need to know Lambda Role ARN to allow access. Role ARN will be available after CloudFormation stack with Lambda functions will be created.
So two options:
- or use template to manually create Lambda IAM Role ARN ` "arn:aws:iam::{AWS Account id}:role/{IAM-ROLE-NAME}"`
- or first deploy lambda functions with fake EsUrls parameter, copy IAM ROLE ARN, update ElasticSearch Access policies. Then copy ElasticSearch urls and update CloudFormation lambda function stack with correct `EsUrls` parameter


1. lambda functions are require snapshot repository. Create it (S3 bucket). To do it you can use this command

```bash
bash ./deploy-s3-bucket.sh \
    <CloudFormation stack name> \
    <S3 bucket name>
```

2. ElasticSearch domain need suitable rights to be able register S3 bucket as snapshot repository and grant access from lambda function.
`elasticsearch-domain-template.yaml` has example how to assign appropriate rights.
First create IAM role, `S3AccessRole` resource from template.
Next, add to ElasticSearch domain `AccessPolices` policy that grant create IAM role access to ElasticSearch domain.
Example of such policy also in `elasticsearch-domain-template.yaml` template file

Ideally if already deployed (production) ElasticSearch domains uses CloudFormation templates. These templates should be udpated.


2. S3 bucket should be registered as repository. Use this command to do it

```bash
python -m esimport_snapshot_cli \
    register-repository \
    <ElasticSearch domain endpoint/url> \
    -s3-bucket \
        <S3 Bucket name> \
        <S3 bucket region>  \
    -arn <ARN of IAM role that will be used to access S3 bucket> \
    -repo-name <New repository name>
```


3. To deploy lambda functions use this command

```bash
bash ./deploy.sh \
    <CloudFormation stack name> \
    <S3 Bucket Name, to store lambda function code> \
    <Retention policy in months> \
    <ES endpoints/urls, comma separated strings> \
    <Sentry dsn> \
    <Indices prefixes, comma separated strings> \
    <Snapshot repo name>
    <Desired LOGLEVE>
````


