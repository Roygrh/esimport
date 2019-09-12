Docker container for AWS DynamoDB Local

AWS DynamoDB Local will let you test against DynamoDB without needing
a full network. For details see https://aws.amazon.com/blogs/aws/dynamodb-local-for-desktop-development/

To use link to your application:

    sudo docker run -d --name dynamodb deangiberson/aws-dynamodb-local

    sudo docker run -d -P --name web --link dynamodb:dynamodb training/webapp python app.py
    

By default db stored in memory and on 8000 port, to override this run with arguments
-dbPath /var/path_to_dir
-port PORT_NUMBER
 
	sudo docker run -d -t dynamodb-inmemory -port 8000 -dbPath /var

where dynamodb-inmemory name of your container
    

