#!/usr/bin/env python
#
#

from distutils.core import setup

setup(name = "sslCertTool",
      version = "1.0.0",
      description = "Tool to create SSL Certificates",
      long_description = """\
This Tool help to create SSL Certificates
""",
      author = 'Michael Calmer',
      author_email = 'Michael.Calmer@suse.com',
      url = 'https://github.com/mcalmer/sslCertTool',
      packages = ["certTool"],
      scripts=['cert-tool'],
      package_data={'certTool': ['*.sh']},
      license = "GPLv2",
      )

