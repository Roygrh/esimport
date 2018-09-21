import sys

# check for error in response
def check_errors(response):
    if response.json().get('error'):
        return sys.exit('Error: {}'.format(response.json()['error']['reason']))
    print(response.status_code)
    print(response.text)
