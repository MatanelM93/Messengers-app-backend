from app import app
from routes import Routes

from db import db
from ma import ma

# initializing app database
db.init_app(app)

# initializing app routes
routes = Routes()
routes.routes()

@app.before_first_request
def initialize_database():
    # must be done to create the databases before creating requests - this is not populating the database
    db.create_all()

# running the application
if __name__ == "__main__":
    ma.init_app(app)
    app.run(port=5000, debug=True)