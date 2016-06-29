import sys
import os
import socket
import string

from certTool.certToolLib import normalizePath, getMachineName, rotateFile

BUILD_DIR = normalizePath("./cert-build")
HOSTNAME = socket.getfqdn()

CA_KEY_NAME = 'CA-PRIVATE-SSL-KEY'
CA_CRT_NAME = 'CA-TRUSTED-SSL-CERT'
CA_CRT_RPM_NAME = string.lower(CA_CRT_NAME)

BASE_SERVER_RPM_NAME = 'ssl-servercert-key-pair'

MD = 'sha256'
CRYPTO = 'aes256'
BITS   = 2048

CA_EXPIRE_DAYS = 3650
CRT_EXPIRE_DAYS = 365

CA_OPENSSL_CNF_NAME = 'ca-openssl.cnf'
SRV_OPENSSL_CNF_NAME = 'server-openssl.cnf'

CA_RPM_SUMMARY = 'Public SSL CA Certificate'
SRV_RPM_SUMMARY = 'Server SSL Key and Certificate'

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
new_certs_dir           = $dir/newcerts
database                = $dir/index.txt
serial                  = $dir/serial
RANDFILE                = $dir/.rand
default_days            = 3650
default_md              = default
policy                  = policy_optional
copy_extensions         = copy
unique_subject          = no

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

[req]
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

def getCertToolPath():
    GENRPM = 'gen-rpm.sh'
    for path in sys.path:
        cert_tool_path = os.path.join(path, "certTool")
        if os.path.exists(os.path.join(cert_tool_path, GENRPM)):
            return cert_tool_path
    raise IOError("Cert Tool Path not found")

def genDistinguishedName(opts):
    distsect = ""
    if opts.country:
        distsect += "C                       = %s\n" % opts.country
    if opts.state:
        distsect += "ST                      = %s\n" % opts.state
    if opts.city:
        distsect += "L                       = %s\n" % opts.city
    if opts.org:
        distsect += "O                       = %s\n" % opts.org
    if opts.org_unit:
        distsect += "OU                      = %s\n" % opts.org_unit
    if 'common_name' in opts and opts.common_name:
        distsect += "CN                      = %s\n" % opts.common_name
    elif 'hostname' in opts and opts.hostname:
        distsect += "CN                      = %s\n" % opts.hostname
    if opts.email:
        distsect += "emailAddress            = %s\n" % opts.email
    return distsect

def genAltNames(opts):
    altnames = ""
    dnsnames = [opts.hostname]
    if opts.cnames and len(opts.cnames) > 0:
        dnsnames.extend(opts.cnames)
    idx = 0
    for name in dnsnames:
        idx = idx + 1
        altnames += "DNS.%d = %s\n" % (idx, name)
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

