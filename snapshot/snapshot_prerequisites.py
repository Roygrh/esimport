import boto3
import json
import settings

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
                settings.S3_BUCKET_ARN
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
                settings.S3_BUCKET_ARN + "/*"
            ]
        }
    ]
}

client = boto3.client('iam')

# Create snapshot role
role_response = client.create_role(
    RoleName=settings.ES_SNAPSHOT_ROLE,
    AssumeRolePolicyDocument=json.dumps(trust_relationship_role)
)

print("Role creation complete.")

# Create snapshot policy
policy_respone = client.create_policy(
    PolicyName=settings.ES_SNAPSHOT_POLICY,
    PolicyDocument=json.dumps(es_snapshot_policy)
)

print("Policy creation complete.")

# snapshot_role = client.get_role(
#     RoleName=ES_SNAPSHOT_ROLE
# )
# role_arn = snapshot_role['Role']['Arn']
role_arn = role_response['Role']['Arn']
policy_arn = policy_respone['Policy']['Arn']

# Attach policy to snapshot role
attach_policy_response = client.attach_role_policy(
    RoleName=settings.ES_SNAPSHOT_ROLE,
    PolicyArn=policy_arn
)

print("Policy attached to Role.")
