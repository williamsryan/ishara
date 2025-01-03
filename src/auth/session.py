from flask_session import Session
from redis import Redis

def configure_sessions(app):
    """Configure Redis for session storage."""
    app.config["SESSION_TYPE"] = "redis"
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_USE_SIGNER"] = True
    app.config["SESSION_KEY_PREFIX"] = "session:"
    app.config["SESSION_REDIS"] = Redis(host="localhost", port=6379, decode_responses=True)

    Session(app)
    