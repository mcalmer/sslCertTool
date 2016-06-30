sslCertTool: A Tool for generating SSL Certificates
===================================================

usage: cert-tool [-h] [--version] {genca,genserver} ...

Generate SSL Certificates

optional arguments:
  -h, --help         show this help message and exit
  --version          Print cert-tool version

Subcommands:
  {genca,genserver}
    genca            generate a new CA Certificate
    genserver        generate a new Server Certificate


usage: cert-tool genca [-h] [--cert-expiration CERT_EXPIRATION]
                       [--common-name COMMON_NAME] [--country COUNTRY]
                       [--state STATE] [--city CITY] [--org ORG]
                       [--org-unit ORG_UNIT] [--email EMAIL] [-p PASSWORD]
                       [--ca-key CA_KEY] [--ca-cert CA_CERT] [--md MD]
                       [--crypt CRYPT] [--bits BITS] [--rpm-only] [-d DIR]
                       [-v]

optional arguments:
  -h, --help            show this help message and exit
  --cert-expiration CERT_EXPIRATION
                        expiration of certificate (default: 3650 days)
  --common-name COMMON_NAME
                        Common Name
  --country COUNTRY     2 letter country code (e.g. US or DE)
  --state STATE         state or province
  --city CITY           city or locality
  --org ORG             organization or company name
  --org-unit ORG_UNIT   organizational unit
  --email EMAIL         email address
  -p PASSWORD, --password PASSWORD
                        CA password. Either the password itself or via
                        enviroment variable defined by "env:<VAR_NAME>". If
                        omitted, the tool will ask for it.
  --ca-key CA_KEY       CA private key filename (default: CA-PRIVATE-SSL-KEY)
  --ca-cert CA_CERT     CA certificate filename (default: CA-TRUSTED-SSL-CERT)
  --md MD               message digest algorithm (default: sha256)
  --crypt CRYPT         crypto algorithm (default: aes256)
  --bits BITS           number of bits in the generated key (default: 2048)
  --rpm-only            build only the rpm
  -d DIR, --dir DIR     build directory (default: cert-build)
  -v, --verbose         Be verbose

usage: cert-tool genserver [-h] [--server-key SERVER_KEY]
                           [--server-cert SERVER_CERT]
                           [--server-cert-req SERVER_CERT_REQ]
                           [--cert-expiration CERT_EXPIRATION]
                           [--server-rpm SERVER_RPM] [--hostname HOSTNAME]
                           [--cname CNAMES] [--country COUNTRY]
                           [--state STATE] [--city CITY] [--org ORG]
                           [--org-unit ORG_UNIT] [--email EMAIL] [-p PASSWORD]
                           [--ca-key CA_KEY] [--ca-cert CA_CERT] [--md MD]
                           [--crypt CRYPT] [--bits BITS] [--rpm-only] [-d DIR]
                           [-v]

optional arguments:
  -h, --help            show this help message and exit
  --server-key SERVER_KEY
                        Server private key filename (default: server.key)
  --server-cert SERVER_CERT
                        Server certificate filename (default: server.crt)
  --server-cert-req SERVER_CERT_REQ
                        Server certificate request filename (default:
                        server.csr)
  --cert-expiration CERT_EXPIRATION
                        expiration of certificate (default: 365 days)
  --server-rpm SERVER_RPM
                        RPM name that houses the server's SSL key and
                        certificate. (the base filename, not filename-version-
                        release.noarch.rpm)
  --hostname HOSTNAME   Hostname of the server. (Default: lesch.suse.de)
  --cname CNAMES        cname of the server. Can be used multiple times.
  --country COUNTRY     2 letter country code (e.g. US or DE)
  --state STATE         state or province
  --city CITY           city or locality
  --org ORG             organization or company name
  --org-unit ORG_UNIT   organizational unit
  --email EMAIL         email address
  -p PASSWORD, --password PASSWORD
                        CA password. Either the password itself or via
                        enviroment variable defined by "env:<VAR_NAME>". If
                        omitted, the tool will ask for it.
  --ca-key CA_KEY       CA private key filename (default: CA-PRIVATE-SSL-KEY)
  --ca-cert CA_CERT     CA certificate filename (default: CA-TRUSTED-SSL-CERT)
  --md MD               message digest algorithm (default: sha256)
  --crypt CRYPT         crypto algorithm (default: aes256)
  --bits BITS           number of bits in the generated key (default: 2048)
  --rpm-only            build only the rpm
  -d DIR, --dir DIR     build directory (default: cert-build)
  -v, --verbose         Be verbose

Examples:
---------

Generate a CA Certificte:
```
$> cert-tool genca -p secret --common-name "My CA" --org "My Company" --email "me@domain.top" --country "US"
```

Generate a Server Certificate:
```
$> cert-tool genserver -p secret --hostname "www.domain.top" --org "My Company" --email "me@domain.top" --country "US"
```

Generate a Server Certificate with multiple cnames and provide the password via environment.

```
$> MY_CA_PASSWD=secret cert-tool genserver -p "env:MY_CA_PASSWD" --hostname "www.domain.top" --org "My Company" \
   --email "me@domain.top" --country "US" --cname "host1.domain.top" --cname "host2.domain.top"
```

Copyright (c) 2016 SUSE LLC
---------------------------

This software is licensed to you under the GNU General Public License,
version 2 (GPLv2). There is NO WARRANTY for this software, express or
implied, including the implied warranties of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
along with this software; if not, see
http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.


Create the tar-ball
-------------------

```
$> git archive --format=tar.gz --prefix=sslCertTool/ HEAD -o sslCertTool.tar.gz
```

