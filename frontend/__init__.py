from flask import Flask 
#from flask_cors import CORS
from .config import Config
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    #CORS(app)  # Enable CORS for all routes
    
    app.config.from_object(Config)
    db.init_app(app)
    
    #routings 
    from .view import views 
    app.register_blueprint(views, url_prefix="/")
       
    return app