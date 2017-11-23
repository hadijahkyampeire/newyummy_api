import os

class Config(object):
    """Parent configuration class."""
    APP_SETTINGS="development"
    DEBUG = False
    CSRF_ENABLED = True
    SECRET = "some-very-long-string-of-random-characters-CHANGE-TO-YOUR-LIKING"
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:0000@localhost/flask_api'
    FLASK_APP="run.py"

class DevelopmentConfig(Config):
    """Configurations for Development."""
    DEBUG = True


class TestingConfig(Config):
    """Configurations for Testing, with a separate test database."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI =  'postgresql://postgres:15december@localhost/test_db'
    DEBUG = True

class StagingConfig(Config):
    """Configurations for Staging."""
    DEBUG = True

class ProductionConfig(Config):
    """Configurations for Production."""
    DEBUG = False
    TESTING = False

app_config = {
    'config_name': DevelopmentConfig,
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'staging': StagingConfig,
    'production': ProductionConfig,
}
