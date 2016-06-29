import os
import subprocess
from certToolLib import CertToolException, normalizePath, gendir, getMachineName, \
        rotateFile, fileExists, initIndexAndSerial, latestRpmEVR, chdir, normalizeAbsPath
from certToolConfig import CA_OPENSSL_CNF_NAME, SRV_OPENSSL_CNF_NAME, OpenSSLConf, \
        getCertToolPath, CA_CRT_RPM_NAME

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
        initIndexAndSerial(self.opts.dir, ca_crt)
        gendir(os.path.join(self.opts.dir, 'newcerts'))

    def genCaRpm(self):
        gendir(self.opts.dir)
        ca_crt = os.path.join(self.opts.dir, self.opts.ca_cert)
        fileExists(ca_crt)

        ca_cert_rpm = os.path.join(self.opts.dir, CA_CRT_RPM_NAME)
        epo, ver, rel = latestRpmEVR(self.opts.dir, CA_CRT_RPM_NAME)
        if rel:
            rel = str(int(rel)+1)

        update_trust_script = os.path.join(getCertToolPath(), "rpmpost-update-ca-trust.sh")

        cmd = [ os.path.join(getCertToolPath(), 'gen-rpm.sh'),
                '--name', CA_CRT_RPM_NAME,
                '--version', ver,
                '--release', rel,
                '--group', 'Productivity/Security',
                '--summary', 'Public SSL CA Certificate',
                '--description', 'Public SSL CA Certificate',
                '--post', update_trust_script,
                '--postun', update_trust_script,
                '/etc/pki/certTool/%s=%s' % (self.opts.ca_cert, normalizeAbsPath(ca_crt))]
        cwd = chdir(self.opts.dir)
        p = subprocess.Popen(cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        stdout_value, stderr_value = p.communicate()
        chdir(cwd)
        if p.returncode > 0:
            raise CertToolException(stdout_value)

    def genServerPrivateKey(self):
        """ private Server key generation """
        serverDir = os.path.join(self.opts.dir, getMachineName(self.opts.set_hostname))
        gendir(serverDir)
        server_key = os.path.join(serverDir, self.opts.server_key)
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
        serverDir = os.path.join(self.opts.dir, getMachineName(self.opts.set_hostname))
        gendir(serverDir)
        server_key = os.path.join(serverDir, self.opts.server_key)
        server_req = os.path.join(serverDir, self.opts.server_cert_req)
        server_crt = os.path.join(serverDir, self.opts.server_cert)

        fileExists(server_key)
        sslconf = os.path.join(serverDir, SRV_OPENSSL_CNF_NAME)

        # gen the request
        cnf = OpenSSLConf(sslconf, template='server')
        cnf.save(self.opts)

        rotateFile(path=server_req)
        cmd = [ '/usr/bin/openssl', 'req',
                '-%s' % self.opts.md, '-text',
                '-config', cnf.filename,
                '-new', '-key', server_key,
                '-out', server_req]
        env = {}
        p = subprocess.Popen(cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             env=env)
        stdout_value, stderr_value = p.communicate()
        if p.returncode > 0:
            raise CertToolException(repr(stdout_value))
        # permissions:
        os.chmod(server_req, 0600)

        # gen the certificate
        if not self.opts.password:
            raise CertToolException("A CA password must be supplied.")

        ca_key = os.path.join(self.opts.dir, self.opts.ca_key)
        ca_crt = os.path.join(self.opts.dir, self.opts.ca_cert)
        ca_sslconf = os.path.join(self.opts.dir, CA_OPENSSL_CNF_NAME)
        fileExists(ca_sslconf)
        fileExists(ca_key)
        fileExists(ca_crt)

        rotateFile(path=server_crt)

        cmd = [ '/usr/bin/openssl', 'ca',
                '-extensions', 'v3_server_sign',
                '-passin', 'env:CERTTOOL_CA_PASSWD',
                '-config', ca_sslconf,
                '-in', server_req,
                '-batch', '-cert', ca_crt,
                '-keyfile', ca_key,
                # startdate?
                '-days', str(self.opts.cert_expiration),
                '-md', self.opts.md,
                '-out', server_crt]
        env = {'CERTTOOL_CA_PASSWD': self.opts.password}
        p = subprocess.Popen(cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             env=env)
        stdout_value, stderr_value = p.communicate()
        if p.returncode > 0:
            raise CertToolException(repr(stdout_value))

        # permissions:
        os.chmod(server_crt, 0644)


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
   
