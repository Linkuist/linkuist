from settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'collectr',                      # Or path to database file if using sqlite3.
        'USER': 'postgres'
    }
}


SKIP_SOUTH_TESTS = True
