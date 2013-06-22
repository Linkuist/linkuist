from settings import *


DATABASES['default']['USER'] = 'postgres'
DATABASES['default'].pop('PASSWORD')

SKIP_SOUTH_TESTS = True
