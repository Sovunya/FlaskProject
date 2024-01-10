from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from .api_routes import api
# from flask_admin import Admin
# from flask_admin.contrib.sqla import ModelView
from app.config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
app.register_blueprint(api, url_prefix='/api')

# Инициализация Flask-Admin
# admin = Admin(app, name='Admin Panel', template_mode='bootstrap3')

from app.models import User, Tour  # Уберите импорт db и login_manager из этой строки

# admin.add_view(ModelView(User, db.session))
# admin.add_view(ModelView(Tour, db.session))

from app import routes