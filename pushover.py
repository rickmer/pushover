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
        self.url = 'https://api.pushover.net/1/messages.json'

    def _get_url_opener_(self, proxy_settings):
        """
        build url opener with correct proxy and auth settings
        """
        if (proxy_settings is not None and 'host' in proxy_settings and 'port' in proxy_settings):
            proxy_handler = ProxyHandler({'https': ':'.join([proxy_settings['host'], proxy_settings['port']])})

            if ('user' in proxy_settings and 'pass' in proxy_settings):
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
        return opener

    def _get_postdata_(self, optional_values):
        """
        build url encoded postdata string
        """
        if (optional_values is None):
            optional_values = {}

        obligate_values = {'token': self.api_token,
                           'user': self.user_token,
                           'message': self.msg}

        values = dict(obligate_values.items() + optional_values.items())

        return urlencode(values)

    def send(self, optional_values=None, verbose=False, proxy_settings=None):
        """
        Method to submit the message. Optinal Parameters can be added.
        """
        req = Request(self.url, self._get_postdata_(optional_values))
        opener = self._get_url_opener_(proxy_settings)
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


def _validate_regexp_(candidate, pattern):
    """
    validator function to match string against regexp pattern
    """
    regex = re.compile(pattern)
    if (regex.match(candidate) is not None):
        return True
    else:
        return False


def _valid_url_(candidate):
    """
    url validator function
    """
    return _validate_regexp_(candidate, r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")


def _valid_auth_(candidate):
    """
    proxy auth settings validator function
    """
    return _validate_regexp_(candidate, r"^[\w]{1,128}?:[\w]{1,128}$")


def _parse_cli_():
    """
    parse commandline arguments
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
    return command_line_argument_parser.parse_args()


def _parse_cfg_file_(cfg_file):
    """
    parse config file
    """
    config_file = ConfigParser()
    try:
        config_file.readfp(open(cfg_file))
    except IOError:
        exit('Error: Specified config file was not found or not readable.')
    return config_file


def _get_config_token_(token_type, cli_cmd, cfg_file):
    """
    retrieve configuration token from cli or configfile
    """
    try:
        if (token_type in vars(cli_cmd)):
            token = cli_cmd.apiToken
        elif (cfg_file.get('pushover_api', token_type) != ''):
            token = cfg_file.get('pushover_api', token_type)
        else:
            exit('Error: No API Token provided.')
    except ConfigParserError:
        exit('Error: ConfigFile is malformed')
    return token


def _get_api_token_(cli_cmd, cfg_file):
    """
    retrieve api token from cli or configfile
    """
    return _get_config_token_('apitoken', cli_cmd, cfg_file)


def _get_user_token_(cli_cmd, cfg_file):
    """
    retrieve user token from cli or configfile
    """
    return _get_config_token_('usertoken', cli_cmd, cfg_file)


def _get_proxy_settings_(cli_cmd, cfg_file):
    try:
        if (cli_cmd.proxy is not None and _valid_url_(cli_cmd.proxy)):
            proxy_protocol = cli_cmd.proxy.split(':')[0]
            proxy_host = cli_cmd.proxy.split('//')[1].split(':')[0]
            proxy_port = cli_cmd.proxy.split('//')[1].split(':')[1]
            proxy_settings = {'host': ''.join([proxy_protocol, '://', proxy_host]),
                              'port': proxy_port}
            if (cli_cmd.proxy_auth is not None and _valid_auth_(cli_cmd.proxy_auth)):
                proxy_settings['user'] = cli_cmd.proxy_auth.split(':')[0]
                proxy_settings['pass'] = cli_cmd.proxy_auth.split(':')[1]
        elif (cfg_file.get('proxy', 'host') != ''):
            proxy_host = cfg_file.get('proxy', 'host')
            proxy_port = cfg_file.get('proxy', 'port')
            proxy_settings = {'host': proxy_host,
                              'port': proxy_port}
            if (cfg_file.get('proxy', 'user') != ''):
                proxy_settings['user'] = cfg_file.get('proxy', 'user')
                proxy_settings['pass'] = cfg_file.get('proxy', 'pass')
        else:
            proxy_settings = {}
    except ConfigParserError:
        exit('Error: ConfigFile is malformed')
    return proxy_settings


def _get_api_parameters_(cli_cmd, cfg_file):
    values = {}
    optinal_value_keys = ['title', 'url', 'url_title', 'priority', 'timestamp', 'sound']

    for key in optinal_value_keys:
        arg_value = vars(cli_cmd)[key]
        try:
            cfg_value = cfg_file.get('defaults', key)
        except ConfigParserError:
            cfg_value = ''
        if (arg_value is not None):
            values[key] = arg_value
        elif (cfg_value != ''):
            values[key] = cfg_value
    return values


def main():
    """
    CommandLine Interface
    """
    commend_line_arguments = _parse_cli_()
    config_file = _parse_cfg_file_(commend_line_arguments.configFile)
    api_token = _get_api_token_(commend_line_arguments, config_file)
    user_token = _get_user_token_(commend_line_arguments, config_file)
    proxy_settings = _get_proxy_settings_(commend_line_arguments, config_file)
    values = _get_api_parameters_(commend_line_arguments, config_file)

    pushover_message = PushOverMessage(api_token, user_token, commend_line_arguments.msg)
    if (proxy_settings):
        pushover_message.send(values, commend_line_arguments.verbose, proxy_settings)
    else:
        pushover_message.send(values, commend_line_arguments.verbose)

if __name__ == "__main__":
    main()
