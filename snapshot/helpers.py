import sys
import requests
from requests.exceptions import HTTPError

# check for error in response
def check_errors(response):
    if response.status_code != requests.codes.ok:
        print(response.text)
        response.raise_for_status()
        # return sys.exit('Error: {}'.format(response.json()['error']['reason']))

    print(response.status_code)
    print(response.text)
