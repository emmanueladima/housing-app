from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os 
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail

mail = Mail()
csrf = CSRFProtect()

login_manager = LoginManager()
login_manager.login_view = 'main.login'

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = os.path.join('app', 'static', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'secret-key'  

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'your_email@gmail.com' #fill in later
    app.config['MAIL_PASSWORD'] = 'your_app_password'  
    app.config['MAIL_DEFAULT_SENDER'] = 'your_email@gmail.com'

    mail.init_app(app)
    db.init_app(app)
    csrf.init_app(app)

    from .routes import main
    app.register_blueprint(main)

    with app.app_context():
        from . import models
        db.create_all()

        from .models import User  # make sure this comes after db.init_app(app)

        @login_manager.user_loader 
        def load_user(user_id):
            return User.query.get(int(user_id))

        login_manager.init_app(app)
    
        @app.context_processor
        def inject_csrf_token():
            from flask_wtf.csrf import generate_csrf
            return dict(csrf_token=generate_csrf)


    return app
