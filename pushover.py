#!/usr/bin/python
"""
Pushover API module and command line tool
"""
from urllib2 import Request, urlopen, HTTPError, URLError
from urllib import urlencode
from json import loads
from argparse import ArgumentParser
from ConfigParser import ConfigParser, Error as ConfigParserError

class PushOverMessage(object):
    """
    a PushOverMessage
    """
    def __init__(self, api_token, user_token, msg):
        self.api_token = api_token
        self.user_token = user_token
        self.msg = msg

    def send(self, optional_values={}, verbose=False):
        """
        Method to submit the message. Optinal Parameters can be added.
        """
        obligate_values = {'token' : self.api_token,
                           'user' : self.user_token,
                           'message' : self.msg }
        values = dict(obligate_values.items() + optional_values.items())
        url = 'https://api.pushover.net/1/messages.json'
        postdata = urlencode(values)
        req = Request(url, postdata)

        try:
            response = urlopen(req)
            json_string = response.read()
            json_obj = loads(json_string)
            if (verbose):
                if (json_obj.get('status') == 1):
                    print 'message was submitted under the id %s' % json_obj.get('request')
        except HTTPError, error:
            if (verbose):
                print 'API Error (%s)' % str(error.code)
            return None
        except URLError, e:
            for error in e:
                if (e.args[0][0] == 8):
                    if (verbose):
                        print 'Error: Pushover API not reachable'
            return None

        if (json_obj.get('status') == 1):
            return json_obj.get('request')
        else:
            return None

def main():
    """
    CommandLine Interface
    """
    command_line_argument_parser = ArgumentParser(description='Send a Pushover message')
    command_line_argument_parser.add_argument('--configFile', type=str, default='pushover.cfg')
    command_line_argument_parser.add_argument('--apiToken', type=str)
    command_line_argument_parser.add_argument('--userToken', type=str)
    command_line_argument_parser.add_argument('--title', type=str)
    command_line_argument_parser.add_argument('--url', type=str)
    command_line_argument_parser.add_argument('--url_title', type=str)
    command_line_argument_parser.add_argument('--device', type=str)
    command_line_argument_parser.add_argument('--priority', type=str)
    command_line_argument_parser.add_argument('--timestamp', type=str)
    command_line_argument_parser.add_argument('--sound', type=str)
    command_line_argument_parser.add_argument('msg', type=str)
    command_line_argument_parser.add_argument('-v', '--verbose', action='store_true')
    commend_line_arguments = command_line_argument_parser.parse_args()
    config_file = ConfigParser()

    try:
        config_file.readfp(open(commend_line_arguments.configFile))
    except IOError:
        exit('Error: Specified config file was not found or not readable.')

    try:
        if (commend_line_arguments.apiToken is not None):
            api_token = commend_line_arguments.apiToken
        elif (config_file.get('pushover_api','apitoken') != ''):
            api_token = config_file.get('pushover_api','apitoken')
        else:
            exit('Error: No API Token provided.')

        if (commend_line_arguments.userToken is not None):
            user_token = commend_line_arguments.userToken
        elif (config_file.get('pushover_api','usertoken') != ''):
            user_token = config_file.get('pushover_api','usertoken')
        else:
            exit('Error No User Token provided.')
    except ConfigParserError:
        exit('Error: ConfigFile is malformed')

    values = {}

    optinal_value_keys = ['title',
                           'url',
                           'url_title',
                           'priority',
                           'timestamp',
                           'sound']

    for key in optinal_value_keys:
        arg_value = vars(commend_line_arguments)[key]
        try:
            cfg_value = config_file.get('defaults', key)
        except ConfigParserError:
            cfg_value = ''
        if (arg_value is not None):
            values[key] = arg_value
        elif (cfg_value != ''):
            values[key] = cfg_value

    pushover_message = PushOverMessage(api_token, user_token, commend_line_arguments.msg)
    pushover_message.send(values, commend_line_arguments.verbose)

if __name__ == "__main__":
    main()
