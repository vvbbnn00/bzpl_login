"""
The flask application package.
"""
import os

from flask_caching import Cache
from flask_login_panel.mods import mod_settings
mod_settings._init()


from flask import Flask
app = Flask(__name__)
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
cache = Cache(config={'CACHE_TYPE': 'simple'})
cache.init_app(app)
app.secret_key = os.urandom(24)
# app.debug = True

import flask_login_panel.views


