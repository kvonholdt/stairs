from flask import Flask
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)

app.config['APP_NAME'] = 'ActiStairs'
app.config['DB_LOCATION'] = 'sqlite:///actistairs.db'


from app import views
