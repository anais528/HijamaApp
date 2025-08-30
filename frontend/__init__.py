from flask import Flask 
from flask_cors import CORS


def create_app():
    
    app = Flask(__name__, static_folder='.', template_folder='.')
    CORS(app)  # Enable CORS for all routes
    app.config['SECRET_KEY'] = "123" 
    
    #routings 
    from .view import views 
    app.register_blueprint(views, url_prefix="/")
       
    return app