import sys
import boto3
import settings

client = boto3.client('iam')

policy_arn = ''

policies = client.list_policies(OnlyAttached=True)
for policy in policies['Policies']:
    if policy['PolicyName'] == settings.ES_SNAPSHOT_POLICY:
        policy_arn = policy['Arn']

if not policy_arn:
    sys.exit("Policy Arn not found.")

try:
    client.detach_role_policy(RoleName=settings.ES_SNAPSHOT_ROLE, PolicyArn=policy_arn)
    client.delete_policy(PolicyArn=policy_arn)
    client.delete_role(RoleName=settings.ES_SNAPSHOT_ROLE)
    print("Role: {0} and Policy: {1} removed.".format(settings.ES_SNAPSHOT_ROLE, settings.ES_SNAPSHOT_POLICY))
except Exception as e:
    print("Unexpected error: {}".format(e))
