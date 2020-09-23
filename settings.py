import os

basedir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@127.0.0.1:3306/jd'
    SECRET_KEY = '123456'
    BASEDIR = basedir
    RESULT_PATH = os.path.join(BASEDIR, 'static', 'analysis_picture')


config = BaseConfig
