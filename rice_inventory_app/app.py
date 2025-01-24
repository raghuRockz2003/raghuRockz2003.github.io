# app.py
import os
print(os.getcwd())  # This will print the current working directory

from flask import Flask
from rice_inventory_app.db import db, init_db

# Importing blueprint from the routes file
from rice_inventory_app.routes import routes_blueprint  # Importing routes_blueprint from the rice_inventory_app package

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rice_bags.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'Root@234'

# Initialize the database
init_db(app)

# Register blueprints
app.register_blueprint(routes_blueprint)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    app.run(debug=True)
