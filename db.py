from flask_sqlalchemy import SQLAlchemy

# setting sqlalchemy outside the app to make it easier to import it anywhere
db = SQLAlchemy()