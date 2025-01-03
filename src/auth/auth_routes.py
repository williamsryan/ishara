from flask import Blueprint, request, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from src.utils.database import fetch_as_dataframe

# Create Blueprint
auth = Blueprint("auth", __name__)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = "auth.login"  # Redirect to 'auth.login' if not logged in

# User loader
class User:
    def __init__(self, user_id, email):
        self.id = user_id
        self.email = email

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

@login_manager.user_loader
def load_user(user_id):
    """Fetch user from the database by ID."""
    query = f"SELECT id, email FROM users WHERE id = {user_id}"
    user = fetch_as_dataframe(query).to_dict("records")
    if user:
        return User(user[0]["id"], user[0]["email"])
    return None

# Login route
@auth.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    # Query user from the database
    query = f"SELECT id, email, password_hash FROM users WHERE email = '{email}'"
    user = fetch_as_dataframe(query).to_dict("records")

    if not user or not check_password_hash(user[0]["password_hash"], password):
        return jsonify({"error": "Invalid email or password"}), 401

    # Create a user object
    user_obj = User(user[0]["id"], user[0]["email"])
    login_user(user_obj)

    return jsonify({"message": "Login successful"}), 200

# Logout route
@auth.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out"}), 200

# Protected route example
@auth.route("/protected", methods=["GET"])
@login_required
def protected():
    return jsonify({"message": f"Welcome {current_user.email}!"}), 200
