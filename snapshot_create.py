import boto3
import requests
from requests_aws4auth import AWS4Auth


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

path = '_snapshot/my-snapshot-repo' # the Elasticsearch API endpoint
url = host + path 

payload = {
  "type": "s3",
  "settings": {
    "bucket": "esimport-snapshot-demo",
    "region": "us-west-2",
    "role_arn": "arn:aws:iam::278533050534:role/esimport-trsut-relationship-demo"
  }
}

headers = {"Content-Type": "application/json"}

r = requests.put(url, auth=awsauth, json=payload, headers=headers)

print(r.status_code)
print(r.text)

