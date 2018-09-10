import boto3
import json

# Create a s3 bucket to store manual snapshot and use it's arn
S3_BUCKET = "arn:aws:s3:::esimport-snapshot-demo"

ES_SNAPSHOT_ROLE = 'esimport-trsut-relationship-demo'
ES_SNAPSHOT_POLICY = 'esimport-snapshot-policy'


# The role to create snapshot of existing es cluster
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

# Above role must have following policy attached
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

# Create snapshot role
role_response = client.create_role(
    RoleName=ES_SNAPSHOT_ROLE,
    AssumeRolePolicyDocument=json.dumps(trust_relationship_role)
)

# Create snapshot policy
policy_respone = client.create_policy(
    PolicyName=ES_SNAPSHOT_POLICY,
    PolicyDocument=json.dumps(es_snapshot_policy)
)

# snapshot_role = client.get_role(
#     RoleName=ES_SNAPSHOT_ROLE
# )
# role_arn = snapshot_role['Role']['Arn']
role_arn = role_response['Role']['Arn']
policy_arn = policy_respone['Policy']['Arn']

# Attach policy to snapshot role
attach_policy_response = client.attach_role_policy(
    RoleName=ES_SNAPSHOT_ROLE,
    PolicyArn=policy_arn
)

# # To delete role and policy
# delete_role = client.delete_role(RoleName=ES_SNAPSHOT_ROLE)
# delete_policy = client.delete_policy(
#     PolicyArn=policy_respone['Policy']['Arn']
# )
