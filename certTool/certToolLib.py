
import string
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

