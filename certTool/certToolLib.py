import os
import string
import shutil
import os.path

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

class CertToolException(Exception):
    """ general exception class for the tool """

