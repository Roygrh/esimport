import requests
import json
import sys
import time

params = (
    ('conflicts', 'proceed'),
    ('wait_for_completion', 'false') # Will return a task ID when querying
)

data = '{ "script": { "inline": "ctx._source.remove(\\"NetworkDeviceType\\")" }, "query": { "match_all":{} } }'

response = requests.post('http://localhost:9200/elevenos/session/_update_by_query', params=params, data=data)

task_id = response.json()["task"] # Print task ID

print("{0}\n".format(task_id))

params = (
            ('pretty', 'true'),
            )

update_interval = 60

# Print task status until completion
while True:
    # Checking status of task by querying Task API with task ID
    response = requests.get('http://localhost:9200/_tasks/{0}'.format(task_id), params=params)

    r = response.json()

    print(json.dumps(r, indent=4, sort_keys=True))

    if r['completed'] == True:
        exit(0)
    else:
        time.sleep(update_interval) # sleep when task not  completed
