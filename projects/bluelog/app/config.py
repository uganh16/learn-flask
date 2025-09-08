import os
import sys


base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# SQLite URI compatible
if sys.platform.startswith('win'):
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'


SECRET_KEY = os.getenv('SECRET_KEY', 'secret string')

SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = os.getenv(
    'DATABASE_URI', prefix + os.path.join(base_dir, 'db.sqlite3'))

BLUELOG_EMAIL = os.getenv('BLUELOG_EMAIL')
BLUELOG_POST_PER_PAGE = 10
BLUELOG_COMMENT_PER_PAGE = 15
