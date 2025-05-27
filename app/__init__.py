from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}/{os.getenv('MYSQL_DB')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "defaultsecretkey")

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    # Import models
    from app.models import User, Train

    # User loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register routes
    from app.routes import register_routes
    register_routes(app)

    # Add default trains if none exist
    with app.app_context():
        if not Train.query.first():
            trains = [
                Train(train_name="Express 101", from_station="Delhi", to_station="Mumbai", total_seats=100, available_seats=100, date=datetime(2025, 6, 1)),
                Train(train_name="Southern 222", from_station="Chennai", to_station="Bangalore", total_seats=80, available_seats=80, date=datetime(2025, 6, 2)),
            ]
            db.session.add_all(trains)
            db.session.commit()

    return app
