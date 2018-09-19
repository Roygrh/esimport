import requests
import boto3
from requests_aws4auth import AWS4Auth
import settings

# Reindex restored_.kibana to .kibana

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

headers = {"Content-Type": "application/json"}

reindex_path = '_reindex'
url = host + reindex_path

payload = {
  "source": {
    "index": "restored_.kibana"
  },
  "dest": {
    "index": ".kibana"
  }
}

r = requests.post(url, auth=awsauth, json=payload, headers=headers)

print(r.status_code)
print(r.text)
