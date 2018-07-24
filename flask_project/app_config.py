import os

# import SECRET_KEY into current namespace
# noinspection PyUnresolvedReferences

try:
    THE_SECRET_KEY = os.environ['SECRET_KEY']
except KeyError:
    THE_SECRET_KEY = 'THE_SECRET_KEY'

try:
    OAUTH_CONSUMER_KEY = os.environ['OAUTH_CONSUMER_KEY']
except KeyError:
    OAUTH_CONSUMER_KEY = 'OAUTH_CONSUMER_KEY'

try:
    OAUTH_SECRET = os.environ['OAUTH_SECRET']
except KeyError:
    OAUTH_SECRET = 'OAUTH_SECRET'

try:
    SENTRY_DSN = os.environ['SENTRY_DSN']
except KeyError:
    SENTRY_DSN = 'SENTRY_DSN'


try:
    DATA_FOLDER = os.environ['DATA_FOLDER']
except KeyError:
    DATA_FOLDER = 'home/web/field-campaigner-data'


class Config(object):
    """Configuration environment for application.
    """
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = THE_SECRET_KEY
    OAUTH_CONSUMER_KEY = OAUTH_CONSUMER_KEY
    OAUTH_SECRET = OAUTH_SECRET
    SENTRY_DSN = SENTRY_DSN
    MAX_AREA_SIZE = 320000000
    DB_LOCATION = os.environ['DATABASE_URL']

    # OSMCHA ATTRIBUTES
    _OSMCHA_DOMAIN = 'https://osmcha.mapbox.com/'
    OSMCHA_API = _OSMCHA_DOMAIN + 'api/v1/'
    OSMCHA_FRONTEND_URL = 'https://osmcha.mapbox.com/'

    # CAMPAIGN DATA
    campaigner_data_folder = "./campaign_manager/static"


class ProductionConfig(Config):
    """Production environment.
    """
    DEBUG = False


class StagingConfig(Config):
    """Staging environment.
    """
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    """Development environment.
    """
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    """Testing environment.
    """
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = True
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    DB_LOCATION = os.environ['TESTDATABASE_URL']
    DRIVER_PATH = os.path.abspath('./campaign_manager/test/chromedriver')
