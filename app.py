from flask import Flask, jsonify, send_from_directory, render_template, url_for
from flask_jwt_extended import JWTManager
# from flask_cors import CORS, cross_origin

from blacklist import BLACKLIST
from db import db


app = Flask(__name__)

# # CORS allow support
#
# cors = CORS(app, origins="http://localhost:4200", allow_headers=[
#     "Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
#     supports_credentials=True)
#
# app.config['CORS_HEADERS'] = 'Content-Type'
# app.config['CORS_ENABLED'] = True
#
# #


# additional configurations -
SECRET_KEY = "!*(-$^r3^"  # app secret key
JWT_SECRET_KEY = "!*(-$^r3^"  # jwt secret key

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"  # set ./data.db to be default database for sqlalchemy
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # flask_sqlalchemy library tracking set to false
app.secret_key = SECRET_KEY  # setting app secret

# setting up jwt
jwt = JWTManager(app)  # creating jwt manager


@app.route('/')
def root():
    return render_template('index.html')


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    # checks for an invalid token to prevent hacks by using old tokens
    return decrypted_token["jti"] in BLACKLIST


@app.before_first_request
def initialize_database():
    # must be done to create the databases before creating requests - this is not populating the database
    db.create_all()

