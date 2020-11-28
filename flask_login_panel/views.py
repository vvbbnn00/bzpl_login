"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import *
from flask_login_panel import app
from flask_login_panel.mods import mod_login_view


@app.route('/')
def index():
    return redirect('/login')


@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )


@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )
