import json


def sqs_msg_parser(msg_body):
    return list(map(lambda msg: json.loads(msg), msg_body.split("\n")))
