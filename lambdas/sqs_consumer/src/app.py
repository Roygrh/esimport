import json
import logging
import os
from elasticsearch import Elasticsearch, helpers

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
log = logging.getLogger(__name__)
es = Elasticsearch("localhost:9200", timeout=30)


def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    # try:
    #     ip = requests.get("http://checkip.amazonaws.com/")
    # except requests.RequestException as e:
    #     # Send some context about this error to Lambda Logs
    #     print(e)

    #     raise e
    records_json_str = event.get('body')
    records =json.loads(records_json_str)

    number_of_records = len(records)
    log.info("About to index %d" % (number_of_records,))

    try:
        helpers.bulk(es, records, request_timeout=30)
    except helpers.BulkIndexError as bie:
        number_of_errors = len(bie.errors)
        conflict_errors = 0

        for error in bie.errors:
            if is_version_conflict_error(error):
                conflict_errors += 1

        log.warning(
            "Got %.2d errors, %.2d of which are IGNORED conflict errors."
            % (number_of_errors, conflict_errors)
        )

        if number_of_errors > conflict_errors:
            raise

    success_message = "Successfully indexed %.2d document(s)" % (number_of_records,)
    log.info(success_message)

    return {"message": success_message}


def is_version_conflict_error(error):
    for op_type, values in error.items():
        status = values.get('status')
        return status == 409
    return False
