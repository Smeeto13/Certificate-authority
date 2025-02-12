# Mini CA
A python based tool for generating and managing OpenSSL keys and certificates

Guide:  https://sophie.smeeton.icu/security/openssl-toolkit/ #Not active link

Requires python 3.10+, openssl, opensc (Smart card support), libp11 (Smart card support)

## TODO:
* Update PIV configs
* Add systemd service for periodicaly updating CRLs
* Add proper error handeling
* Allow picking Key type for CA
## Potential future features:
* Intermediate CA support
* Run with args from cmdline
