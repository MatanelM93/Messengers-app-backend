from app import app
from routes import Routes

from db import db
from ma import ma

# initializing app routes
routes = Routes()
routes.routes()

# running the application
if __name__ == "__main__":
    db.init_app(app)
    ma.init_app(app)
    app.run(port=5000, debug=True)