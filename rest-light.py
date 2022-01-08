##################################################
# Imports & Global variables
##################################################
from flask import Flask, request
import os
import logging
import re
import string
import subprocess
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
            key_tmp = re.findall("\w+", lines[0])[0]
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
def check_access(input_args):
    if 'api_key' in input_args:
        provided_key = sanitize_input(input_args['api_key'])
        if provided_key == LOADED_API_KEY:
            return (True, None)
        else:
            logging.warning('Request with wrong API-Key received')
            return (False, { 'error': 'Wrong API-Key provided' })
    else:
        logging.warning('Request without API-Key received')
        return (False, { 'error': 'No API-Key provided' })

# function to reveive arguments from request
def parse_request(input_args, required_arguments):
    valid, error = check_access(input_args)
    if not valid:
        return (valid, error)

    arguments = {}
    for argument in required_arguments:
        if argument in input_args:
            arguments[argument] = sanitize_input(input_args[argument])
        else:
            logging.info('API-Request without mandory field ' + argument)
            return (False, { 'error': 'Mandatory field ' + argument + ' not provided' })
    
    return (True, arguments)

# function that generates a return dict for a completed subprocess 
def parse_results(completed_process):
    if completed_process is not None and completed_process.returncode == 0:
        return { 'status': 'Success', 'stdout': completed_process.stdout }
    elif completed_process is not None and 'stderr' in completed_process:
        logging.error("Running of subprocess failed with output: " + run_result.stderr)
        return { 'status': 'Error', 'stdout': completed_process.stdout, 'stdout': completed_process.stderr }
    else:
        logging.error("Running of subprocess failed without output")
        return { 'status': 'Error', 'stdout': 'Could not run command!' }

# setup logging on startup
def setup_logging():
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s:%(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)

# function that cleans input from possible injections
def sanitize_input(input):
    return re.findall("\w+", str(input))[0]

##################################################
# Flask routes
##################################################
# status page
@app.route('/', methods=['GET'])
def hello():
    return 'Running <a href="https://github.com/' + str(os.getenv('GITHUB_REPOSITORY')) + '">REST-Light</a> Version ' + str(os.getenv('APP_VERSION'))

# api to switch sockets
@app.route('/send', methods=['POST'])
def send():
    logging.info(request.form.to_dict(flat=False))
    valid, results = parse_request(request.form, ['system_code', 'unit_code', 'state'])
    if not valid:
        return results

    run_result = None
    try:
        run_result = subprocess.run(["/opt/433Utils/RPi_utils/send", 
                                results['system_code'],
                                results['unit_code'],
                                results['state'] ], capture_output=True)
    except:
        logging.error("Error in Subprocess Call")
    return parse_results(run_result)


##################################################
# Main call
##################################################
if __name__ == '__main__':
    # init
    setup_logging()
    LOADED_API_KEY = load_key()
    # serve
    app.run(debug=True, host='0.0.0.0', port=4242)
