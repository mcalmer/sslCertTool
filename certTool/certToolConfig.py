import os
import socket
import string

from certTool.certToolLib import normalizePath, getMachineName, rotateFile

BUILD_DIR = normalizePath("./cert-build")
HOSTNAME = socket.getfqdn()
MACHINENAME = getMachineName(HOSTNAME)

CA_KEY_NAME = 'CA-PRIVATE-SSL-KEY'
CA_CRT_NAME = 'CA-TRUSTED-SSL-CERT'
CA_CRT_RPM_NAME = string.lower(CA_CRT_NAME)

BASE_SERVER_RPM_NAME = 'ssl-servercert-key-pair'
BASE_SERVER_TAR_NAME = 'ssl-servercert-archive'

CA_OPENSSL_CNF_NAME = 'ca-openssl.cnf'
SERVER_OPENSSL_CNF_NAME = 'server-openssl.cnf'

MD = 'sha256'
CRYPTO = 'aes256'
BITS   = 2048

CA_EXPIRE_DAYS = 3650
CRT_EXPIRE_DAYS = 365

CA_OPENSSL_CNF_NAME = 'ca-openssl.cnf'
SRV_OPENSSL_CNF_NAME = 'server-openssl.cnf'

OPENSSL_CA_CONF_TEMPLATE = """\
###############################################
# sslCertTool Template for CA Management
#
# !!! Never rename the sections !!!
#
###############################################
[ca]
default_ca              = CA_default

[ CA_default ]
default_bits            = 2048
x509_extensions         = v3_ca
dir                     = {1}
database                = $dir/index.txt
serial                  = $dir/serial
RANDFILE                = $dir/.rand
default_days            = 3650
default_md              = default
policy                  = policy_optional

[policy_optional]
countryName             = optional
stateOrProvinceName     = optional
localityName            = optional
organizationName        = optional
organizationalUnitName  = optional
commonName              = optional
emailAddress            = optional

###############################################

[req]
default_bits            = 2048
distinguished_name      = req_distinguished_name
x509_extensions         = v3_ca
string_mask             = utf8only
prompt                  = no

[v3_ca]
basicConstraints=critical, CA:true
nsComment="sslCertTool Generated CA Certificate"
nsCertType=sslCA, emailCA
keyUsage=cRLSign, keyCertSign
subjectKeyIdentifier=hash
authorityKeyIdentifier=keyid:always,issuer
subjectAltName=email:copy

[v3_server_sign]
basicConstraints=CA:false
nsComment="sslCertTool Generated Server Certificate"
nsCertType=server
keyUsage=digitalSignature, keyEncipherment, keyAgreement
extendedKeyUsage = serverAuth, clientAuth
subjectKeyIdentifier=hash
authorityKeyIdentifier=keyid,issuer:always

###############################################
[ req_distinguished_name ]
{0}
"""

OPENSSL_SERVER_CONF_TEMPLATE = """\
###############################################

[req_server]
default_bits            = 2048
distinguished_name      = req_distinguished_name
x509_extensions         = v3_server_sign
string_mask             = utf8only
prompt                  = no
req_extensions          = v3_req

[v3_server_sign]
basicConstraints=CA:false
nsComment="sslCertTool Generated Server Certificate"
nsCertType=server
keyUsage=digitalSignature, keyEncipherment, keyAgreement
extendedKeyUsage = serverAuth, clientAuth
subjectKeyIdentifier=hash
authorityKeyIdentifier=keyid,issuer:always

[ v3_req ]
# Extensions to add to a certificate request
basicConstraints = CA:false
keyUsage = nonRepudiation, digitalSignature, keyEncipherment

subjectAltName          = @alt_names

[alt_names]
{1}

###############################################
[ req_distinguished_name ]
{0}

"""

def genDistinguishedName(opts):
    distsect = ""
    if opts.set_country:
        distsect += "C                       = %s\n" % opts.set_country
    if opts.set_state:
        distsect += "ST                      = %s\n" % opts.set_state
    if opts.set_city:
        distsect += "L                       = %s\n" % opts.set_city
    if opts.set_org:
        distsect += "O                       = %s\n" % opts.set_org
    if opts.set_org_unit:
        distsect += "OU                      = %s\n" % opts.set_org_unit
    if opts.set_common_name:
        distsect += "CN                      = %s\n" % opts.set_common_name
    if opts.set_email:
        distsect += "emailAddress            = %s\n" % opts.set_email
    return distsect

def genAltNames(opts):
    altnames = ""
    dnsnames = [opts.set_hostname]
    if opts.add_cname and len(opts.add_cname) > 0:
        dnsnames.extend(opts.add_cname)
    idx = 0
    for name in dnsnames:
        idx = idx + 1
        altnames += "DNS.%d = %s\n" %(i, name)
    return altnames

class OpenSSLConf(object):
    def __init__(self, filename, template='CA'):
        self.filename = normalizePath(filename)
        if template.upper() == 'CA':
            self.cnf_template = OPENSSL_CA_CONF_TEMPLATE
            self.is_ca = True
        else:
            self.cnf_template = OPENSSL_SERVER_CONF_TEMPLATE
            self.is_ca = False

    def save(self, opts):
        rotateFile(path=self.filename)
        with open(self.filename, 'w') as f:
            if self.is_ca:
                f.write(self.cnf_template.format(genDistinguishedName(opts), opts.dir))
            else:
                f.write(self.cnf_template.format(genDistinguishedName(opts), genAltNames(opts)))
        os.chmod(self.filename, 0600)

