from typing import Tuple, Dict, Any
from elasticsearch import Elasticsearch

# Initialize Elasticsearch client (adjust hosts as needed)
es = Elasticsearch(hosts=[{"host": "localhost", "port": 9200}])
INDEX_NAME = "devices"  # Elasticsearch index name

def to_bulk_action(record) -> Tuple[Dict[str, Dict[str, str]], Dict[str, Any]]:
    """
    Prepare a single bulk action for Elasticsearch.
    Omits the 'id' field so that ES auto-generates its own _id.
    """
    action = {"index": {"_index": INDEX_NAME}}
    document = record.dict(exclude_none=True)
    return action, document

def send_to_es(actions: list):
    """
    Send a batch of bulk actions to Elasticsearch.
    `actions` should be a flat list: [action1, doc1, action2, doc2, ...]
    """
    es.bulk(body=actions)
