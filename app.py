import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Set up database base class
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy with the base class
db = SQLAlchemy(model_class=Base)

# Create the Flask application
app = Flask(__name__)

# Configure secret key
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key-for-dev")

# Configure the SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///education_management.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the database with the app
db.init_app(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Import models and routes within app context to avoid circular imports
with app.app_context():
    from models import User, Order, ClassRecord, PaymentRecord, SalaryRecord
    import routes
    
    # Create database tables if they don't exist
    db.create_all()
    
    # Create default admin user if it doesn't exist
    from werkzeug.security import generate_password_hash
    admin = User.query.filter_by(username="admin").first()
    if not admin:
        admin = User(username="admin", password_hash=generate_password_hash("admin"))
        db.session.add(admin)
        db.session.commit()
        logging.info("Default admin user created")

# Configure login manager user loader
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))
