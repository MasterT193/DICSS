from extensions import db
from flask_login import login_user as flask_login_user
from models import User
import bcrypt

def register_user(username, password):
    if User.query.filter_by(username=username).first():
        raise ValueError("Username already exists")
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    new_user = User(username=username, password=hashed_password.decode('utf-8'))  # Store as string
    db.session.add(new_user)
    db.session.commit()

def authenticate_user(username, password):
    user = User.query.filter_by(username=username).first()
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):  # Re-encode to bytes
        return user
    return None