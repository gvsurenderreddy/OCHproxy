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
2. Install python2.
3. Use `python2 setup.py` to install dependencies.

## Usage
Use `python2 ochload.py` to start the server. After the first run, a file named `config.json` is generated.
You need to add your usernames and passwords there if you want to use a hoster.

## Supported hosters
Look in the `hoster` directory for a list of supported hosters.