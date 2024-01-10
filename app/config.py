from decouple import config

class Config:
    SECRET_KEY = config('SECRET_KEY', default='your_default_secret_key')
    SQLALCHEMY_DATABASE_URI = config('DATABASE_URL', default='sqlite:///your_database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
    UPLOAD_FOLDER = 'app/static/uploads'

    # Для настроек почты
    MAIL_USERNAME = config('MAIL_USERNAME', default='senior.nikita1@yandex.ru')
    MAIL_PASSWORD = config('MAIL_PASSWORD', default='yjwnaihjvzrrlhjm')
    MAIL_SERVER = 'smtp.yandex.ru'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False