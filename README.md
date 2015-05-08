pushover
========

[![Code Climate](https://codeclimate.com/github/rickmer/pushover/badges/gpa.svg)](https://codeclimate.com/github/rickmer/pushover) 

a pushover module (yet another) and command line tool

### module usage
```
from pushover import PushOverMessage
msg = PushOverMessage('api_key', 'user_key', 'nachricht')
msg.send()
```


### commandline usage

```
pushover.py --help
usage: pushover.py [-h] [--configFile CONFIGFILE] [--apiToken APITOKEN]
                   [--userToken USERTOKEN] [--title TITLE] [--url URL]
                   [--url_title URL_TITLE] [--device DEVICE]
                   [--priority PRIORITY] [--timestamp TIMESTAMP]
                   [--sound SOUND] [--proxy PROXY] [--proxy_auth PROXY_AUTH]
                   [-v]
                   msg

Send a Pushover message

positional arguments:
  msg

optional arguments:
  -h, --help            show this help message and exit
  --configFile CONFIGFILE
  --apiToken APITOKEN
  --userToken USERTOKEN
  --title TITLE
  --url URL
  --url_title URL_TITLE
  --device DEVICE
  --priority PRIORITY
  --timestamp TIMESTAMP
  --sound SOUND
  --proxy PROXY         http(s)://proxyserver:port
  --proxy_auth PROXY_AUTH
                        user:pass
  -v, --verbose
```


