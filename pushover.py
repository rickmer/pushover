#!/usr/bin/python
"""
Pushover API module and command line tool
"""
from urllib2 import Request, HTTPError, URLError, build_opener, ProxyBasicAuthHandler, ProxyHandler, install_opener
from urllib import urlencode
from json import loads
from argparse import ArgumentParser
from ConfigParser import ConfigParser, Error as ConfigParserError
import re

class PushOverMessage(object):
    """
    a PushOverMessage
    """
    def __init__(self, api_token, user_token, msg):
        self.api_token = api_token
        self.user_token = user_token
        self.msg = msg

    def send(self, optional_values=None, verbose=False, proxy_settings=None):
        """
        Method to submit the message. Optinal Parameters can be added.
        """
        if (optional_values is None):
            optional_values = {}

        obligate_values = {'token' : self.api_token,
                           'user' : self.user_token,
                           'message' : self.msg }

        values = dict(obligate_values.items() + optional_values.items())

        url = 'https://api.pushover.net/1/messages.json'

        postdata = urlencode(values)

        req = Request(url, postdata)

        if (    proxy_settings is not None
            and 'host' in proxy_settings
            and 'port' in proxy_settings):
            proxy_handler = ProxyHandler( { 'https' : ':'.join([proxy_settings['host'], proxy_settings['port']])} )

            if (    'user' in proxy_settings
                and 'pass' in proxy_settings):
                proxy_auth_handler = ProxyBasicAuthHandler()
                proxy_auth_handler.add_password('',
                                                ':'.join([proxy_settings['host'], proxy_settings['port']]),
                                                proxy_settings['user'],
                                                proxy_settings['pass'])
                opener = build_opener(proxy_handler, proxy_auth_handler)
            else:
                opener = build_opener(proxy_handler)
        else:
            opener = build_opener()

        install_opener(opener)

        try:
            response = opener.open(req)
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

def _valid_url_(candidate):
    """
    url validator function
    """
    regex = re.compile(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
    if (regex.match(candidate) is not None):
        return True
    else:
        return False

def _valid_auth_(candidate):
    """
    proxy auth settings validator function
    """
    regex = re.compile(r"^[a-z]{1,128}?:[a-z]{1,128}$")
    if (regex.match(candidate) is not None):
        return True
    else:
        return False

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
    command_line_argument_parser.add_argument('--proxy', type=str, help='http(s)://proxyserver:port')
    command_line_argument_parser.add_argument('--proxy_auth', type=str, help='user:pass')
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

    try:
        if (    commend_line_arguments.proxy is not None
            and _valid_url_(commend_line_arguments.proxy)):
            proxy_enabled = True
            proxy_protocol = commend_line_arguments.proxy.split(':')[0]
            proxy_host = commend_line_arguments.proxy.split('//')[1].split(':')[0]
            proxy_port = commend_line_arguments.proxy.split('//')[1].split(':')[1]
            proxy_settings = {'host' : ''.join([proxy_protocol, '://', proxy_host]),
                              'port' : proxy_port}
            if (    commend_line_arguments.proxy_auth is not None
                and _valid_auth_(commend_line_arguments.proxy_auth)):
                proxy_settings['user'] = commend_line_arguments.proxy_auth.split(':')[0]
                proxy_settings['pass'] = commend_line_arguments.proxy_auth.split(':')[1]
        elif (config_file.get('proxy','host') != ''):
            proxy_enabled = True
            proxy_host = config_file.get('proxy', 'host')
            proxy_port = config_file.get('proxy', 'port')
            proxy_settings = {'host' : proxy_host,
                              'port' : proxy_port}
            if (config_file.get('proxy','user') != ''):
                proxy_settings['user'] = config_file.get('proxy', 'user')
                proxy_settings['pass'] = config_file.get('proxy', 'pass')
        else:
            exit('Error: proxy configuration string malformed.')
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
    if (proxy_enabled):
        pushover_message.send(values, commend_line_arguments.verbose, proxy_settings)
    else:
        pushover_message.send(values, commend_line_arguments.verbose)

if __name__ == "__main__":
    main()
