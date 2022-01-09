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
# Stores the currently valid api-key
LOADED_API_KEY = None

# important paths for the application
paths = {
    "base": "/etc/rest-light",
    "433utils": "/opt/433Utils/RPi_utils",
    "api_key": "/etc/rest-light/api-key.txt"
}

##################################################
# utility functions
##################################################
# setup logging on startup
def setup_logging():
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s:%(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)

# loads key on app startup
def load_key():
    # exit if key already defined
    if LOADED_API_KEY is not None:
        return

    # try to open persistence file
    key_tmp = None
    try:
        with open(paths['api_key'], 'r') as f:
            lines = f.readlines()
            key_tmp = re.findall("\w+", lines[0])[0]
    except FileNotFoundError as e:
        logging.info('No API-Key found, generating new one')
    except BaseException as e:
        logging.fatal('Unkown exception when trying to load api-key! ' + str(e))

    # return key
    if key_tmp is not None:
        return key_tmp
    # generate new key
    else:
        new_key = ''.join(random.choices(
            string.ascii_lowercase + string.ascii_uppercase + string.digits, k=42))
        # persists key
        try:
            with open(paths['api_key'], 'w') as f:
                f.write(new_key)
        except BaseException as e:
            logging.fatal(
                'Could not save API-Key in the following folder. Ensure permissions are correct! ' + paths['base'])
            logging.fatal(str(e))
            sys.exit()

        # return key and log
        logging.warning('#'*60)
        logging.warning('Generated API-Key: ' + new_key)
        logging.warning('#'*60)
        return new_key

##################################################
# Functions to handle requests
##################################################
# function that cleans input from possible injections
def sanitize_input(input):
    output = None
    try: 
        output = re.findall("\w+", str(input))[0]
    except BaseException as e:
            logging.error('Received unparsable web-request')
            logging.error(str(e))
    return output

# function to check, if a provided api-key is valid
def check_access(input_args):
    if 'api_key' in input_args:
        provided_key = sanitize_input(input_args['api_key'])
        if provided_key == LOADED_API_KEY:
            return (True, None)
        else:
            logging.warning('Request with wrong API-Key received')
            return (False, {'error': 'Wrong API-Key provided'})
    else:
        logging.warning('Request without API-Key received')
        return (False, {'error': 'No API-Key provided'})

# function to reveive arguments from request
def parse_request(input_args, required_arguments):
    logging.debug(input_args.to_dict(flat=False))
    valid, error = check_access(input_args)
    if not valid:
        return (valid, error)

    arguments = {}
    for argument in required_arguments:
        if argument in input_args:
            arguments[argument] = sanitize_input(input_args[argument])
        else:
            logging.info('API-Request without mandory field ' + argument)
            return (False, {'error': 'Mandatory field ' + argument + ' not provided'})

    return (True, arguments)

# function that runs a OS-Subprocess and generates a return-dict 
def run_command(arguments):
    # Run Command and capture output
    run_result = None
    try:
        run_result = subprocess.run(arguments, capture_output=True)
    except subprocess.SubprocessError as e:
        logging.fatal(
            "Running of subprocess resulted in SubprocessError: " + str(e.output))
        return {'status': 'Error', 'stdout': "Running of subprocess resulted in SubprocessError: " + str(e.output)}
    except FileNotFoundError as e:
        logging.fatal(
            "Running of subprocess resulted in FileNotFoundError: " + str(e.strerror))
        return {'status': 'Error', 'stdout': "Running of subprocess resulted in FileNotFoundError: " + str(e.strerror)}

    # treat output
    if run_result is not None and run_result.returncode == 0:
        logging.debug("Successfully ran command: " + " ".join(arguments))
        return {'status': 'Success', 'stdout': run_result.stdout}
    elif run_result is not None and 'stderr' in run_result:
        logging.error(
            "Running of subprocess failed with output: " + run_result.stderr)
        return {'status': 'Error', 'stdout': run_result.stdout, 'stdout': run_result.stderr}
    else:
        logging.error("Running of subprocess failed without output")
        return {'status': 'Error', 'stdout': 'Could not run command!'}

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
    request_valid, parsed_request = parse_request(
        request.form, ['system_code', 'unit_code', 'state'])
    if not request_valid:
        return parsed_request

    return run_command([paths['433utils'] + "/send",
                        parsed_request['system_code'],
                        parsed_request['unit_code'],
                        parsed_request['state']])

# api to send raw codes
@app.route('/codesend', methods=['POST'])
def codesend():
    request_valid, parsed_request = parse_request(
        request.form, ['decimalcode'])
    if not request_valid:
        return parsed_request

    return run_command([paths['433utils'] + "/codesend",
                        parsed_request['decimalcode']])


##################################################
# Main call
##################################################
if __name__ == '__main__':
    # init
    setup_logging()
    LOADED_API_KEY = load_key()
    # serve
    app.run(debug=True, host='0.0.0.0', port=4242)
