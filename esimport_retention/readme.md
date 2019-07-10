# General information

`standard-deploy.yaml` CloudFormation template that will deploy 3 lambda functions:
1. To create snapshot for indices that dedicated to data from previous month.
2. To verify state of snapshots that were create from indices dedicated to data from previous month.
3. Remove indices which older than defined retantion policy (in months), but only if snapshots exists for such indices.

Each functions will be triggerd by cron defined schedule
1. Snapshot creation on the 5th day in each month
2. Snapshot verifier on the 6th day in each month
3. Old indices deletetion on 15th day in each month

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
    --cov=esimport_retention_core\
    --cov=esimport_snapshot_creation\
    --cov=esimport_snapshot_verifier\
    --cov=esimport_retention\
    --cov-report=term-missing
```

# Deploy

1. lambda functions are require snapshot repository. Create it (S3 bucket). To do it you can use this command

```bash
bash ./deploy-s3-bucket.sh \
    <CloudFormation stack name> \
    <S3 bucket name>
```

2. ElasticSearch domain need suitable rights to be able register S3 bucket as snapshot repository.
`elasticsearch-domain-template.yaml` has example of rights.
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
    <S3 Bucket Name> \
    <Retention policy in months> \
    <ES endpoints/urls, comma separated strings> \
    <Sentry dsn> \
    <Indices prefixes, comm separated strings> \
    <Snapshot repo name>
    <Desired LOGLEVE>
````


