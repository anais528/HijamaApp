import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret")
    # Use SQLite as fallback for development if DATABASE_URL not set
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///hijama_app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
