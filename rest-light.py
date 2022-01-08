##################################################
# Imports & Global variables
##################################################
from flask import Flask
import os
import logging
import re
import string
import random

app = Flask(__name__)
LOADED_API_KEY = None                          # Stores the current valid api-key
basepath = "/etc/rest-light"
api_key_path = basepath + "/api-key.txt"

##################################################
# function for api-key validation
##################################################
# loads key on app startup
def load_key():
    # exit if key already defined
    if LOADED_API_KEY is not None:
        return

    # try to open persistence file
    key_tmp = None
    try:
        with open(api_key_path, 'r') as f:
            lines = f.readlines()
            key_tmp = re.search("\w+", lines[0])
    except:
        logging.info('No API-Key found, generating new one')

    # return key
    if key_tmp is not None:
        return key_tmp
    else:
        new_key = ''.join(random.choices(
            string.ascii_lowercase + string.ascii_uppercase + string.digits, k=42))
        # persists key
        with open(api_key_path, 'w') as f:
            f.write(new_key)
        # return key
        return new_key

# function to check, if a provided api-key is valid
def check_access(input_api_key: str):
    if input_api_key == LOADED_API_KEY:
        return True
    else:
        return False

##################################################
# Flask routes
##################################################
# status page
@app.route('/')
def hello():
    return 'Running <a href="https://gihub.com/' + os.getenv('GITHUB_REPOSITORY') + '">REST-Light</a> Version ' + os.getenv('APP_VERSION')


##################################################
# Main call
##################################################
if __name == '__main__':
    LOADED_API_KEY = load_key()
    app.run(debug=True, host='0.0.0.0')
