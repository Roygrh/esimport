from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search # pip install elasticsearch-dsl
import requests

es = Elasticsearch()
s = Search(using=es, index="elevenos", doc_type="property")

s = s.source([])
ids = [h.meta.id for h in s.scan()]                                                                                                                                                                                  

amount = len(ids)
done = 0 

data = '{"script" : "ctx._source.remove(\\"ServiceAreas\\")"}'

# loop through all documents with _type=property
for id in ids:
    response = requests.post('http://localhost:9200/elevenos/property/{0}/_update'.format(id), data=data)
    done+=1 # deleted field ["ServiceAreas"] (if present) from current document
    print("Deleted [\"ServiceAreas\"] at _id={0} \t\t [{1}/{2}]".format(id, done, amount))