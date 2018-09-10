import requests
import boto3
from requests_aws4auth import AWS4Auth

S3_BUCKET_NAME = 'esimport-snapshot-demo'
ES_SNAPSHOT_ROLE = 'esimport-trsut-relationship-demo'
ES_INDEX_NAME = 'esrecord'

# Change it to target (encryption at rest enabled) es cluster endpoint
host = 'https://search-esimport-test-ear-rtldagkp6iu5ohy2h2f6rzmcky.us-west-2.es.amazonaws.com/'
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

# Get snapshot role arn
client = boto3.client('iam')
snapshot_role = client.get_role(
    RoleName=ES_SNAPSHOT_ROLE
)
role_arn = snapshot_role['Role']['Arn']

path = '_snapshot/my-snapshot-repo' # my-snapshot-repo is the name of previously taken snapshot repository
url = host + path 

payload = {
  "type": "s3",
  "settings": {
    "bucket": S3_BUCKET_NAME,
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

### Restore snapshot

restore_path = '_snapshot/my-snapshot-repo/esimport-snapshot-demo/_restore'
url = host+restore_path

payload = {"indices": ES_INDEX_NAME}

r = requests.post(url, auth=awsauth, json=payload, headers=headers)

print(r.status_code)
print(r.text)

