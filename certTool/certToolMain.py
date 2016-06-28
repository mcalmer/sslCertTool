import os
import subprocess
from certToolLib import CertToolException, normalizePath, gendir, getMachineName, \
        rotateFile

class CertTool(object):
    def __init__(self, opts):
        self.genca = False
        self.genserver = False
        self.opts = opts
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
        if self.genserver:
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
        pass

    def genCaRpm(self):
        pass

    def genServerPrivateKey(self):
        """ private Server key generation """
        print self.opts
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
        return 0

    def _check_server_opts(self):
        self.opts.dir = normalizePath(self.opts.dir)
        return 0
   
