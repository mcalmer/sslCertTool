
import argparse
from certTool.certToolConfig import CA_KEY_NAME, CA_CRT_NAME, CA_EXPIRE_DAYS, CRT_EXPIRE_DAYS, \
        HOSTNAME, BUILD_DIR, MD, CRYPTO, BITS

#MACHINENAME

#CA_CRT_RPM_NAME

#BASE_SERVER_RPM_NAME
#BASE_SERVER_TAR_NAME

#CA_OPENSSL_CNF_NAME
#SERVER_OPENSSL_CNF_NAME

#MD
#CRYPTO


def _create_parser():
    # create the top-level parser
    parser = argparse.ArgumentParser(
        prog='cert-tool',
        description="Generate SSL Certificates")

    # Generic options
    parser.add_argument(
        '--version',
        action='version',
        version='1.0.0',
        help='Print cert-tool version')

    subparsers = parser.add_subparsers(title='Subcommands')

    _create_genca_subparser(subparsers)
    _create_genserver_subparser(subparsers)

    return parser

def _create_genca_subparser(subparsers):
    """ Create the parser for the "genca" command. """

    genca_parser = subparsers.add_parser('genca',
                                         help='generate a new CA Certificate')
    genca_parser.set_defaults(which='genca')
    genca_parser.add_argument(
        '--ca-key', action='store', default=CA_KEY_NAME,
        help='CA private key filename (default: %s)' % CA_KEY_NAME)
    genca_parser.add_argument(
        '--ca-cert', action='store', default=CA_CRT_NAME,
        help='CA certificate filename (default: %s)' % CA_CRT_NAME)
    genca_parser.add_argument(
        '-p', '--password', action='store', help='CA password')
    genca_parser.add_argument(
        '--cert-expiration', action='store', type=int, default=CA_EXPIRE_DAYS,
        help='expiration of certificate (default: %s days)' % CA_EXPIRE_DAYS)

    _append_distinguishing(genca_parser, servercert=False)
    _append_common_options(genca_parser)



def _create_genserver_subparser(subparsers):
    """ Create the parser for the "genserver" command. """

    genserver_parser = subparsers.add_parser('genserver',
                                             help='generate a new CA Certificate')
    genserver_parser.set_defaults(which='genserver')
    genserver_parser.add_argument(
        '--server-key', action='store', default='server.key',
        help='Server private key filename (default: server.key)')
    genserver_parser.add_argument(
        '--server-cert', action='store', default='server.crt',
        help='Server certificate filename (default: server.crt)')
    genserver_parser.add_argument(
        '--server-cert-req', action='store', default='server.csr',
        help='Server certificate request filename (default: server.csr)')
    genserver_parser.add_argument(
        '--ca-key', action='store', default=CA_KEY_NAME,
        help='CA private key filename (default: %s)' % CA_KEY_NAME)
    genserver_parser.add_argument(
        '--ca-cert', action='store', default=CA_CRT_NAME,
        help='CA certificate filename (default: %s)' % CA_CRT_NAME)
    genserver_parser.add_argument(
        '-p', '--password', action='store', help='CA password')
    genserver_parser.add_argument(
        '--cert-expiration', action='store', type=int, default=CRT_EXPIRE_DAYS,
        help='expiration of certificate (default: %s days)' % CRT_EXPIRE_DAYS)

    _append_distinguishing(genserver_parser, servercert=True)
    _append_common_options(genserver_parser)


def _append_common_options(parser):
    parser.add_argument(
        '--md', action='store', default=MD,
        help="message digest algorithm (default: %s)" % MD)
    parser.add_argument(
        '--crypt', action='store', default=CRYPTO,
        help="crypto algorithm (default: %s)" % CRYPTO)
    parser.add_argument(
        '--bits', action='store', type=int, default=BITS,
        help="number of bits in the generated key (default: %s)" % BITS)

    parser.add_argument(
        '-d', '--dir', action='store', default=BUILD_DIR,
        help="build directory (default: %s)" % BUILD_DIR)
    parser.add_argument(
        '-v', '--verbose', action='store_true', default=False,
        help="Be verbose"),


def _append_distinguishing(parser, servercert=False):

    if servercert:
        parser.add_argument(
            '--set-hostname', action='store', default=HOSTNAME,
            help='Hostname of the server. (Default: %s)' % HOSTNAME)
        parser.add_argument(
            '--add-cname', action='append',
            help='cname of the server. Can be used multiple times.')
    else:
        parser.add_argument(
            '--set-common-name', action='store', help='Common Name')
    parser.add_argument(
        '--set-country', action='store', help='2 letter country code (e.g. US or DE)')
    parser.add_argument(
        '--set-state', action='store', help='state or province')
    parser.add_argument(
        '--set-city', action='store', help='city or locality')
    parser.add_argument(
        '--set-org', action='store', help='organization or company name')
    parser.add_argument(
        '--set-org-unit', action='store', help='organizational unit')
    parser.add_argument(
        '--set-email', action='store', help='email address')


def get_options(args=None):

    return _create_parser().parse_args(args)


