#!/usr/bin/env python
import imp
import os
import site
import sys

from django.core.management import execute_manager

# Paths
VENDOR_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'vendor'))
site.addsitedir(VENDOR_PATH)


try:
    imp.find_module('settings') # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n" % __file__)
    sys.exit(1)

import settings


if __name__ == "__main__":
    execute_manager(settings)
