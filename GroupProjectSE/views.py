"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template
from flask import request  # Make sure this import is at the top
from GroupProjectSE import app
import os
from GroupProjectSE.ml.predict import predict_disease


@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'MainPage.html',
        title='Project Info',
        year=datetime.now().year,
    )

@app.route('/info')
def info():
    """Renders the flask page."""
    return render_template(
        'index.html',
        title='Flask Info',
        year=datetime.now().year,
    )

@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Name and Emails'
    )

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='CNN Algorithm for Plant Disease Detection'
    )

app.config["UPLOAD_FOLDER"] = os.path.join("GroupProjectSE", "static", "uploads")


@app.route('/plant_analysis', methods=['GET', 'POST'])
def analyze():
    result = None
    file_url = None

    if request.method == 'POST':
        file = request.files['file']

        if file.filename != "":
            filename = file.filename
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)

            file_url = "/static/uploads/" + filename

            # run fake ML prediction
            result = predict_disease(save_path)

    return render_template(
        'plant_analysis.html',
        title='Plant Analysis',
        year=datetime.now().year,
        result=result,
        file_url=file_url
    )

@app.route('/generate_report', methods=['POST'])
def generate_report():
    file_path = request.form.get('file_path')
    result = request.form.get('result')

    return render_template(
        'report.html',
        title='Plant Analysis Report',
        year=datetime.now().year,
        file_path=file_path,
        result=result
    )
