import boto3
import requests
from requests_aws4auth import AWS4Auth
import settings

# Get snapshot role arn
client = boto3.client('iam')
snapshot_role = client.get_role(
    RoleName=settings.ES_SNAPSHOT_ROLE
)
role_arn = snapshot_role['Role']['Arn']

# Change host to es cluster endpoint
host = settings.ES_HOST_SOURCE
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

print(r.status_code)
print(r.text)
print("Repo registration done.")

path = '_snapshot/{}/{}'.format(settings.ES_SNAPSHOT_REPO, settings.ES_SNAPSHOT_NAME)
url = host + path

r = requests.put(
  url,
  auth=awsauth
)

print(r.status_code)
print(r.text)
print("Snapshot process has started!")

