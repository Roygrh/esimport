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
host = 'https://search-esimport-test-7t44eh5b3x5x7a63eqkrtw7vfy.us-west-2.es.amazonaws.com/'
region = 'us-west-2'
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

path = '_snapshot/' + settings.ES_SNAPSHOT_REPO # my-snapshot-repo is the name of snapshot repository
url = host + path 

payload = {
  "type": "s3",
  "settings": {
    "bucket": settings.S3_BUCKET_NAME,
    "region": region,
    "role_arn": role_arn
  }
}

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
print("Snapshot done!")

