"""
Flask application for blockchain voting frontend.
"""
from flask import Flask
from flask_login import LoginManager
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24).hex()

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


from frontend import routes
