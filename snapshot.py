import boto3
import json

S3_BUCKET = "arn:aws:s3:::esimport-snapshot-demo"

trust_relationship_role = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "",
            "Effect": "Allow",
            "Principal": {
                "Service": "es.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}

es_snapshot_policy = {
    "Version":"2012-10-17",
    "Statement":[
        {
            "Action":[
                "s3:ListBucket"
            ],
            "Effect":"Allow",
            "Resource":[
                S3_BUCKET
            ]
        },
        {
            "Action":[
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "iam:PassRole"
            ],
            "Effect":"Allow",
            "Resource":[
                S3_BUCKET + "/*"
            ]
        }
    ]
}

client = boto3.client('iam')

role_response = client.create_role(
    RoleName='esimport-trsut-relationship-demo',
    AssumeRolePolicyDocument=json.dumps(trust_relationship_role)
)

policy_respone = client.create_policy(
    PolicyName='esimport-snapshot-policy',
    PolicyDocument=json.dumps(es_snapshot_policy)
)

role_arn = client.get_role(RoleName='esimport-trsut-relationship-demo')['Role']['Arn']
policy_arn = client.get_policy(Role)
attach_policy_response = client.attach_role_policy(
    RoleName='esimport-trsut-relationship-demo',
    PolicyArn='arn:aws:iam::278533050534:policy/esimport-snapshot-policy'
)

print(role_response)
print(policy_respone)
