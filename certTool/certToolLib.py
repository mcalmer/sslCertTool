import os
import glob
import rpm
import string
import shutil
import subprocess
import os.path

def chdir(newdir):
    "chdir with the previous cwd as the return value"
    cwd = os.getcwd()
    os.chdir(newdir)
    return cwd

def normalizeAbsPath(path):
    if path is None:
        return None
    return os.path.abspath(normalizePath(path))

def normalizePath(path):
    return os.path.normpath(
            os.path.expanduser(
                os.path.expandvars(path)))

def getMachineName(hostname):
    """ xxx.yyy.zzz.com --> xxx.yyy
        yyy.zzz.com     --> yyy
        zzz.com         --> zzz.com
        xxx             --> xxx
        *.yyy.zzz.com   --> _star_.yyy
    """
    hostnamerep = hostname.replace('*', '_star_')
    hn = string.split(hostnamerep, '.')
    if len(hn) < 3:
        return hostnamerep
    return string.join(hn[:-2], '.')

def gendir(directory):
    "makedirs, but only if it doesn't exist first"
    if not os.path.exists(directory):
        try:
            os.makedirs(directory, 0700)
        except OSError, e:
            print "Error: %s" % (e, )
            sys.exit(1)

def rotateFile(path, maxrotate=5):
    if not path:
        raise CertToolException("Invalid Argument for path")
    if not os.path.exists(path):
        # nothing to do
        return None
    pathSuffix = normalizePath(path) + '.'
    pathSuffix1 = '%s%d' % (pathSuffix, 1)

    # find last in series (of rotations):
    last = 0
    while os.path.exists('%s%d' % (pathSuffix, last + 1)):
        last = last + 1

    # rotate backups
    for idx in range(last, 0, -1):
        if idx >= maxrotate:
            os.unlink('%s%d' % (pathSuffix, idx))
        else:
            os.rename('%s%d' % (pathSuffix, idx), '%s%d' % (pathSuffix, idx + 1))

    # rotate the initial file
    shutil.copy2(path, pathSuffix1)
    return pathSuffix1

def fileExists(filename):
    if not os.path.exists(filename):
        raise CertToolException("File '%s' does not exist." % filename)

def initIndexAndSerial(ca_dir, ca_crt):
    fileExists(ca_dir)
    fileExists(ca_crt)
    index_file = os.path.join(ca_dir, 'index.txt')
    if not os.path.exists(index_file):
        with open(index_file, 'w') as f:
            f.write("")
    serial_file = os.path.join(ca_dir, 'serial')
    if os.path.exists(serial_file):
        return

    cmd = [ '/usr/bin/openssl', 'x509',
            '-noout', '-serial',
            '-in', ca_crt]
    env = {}
    p = subprocess.Popen(cmd,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         env=env)
    stdout_value, stderr_value = p.communicate()
    if p.returncode > 0:
        raise CertToolException(repr(stdout_value) + repr(stderr_value))
    ca_serial = string.split(string.strip(stdout_value), '=')
    if len(ca_serial) != 2:
        raise CertToolException("Unable to read CA serial")
    ca_serial = ca_serial[1]
    next_serial = eval(hex(eval('0x'+ca_serial))) + 1
    with open(serial_file, 'w') as s:
        s.write("%X" % next_serial)

def latestRpmEVR(directory, rpmname):
    epo, ver, rel = None, '1.0', '0'
    filenames = glob.glob(os.path.join(directory, "%s-*.noarch.rpm" % rpmname))
    if not filenames:
        return epo, ver, rel
    hdr = [epo, ver, rel]
    for rpm_file in filenames:
        cmd = [ 'rpm', '-qp', '--qf',
                '%{EPOCH}-|_%{VERSION}-|_%{RELEASE}',
                rpm_file ]
        p = subprocess.Popen(cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        stdout_value, stderr_value = p.communicate()
        if p.returncode > 0:
            raise CertToolException(repr(stdout_value) + repr(stderr_value))
        epo, ver, rel = string.split(stdout_value, '-|_')
        if epo and epo == '(none)':
            epo = None
        h = [epo, ver, rel]
        comp = rpm.labelCompare(h, hdr)
        if comp > 0:
            hdr = h
    return hdr


class CertToolException(Exception):
    """ general exception class for the tool """

