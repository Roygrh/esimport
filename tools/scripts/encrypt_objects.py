"""
    Usage: python encrypt_objects.py bucket_name
    Set proper aws credentials first
    this script was created for OS-2550
    after ticket is shipped, evaluate weather we need this scriptt &
    do cleanup
"""

import boto3
import sys

# All distrodev buckets in monolith_dev
# do this one by one
# buckets = [
    # "gpns-report-ui-prod",
    # "reporting-prod-nested-stacks-tmpdir",
    # "lambda-artifacts-11",
    # "eleven-prod-lambda-artifacts",
    # "dataservices.esimport.production"
    # ]


s3 = boto3.resource("s3")
client = boto3.client("s3")
data = {}
bucket = sys.argv[1]

print(f"making list of objects & writing to file -> {bucket}.csv")
with open(f"{bucket}.csv","a") as f:
    bucket_res = s3.Bucket(bucket)
    for obj in bucket_res.objects.all():
        key = s3.Object(bucket_res.name, obj.key)
        if key.server_side_encryption == None:
            print(f"{bucket}.....{obj.key}")
            f.write(f"{bucket_res.name},{key.server_side_encryption},{obj.key}\n")
    print("ok\n**********")

print("reading objects' key from file -> bucket_data.csv")
object_list = []
# csv data is in this format
# bucket_name, object_encryption, object_key
with open(f"{bucket}.csv","r") as f:
    for line in f.readlines():
        line = line.split(",")
        line[2] = line[2].strip("\n")
        object_list.append(line)
    print("ok\n**********")

# Since all buckets will have encryption turned on by default as stated by amazon
# copying & replacing object will encrypt them
print(f"encrypting objects & logging error to file -> {bucket}_error_logs.csv")
with open(f"{bucket}_error_logs.csv","w") as f:
    for obj in object_list:
        bucket_name = obj[0]
        obj_encryption = obj[1]
        obj_key = obj[2]

        copy_source = {
            'Bucket': bucket_name,
            'Key': obj_key
        }
        s3.meta.client.copy(copy_source, bucket_name, obj_key)
    print("ok\n**********")