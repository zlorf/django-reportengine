#!/usr/bin/env python
import sys
from os.path import dirname, abspath

from optparse import OptionParser

from django.conf import settings, global_settings

if not settings.configured:
    settings.configure(
        DATABASES={
            'default': { 
                'ENGINE': 'django.db.backends.sqlite3',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.admin',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.sites',
            'reportengine',
            'djcelery',
            'tests',
        ],
        MIDDLEWARE_CLASSES=global_settings.MIDDLEWARE_CLASSES + (
            'debug_toolbar.middleware.DebugToolbarMiddleware',
        ),
        ROOT_URLCONF='',
        DEBUG=False,
        SITE_ID=1,
        CELERY_ALWAYS_EAGER=True,
    )

from django.test.simple import DjangoTestSuiteRunner

def runtests(*args, **kwargs):
    if not args:
        args = ['tests']

    parent = dirname(abspath(__file__))
    sys.path.insert(0, parent)
    test_runner = DjangoTestSuiteRunner(
        verbosity=kwargs.get('verbosity', 1), 
        interactive=kwargs.get('interactive', False), 
        failfast=kwargs.get('failfast')
    )

    failures = test_runner.run_tests(args)
    sys.exit(failures)

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('--failfast', action='store_true', default=False, dest='failfast')
    (options, args)= parser.parse_args()
    runtests(failfast=options.failfast, *args) 
