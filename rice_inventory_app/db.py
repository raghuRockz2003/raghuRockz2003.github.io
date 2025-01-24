from flask_sqlalchemy import SQLAlchemy

# Create a single instance of SQLAlchemy
db = SQLAlchemy()

def init_db(app):
    db.init_app(app)
