from flask_bootstrap import Bootstrap4
from flask_login import LoginManager
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy


bootstrap = Bootstrap4()
db = SQLAlchemy()
login_manager = LoginManager()
moment = Moment()


@login_manager.user_loader
def load_user(user_id):
    from app.models import Admin
    user = Admin.query.get(int(user_id))
    return user


login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'warning'
