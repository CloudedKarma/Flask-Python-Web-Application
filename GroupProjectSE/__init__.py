"""
The flask application package.
"""

from flask import Flask
import os

app = Flask(__name__)

# Add upload folder
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')

# Create upload folder if missing
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

import GroupProjectSE.views
