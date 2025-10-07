"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template
from GroupProjectSE import app

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
