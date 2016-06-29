import os
import subprocess
from certToolLib import CertToolException, normalizePath, gendir, getMachineName, \
        rotateFile, fileExists
from certToolConfig import CA_OPENSSL_CNF_NAME, SRV_OPENSSL_CNF_NAME, OpenSSLConf

class CertTool(object):
    def __init__(self, opts):
        self.genca = False
        self.genserver = False
        self.opts = opts
        print self.opts
        if opts.which == 'genca':
            self._check_ca_opts()
            self.genca = True
        elif opts.which == 'genserver':
            self._check_server_opts()
            self.genserver = True
        else:
            raise CertToolException("invalid module")

    def run(self):
        if self.genca:
            self.genCaPrivateKey()
            self.genCaPublicCert()
            self.genCaRpm()
        elif self.genserver:
            self.genServerPrivateKey()
            self.genServerPublicCert()
            self.genServerRpm()
        return 0

    def genCaPrivateKey(self):
        """ private CA key generation """
        gendir(self.opts.dir)
        ca_key = os.path.join(self.opts.dir, self.opts.ca_key)
        if os.path.exists(ca_key):
            raise CertToolException("CA private key already exists")
        cmd = [ '/usr/bin/openssl', 'genrsa',
                '-passout', 'env:CERTTOOL_CA_PASSWD',
                '-%s' % self.opts.crypt,
                '-out', ca_key,
                str(self.opts.bits)]
        env = {'CERTTOOL_CA_PASSWD': self.opts.password}
        p = subprocess.Popen(cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             env=env)
        stdout_value, stderr_value = p.communicate()
        if p.returncode > 0:
            raise CertToolException(repr(stdout_value))
        # permissions:
        os.chmod(ca_key, 0600)

    def genCaPublicCert(self):
        """ public CA certificate generation """
        gendir(self.opts.dir)
        ca_key = os.path.join(self.opts.dir, self.opts.ca_key)
        ca_crt = os.path.join(self.opts.dir, self.opts.ca_cert)
        sslconf = os.path.join(self.opts.dir, CA_OPENSSL_CNF_NAME)

        if os.path.exists(ca_crt):
            raise CertToolException("CA public certificate already exists")
        fileExists(ca_key)

        if not self.opts.password:
            raise CertToolException("A CA password must be supplied.")
        cnf = OpenSSLConf(sslconf)
        cnf.save(self.opts)

        cmd = [ '/usr/bin/openssl', 'req',
                '-passin', 'env:CERTTOOL_CA_PASSWD',
                '-text', '-config', cnf.filename,
                '-new', '-x509',
                '-days', str(self.opts.cert_expiration),
                '-%s' % self.opts.md,
                '-key', ca_key,
                '-out', ca_crt]
        env = {'CERTTOOL_CA_PASSWD': self.opts.password}
        p = subprocess.Popen(cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             env=env)
        stdout_value, stderr_value = p.communicate()
        if p.returncode > 0:
            raise CertToolException(repr(stdout_value))

        # permissions:
        os.chmod(ca_crt, 0644)

    def genCaRpm(self):
        pass

    def genServerPrivateKey(self):
        """ private Server key generation """
        serverDir = os.path.join(self.opts.dir, getMachineName(self.opts.set_hostname))
        gendir(serverDir)
        server_key = os.path.join(serverDir, self.opts.ca_key)
        rotateFile(server_key)
        cmd = [ '/usr/bin/openssl', 'genrsa',
                '-out', server_key,
                str(self.opts.bits)]
        env = {}
        p = subprocess.Popen(cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             env=env)
        stdout_value, stderr_value = p.communicate()
        if p.returncode > 0:
            raise CertToolException(repr(stdout_value))
        # permissions:
        os.chmod(server_key, 0600)

    def genServerPublicCert(self):
        pass

    def genServerRpm(self):
        pass

    def _check_ca_opts(self):
        self.opts.dir = normalizePath(self.opts.dir)
        if not self.opts.password:
            raise CertToolException("Password must not be empty")
        if not self.opts.set_common_name:
            raise CertToolException("A CA must have a common name")
        return 0

    def _check_server_opts(self):
        self.opts.dir = normalizePath(self.opts.dir)
        if not self.opts.password:
            raise CertToolException("CA Password must be provided")
        if not self.opts.set_hostname:
            raise CertToolException("A Server Certificate must have a hostname")
        return 0
   
