from collectr.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'collectr',                      # Or path to database file if using sqlite3.
        'USER': 'postgres'
    }
}

SECRET_KEY = 'j!v*yjq%gals10eqa(04kur*_yl#9!o!#b^^8vnxzky5q=#wb$'
