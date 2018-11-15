from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search # pip install elasticsearch-dsl
import requests

es = Elasticsearch()
s = Search(using=es, index="elevenos", doc_type="session")

s = s.source([])
ids = [h.meta.id for h in s.scan()]

amount = len(ids)
done = 0

data = '{"script" : "ctx._source.remove(\\"NetworkDeviceType\\")"}'

# loop through all documents with _type=session
for id in ids:
    response = requests.post('http://localhost:9200/elevenos/session/{0}/_update'.format(id), data=data)
    done+=1 # deleted field ["NetworkDeviceType"] (if present) from current document
    print("Deleted [\"NetworkDeviceType\"] at _id={0} \t\t [{1}/{2}]".format(id, done, amount))
