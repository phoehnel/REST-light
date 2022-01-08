##################################################
# Imports & Global variables
##################################################
from flask import Flask
import os
import logging
import re
import string
import sys
import random

app = Flask(__name__)
LOADED_API_KEY = None                          # Stores the current valid api-key
basepath = "/etc/rest-light"
api_key_path = basepath + "/api-key.txt"

##################################################
# utility functions
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
        try:
            with open(api_key_path, 'w') as f:
                f.write(new_key)
        except:
            logging.info('Could not save API-Key in the following folder. Ensure permissions are correct! ' + basepath)
            sys.exit()

        # return key and log
        logging.warning('##################################################')
        logging.warning('Generated API-Key: ' + new_key)
        logging.warning('##################################################')
        return new_key

# function to check, if a provided api-key is valid
def check_access(input_api_key: str):
    if input_api_key == LOADED_API_KEY:
        return True
    else:
        return False

# setup logging on startup
def setup_logging():
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s:%(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)

##################################################
# Flask routes
##################################################
# status page
@app.route('/')
def hello():
    return 'Running <a href="https://github.com/' + str(os.getenv('GITHUB_REPOSITORY')) + '">REST-Light</a> Version ' + str(os.getenv('APP_VERSION'))


##################################################
# Main call
##################################################
if __name__ == '__main__':
    # init
    setup_logging()
    LOADED_API_KEY = load_key()
    # serve
    app.run(debug=True, host='0.0.0.0', port=4242)
