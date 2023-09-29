"""
    Usage: python encrypt_objects.py
    Set proper aws credentials first
    this script was created for OS-2550
    after ticket is shipped, evaluate weather we need this scriptt &
    do cleanup
"""

import boto3

# All distrodev buckets in monolith_dev
buckets = [
    "gpns-report-ui-prod",
    "reporting-prod-nested-stacks-tmpdir",
    "lambda-artifacts-11",
    "eleven-prod-lambda-artifacts",
    "dataservices.esimport.production"
    ]


s3 = boto3.resource("s3")
client = boto3.client("s3")
data = {}

print("making list of objects & writing to file -> bucket_data.csv")
with open("bucket_data.csv","a") as f:
    for bucket in buckets:
        print(f"*************{bucket}*************\n")
        bucket_res = s3.Bucket(bucket)
        try:
            for obj in bucket_res.objects.all():
                key = s3.Object(bucket_res.name, obj.key)
                try:
                    if key.server_side_encryption == None:
                        print(f"{bucket}.....{obj.key}")
                        f.writelines(f"{bucket_res.name},{key.server_side_encryption},{obj.key}\n")
                except Exception as e:
                    print(f"{bucket} {e}.....{obj.key}")
                    f.writelines(f"{bucket_res.name},{e},{obj.key}\n")
        except Exception as e:
            print(e)
            pass

print("reading objects' key from file -> bucket_data.csv")
object_list = []

# csv data is in this format
# bucket_name, object_encryption, object_key
with open("bucket_data.csv","r") as f:
    for line in f.readlines():
        line = line.split(",")
        line[2] = line[2].strip("\n")
        object_list.append(line)
# Since all buckets will have encryption turned on by default as stated by amazon
# copying & replacing object will encrypt them
print("encrypting objects & logging error to file -> copy_error_logs.csv")
with open("copy_error_logs.csv","w") as f:
    for obj in object_list:
        bucket_name = obj[0]
        obj_encryption = obj[1]
        obj_key = obj[2]

        copy_source = {
            'Bucket': bucket_name,
            'Key': obj_key
        }

        try:
            s3.meta.client.copy(copy_source, bucket_name, obj_key)
        except Exception as e:
            print(f"{bucket_name}, {e}, {obj_key}\n")
            f.write(f"{bucket_name}, {e}, {obj_key}\n")

