#
# Dockerfile for DynamoDB Local
#
# https://aws.amazon.com/blogs/aws/dynamodb-local-for-desktop-development/
#
FROM openjdk:8-jre

# Create working space
WORKDIR /var/dynamodb_wd

# Default port for DynamoDB Local
# EXPOSE 8000


ADD log4j.properties /var/dynamodb_wd
ADD log4j2.xml /var/dynamodb_wd

# Get the package from Amazon
RUN wget -O /tmp/dynamodb_local_latest https://s3-us-west-2.amazonaws.com/dynamodb-local/dynamodb_local_latest.tar.gz && \
    tar xfz /tmp/dynamodb_local_latest && \
    rm -f /tmp/dynamodb_local_latest &&\
    mkdir -p /var/dynamodb_local && \
    # change logs settings
    export DEBIAN_FRONTEND=noninteractive && \
    apt-get -yq update && \
    apt-get -yq upgrade && \
	apt-get -yq install zip && \
    zip -d DynamoDBLocal.jar log4j.properties log4j2.xml && \
    zip -u DynamoDBLocal.jar log4j.properties log4j2.xml


# to save in file set cmd parameter "-dbPath /var/dynamodb_local"

# Default command for image
ENTRYPOINT ["/usr/bin/java", "-Djava.library.path=.", "-jar", "DynamoDBLocal.jar"]
CMD ["-port", "8000", "-inMemory"]


# Add VOLUMEs to allow backup of config, logs and databases
# VOLUME ["/var/dynamodb_local", "/var/dynamodb_wd"]


