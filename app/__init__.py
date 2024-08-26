from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
#CORS(app)
#CORS(app, supports_credentials=True)

app.secret_key = 'your_secret_key'  

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

from .modules import models
from .routes import routes_categories, routes_users, routes_products
from .utils import utils


