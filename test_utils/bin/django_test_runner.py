#!/usr/bin/env python
"""
Many thanks to Brian Rosner <oebfare.com> for letting me include
this code in Test Utils.
"""

import os
import sys

from optparse import OptionParser

from django.conf import settings
from django.core.management import call_command

def main():
    """
The entry point for the script. This script is fairly basic. Here is a
quick example of how to use it::

    django_test_runner.py [path-to-app]

You must have Django on the PYTHONPATH prior to running this script. This
script basically will bootstrap a Django environment for you.

By default this script with use SQLite and an in-memory database. If you
are using Python 2.5 it will just work out of the box for you.
"""
    parser = OptionParser()
    parser.add_option("--DATABASE_ENGINE", dest="DATABASE_ENGINE", default="sqlite3")
    parser.add_option("--DATABASE_NAME", dest="DATABASE_NAME", default="")
    parser.add_option("--DATABASE_USER", dest="DATABASE_USER", default="")
    parser.add_option("--DATABASE_PASSWORD", dest="DATABASE_PASSWORD", default="")
    parser.add_option("--SITE_ID", dest="SITE_ID", type="int", default=1)

    options, args = parser.parse_args()

    # check for app in args
    try:
        app_path = args[0]
    except IndexError:
        print "You did not provide an app path."
        raise SystemExit
    else:
        if app_path.endswith("/"):
            app_path = app_path[:-1]
        parent_dir, app_name = os.path.split(app_path)
        sys.path.insert(0, parent_dir)

    settings.configure(**{
        "DATABASE_ENGINE": options.DATABASE_ENGINE,
        "DATABASE_NAME": options.DATABASE_NAME,
        "DATABASE_USER": options.DATABASE_USER,
        "DATABASE_PASSWORD": options.DATABASE_PASSWORD,
        "SITE_ID": options.SITE_ID,
        "ROOT_URLCONF": "",
        "TEMPLATE_LOADERS": (
            "django.template.loaders.filesystem.load_template_source",
            "django.template.loaders.app_directories.load_template_source",
        ),
        "TEMPLATE_DIRS": (
            os.path.join(os.path.dirname(__file__), "templates"),
        ),
        "INSTALLED_APPS": (
            # HACK: the admin app should *not* be required. Need to spend some
            # time looking into this. Django #8523 has a patch for this issue,
            # but was wrongly attached to that ticket. It should have its own
            # ticket.
            "django.contrib.admin",
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django.contrib.sites",
            app_name,
        ),
    })
    call_command("test")

if __name__ == "__main__":
    main()
