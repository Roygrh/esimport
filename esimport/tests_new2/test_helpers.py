import json
from time import sleep


def sqs_msg_parser(msg_body):
    return list(map(lambda msg: json.loads(msg), msg_body.split("\n")))


def fetch_sqs_messages(sqs_q):
    messages = None
    for _ in range(15):
        messages = sqs_q.receive_messages()
        if messages:
            break

        sleep(1)

    assert messages is not None
    return messages
