
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
        return 0

    def _check_ca_opts(self):
        self.opts.dir = normalizePath(self.opts.dir)
        return 0

    def _check_server_opts(self):
        self.opts.dir = normalizePath(self.opts.dir)
        return 0
   
