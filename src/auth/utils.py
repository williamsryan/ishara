from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

def hash_password(password: str) -> str:
    """Hash a plain-text password."""
    return bcrypt.generate_password_hash(password).decode('utf-8')

def check_password(password: str, hashed: str) -> bool:
    """Verify a plain-text password against a hashed password."""
    return bcrypt.check_password_hash(hashed, password)
