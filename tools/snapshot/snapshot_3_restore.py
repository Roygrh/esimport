import requests
import boto3
from requests_aws4auth import AWS4Auth
import settings
from helpers import check_errors

# Change it to target (encryption at rest enabled) es cluster endpoint
host = settings.ES_HOST_DESTINATION
region = settings.S3_BUCKET_REGION
service = 'es'
session = boto3.Session()
credentials = session.get_credentials()
awsauth = AWS4Auth(
    credentials.access_key, 
    credentials.secret_key, 
    region, 
    service, 
    session_token=credentials.token
)

# Get snapshot role arn
client = boto3.client('iam')
snapshot_role = client.get_role(
    RoleName=settings.ES_SNAPSHOT_ROLE
)
role_arn = snapshot_role['Role']['Arn']

path = '_snapshot/' + settings.ES_SNAPSHOT_REPO
url = host + path 

payload = {
  "type": "s3",
  "settings": {
    "bucket": settings.S3_BUCKET_NAME,
    "role_arn": role_arn
  }
}

if region == 'us-east-1':
  payload['settings'].update({'endpoint': 's3.amazonaws.com'})
else:
  payload['settings'].update({'region': region})

headers = {"Content-Type": "application/json"}

r = requests.put(
  url, 
  auth=awsauth, 
  json=payload, 
  headers=headers
)

check_errors(r)

### Restore snapshot

restore_path = '_snapshot/{}/{}/_restore'.format(settings.ES_SNAPSHOT_REPO, settings.ES_SNAPSHOT_NAME)
url = host+restore_path

payload = {
  "indices": settings.ES_INDEX_NAME,
  "ignore_unavailable": True,
  "include_global_state": True,
  "rename_pattern": ".kibana",
  "rename_replacement": "restored_.kibana"
}

r = requests.post(url, auth=awsauth, json=payload, headers=headers)

check_errors(r)
