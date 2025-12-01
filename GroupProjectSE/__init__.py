"""
The flask application package.
"""

from flask import Flask
from flask_login import LoginManager
import os
from GroupProjectSE.auth import get_user_by_id

app = Flask(__name__)

# Secret key (required for sessions)
app.secret_key = "CHANGE_ME_TO_SOMETHING_SECURE"

# Upload folder
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'GroupProjectSE', 'static', 'uploads')

# Create upload folder if missing
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Login manager setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"   # Page to redirect if user not logged in

@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(int(user_id))

import GroupProjectSE.views
