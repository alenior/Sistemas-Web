import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sua_chave_secreta_segura'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f"mysql://root:password@localhost/contas_a_pagar"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True  # Defina como False em produção

class ProductionConfig(Config):
    DEBUG = False
    # Outras configurações específicas de produção

class DevelopmentConfig(Config):
    DEBUG = True
    # Outras configurações específicas de desenvolvimento

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    # Outras configurações específicas de testes
