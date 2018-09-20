####################
# PRODUCTION - WEST
####################

# Create a s3 bucket to store manual snapshot and use it's arn
S3_BUCKET_ARN = 'arn:aws:s3:::dataservices.elasticsearch.production'
S3_BUCKET_NAME = 'dataservices.elasticsearch.production'
S3_BUCKET_REGION = 'us-west-2'

ES_SNAPSHOT_ROLE = 'es-snapshot-role'
ES_SNAPSHOT_POLICY = 'es-snapshot-policy'

ES_SNAPSHOT_REPO = 'es-snapshot-repo'
ES_SNAPSHOT_NAME = 'es-snapshot'

ES_HOST_SOURCE = 'https://search-elevenapi-umjus7tn4tv246xajqgflsivou.us-west-2.es.amazonaws.com/'
ES_HOST_DESTINATION = 'https://search-elevenapi-west-dhoralah2afgwov7iyu7hd74u4.us-west-2.es.amazonaws.com/'

ES_INDEX_NAME = '*'


##########
# STAGING
##########

# # Create a s3 bucket to store manual snapshot and use it's arn
# S3_BUCKET_ARN = 'arn:aws:s3:::dataservices.elasticsearch'
# S3_BUCKET_NAME = 'dataservices.elasticsearch'
# S3_BUCKET_REGION = 'us-east-1'
# 
# ES_SNAPSHOT_ROLE = 'es-snapshot-role'
# ES_SNAPSHOT_POLICY = 'es-snapshot-policy'
# 
# ES_SNAPSHOT_REPO = 'es-snapshot-repo'
# ES_SNAPSHOT_NAME = 'es-snapshot'
# 
# ES_HOST_SOURCE = 'https://search-elevenapi-staging-wcpgd2s6avtogdhz5nkey4vroq.us-east-1.es.amazonaws.com/'
# ES_HOST_DESTINATION = 'https://search-elevenapi-staging-encrypted-tcudtqjbw4a7otqmoc2wni53zu.us-east-1.es.amazonaws.com/'
# 
# ES_INDEX_NAME = '*'
