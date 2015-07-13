# Here be dragons!
OCHproxy is currently in ?-stage and under active development. Please expect a few rough edges and bugs. 
It would be nice if you could test it and report any of these.

-----

[![Build Status](https://travis-ci.org/bauerj/OCHproxy.svg)](https://travis-ci.org/bauerj/OCHproxy)
[![Code Climate](https://codeclimate.com/github/bauerj/OCHproxy/badges/gpa.svg)](https://codeclimate.com/github/bauerj/OCHproxy)
[![Coverage Status](https://coveralls.io/repos/bauerj/OCHproxy/badge.svg?branch=master&service=github)](https://coveralls.io/github/bauerj/OCHproxy?branch=master)
[![Code Health](https://landscape.io/github/bauerj/OCHproxy/master/landscape.svg?style=flat)](https://landscape.io/github/bauerj/OCHproxy/master)
# OCHproxy
OCHproxy is an API that eases downloading from one-click hosters.
Using OCHproxy, you can share premium-accounts for one-click hosters with other people and get the following benefits:

+ No-one can steal your premium-account.
+ Your hoster won't ban you for using the account from multiple IPs.


## Name
OCH is short for One-Click-Hoster. 
You could argue that this actually not a proxy server but merely an HTTP-API. I guess it's kind of both.

## Installation
Currently, this is the best way to install OCHproxy:

1. Clone the Git repository.
2. Install python2 (and pip).
3. Use `pip install -r requirements.txt` to install dependencies.
4. Create a file named `users.txt` and add at least one line in the format `username:password`.
4. Run `ochproxy.py` a file named config.json will be generated. You will need to add at least one account there.
4. Restart ochproxy.
4. Open http://localhost:8081/


## FAQ
*While installing the dependencies on Linux, I get a message like this:*

    src/lxml/lxml.etree.c:16:20: fatal error: Python.h: Not found
    
You need to install the header files for Python, libXML2 and libXSLT so that pip can compile `pyquery`.

    apt-get install libxml2-dev libxslt1-dev python-dev
    

## Usage
Use `python2 ochproxy.py` to start the server. After the first run, a file named `config.json` is generated.
You need to add your usernames and passwords there if you want to use a hoster.

## Supported hosters
Look in the `hoster` directory for a list of supported hosters.

## Run the tests
To run the tests, you need to install py.test:

    pip install py.test
    
Then you can just run `py.test` and see if the tests are running as they are supposed to.