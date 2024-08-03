from werkzeug.security import generate_password_hash, check_password_hash
from models import User, db

def register_user(username, password):
    password_hash = generate_password_hash(password)
    user = User(username=username, password_hash=password_hash)
    db.session.add(user)
    db.session.commit()

def verify_user(username, password):
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        return user
    return None
