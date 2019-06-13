# -*- coding:utf-8 -*-
import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # python -c 'import os; print(os.urandom(16))'
    SECRET_KEY = os.environ.get('SECRET_KEY') or b'\xd4Y\x0bJ\x9e\x9fx+\x9bh\xba\x9a=\xee,\x08'
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.126.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '25'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in \
        ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') 
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') 
    WEBLOG_MAIL_SUBJECT_PREFIX = '[WeBlog]'
    WEBLOG_MAIL_SENDER = 'WeBlog Admin <%s>' % MAIL_USERNAME
    WEBLOG_ADMIN = os.environ.get('WEBLOG_ADMIN') or MAIL_USERNAME
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WEBLOG_POSTS_PER_PAGE = 30
    WEBLOG_FOLLOWERS_PER_PAGE = 50
    WEBLOG_COMMENTS_PER_PAGE = 30
    WEBLOG_SLOW_DB_QUERY_TIME = 0.5 # second
    SQLALCHEMY_RECORD_QUERIES = True
    SSL_DISABLE = True

    @staticmethod
    def init_app(app):
        pass

    @classmethod
    def print_config(cls, app):
        app.logger.info('Use config: %s' % cls.__name__)
        for attr_name in dir(cls):
            if (attr_name[0:2] != '__'):
                attr = getattr(cls, attr_name)
                app.logger.info("%s = %s" % (attr_name, attr))


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # log errors to file
        import logging
        from logging.handlers import RotatingFileHandler
        import os
        
        basedir = os.path.abspath(os.path.dirname(__file__))
        logdir = os.path.join(basedir, 'tmp/log')
        if not os.path.isdir(logdir):
            os.mkdir(logdir)
        log_file_path = os.path.join(logdir, 'weblog.log')
        file_handler = RotatingFileHandler(log_file_path, maxBytes=1024*1024*10, backupCount=3, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'))
        app.logger.addHandler(file_handler)


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite://'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # email errors to the administrators
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure = ()
        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.WEBLOG_MAIL_SENDER,
            toaddrs=[cls.WEBLOG_ADMIN],
            subject=cls.WEBLOG_MAIL_SUBJECT_PREFIX + ' Application Error',
            credentials=credentials,
            secure=secure)
        mail_handler.setLevel(logging.ERROR)
        mail_handler.setFormatter(logging.Formatter('%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'))
        app.logger.addHandler(mail_handler)



class HerokuConfig(ProductionConfig):
    SSL_DISABLE = bool(os.environ.get('SSL_DISABLE'))
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)
        # log to stderr
        import logging
        from logging import StreamHandler
        app.logger.setLevel(logging.INFO)
        #file_handler = StreamHandler()
        #file_handler.setFormatter(logging.Formatter('%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'))
        #file_handler.setLevel(logging.INFO)
        #app.logger.addHandler(file_handler)

        # handle reverse proxy server headers
        from werkzeug.contrib.fixers import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'heroku': HerokuConfig,

    'default': DevelopmentConfig
}
