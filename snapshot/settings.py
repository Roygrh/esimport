# Create a s3 bucket to store manual snapshot and use it's arn
S3_BUCKET_ARN = 'arn:aws:s3:::esimport-snapshot-mark'
S3_BUCKET_NAME = 'dataservices.elasticsearch.snapshot'
S3_BUCKET_REGION = 'us-west-2'

ES_SNAPSHOT_ROLE = 'es-snapshot-role'
ES_SNAPSHOT_POLICY = 'es-snapshot-policy'

ES_SNAPSHOT_REPO = 'es-snapshot-repo'
ES_SNAPSHOT_NAME = 'es-snapshot'

ES_HOST_SOURCE = 'https://search-esimport-test-7t44eh5b3x5x7a63eqkrtw7vfy.us-west-2.es.amazonaws.com/'
ES_HOST_DESTINATION = 'https://search-esimport-test-ear-rtldagkp6iu5ohy2h2f6rzmcky.us-west-2.es.amazonaws.com/'

ES_INDEX_NAME = 'esrecord'
