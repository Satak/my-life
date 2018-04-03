"""My Life Application Core."""

from os import environ, path

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from conf import SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY
bcrypt = Bcrypt(app)

# set local env Set-Item -path env:DB_PATH -value 'sqlite:////Dev/satak/my-life/db/test.db'
database_path = path.join(path.dirname(__file__), 'db', 'database.db')
DP_PATH = 'sqlite:///{}'.format(database_path)

print(DP_PATH)


app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DB_PATH', DP_PATH)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
