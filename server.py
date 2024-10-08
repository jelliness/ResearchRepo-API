from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate #install this module in your terminal
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from werkzeug.security import generate_password_hash, check_password_hash
from models import db
from config import Config
from flask_mail import Mail
from dash_app import create_dash_app

#Initialize the app
app = Flask(__name__)
CORS(app)

#database Configuration
app.config.from_object(Config)


# Initialize the database
db.init_app(app)
mail = Mail(app)
migrate = Migrate(app, db)


# function that checks db if existing or not
def check_db(db_name, user, password, host='localhost', port='5432'):
    try:
        connection = psycopg2.connect(user=user, password=password, host=host, port=port, dbname='postgres')
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()

        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        exists = cursor.fetchone()

        if not exists:
            cursor.execute(f'CREATE DATABASE "{db_name}"')
            print(f"Database '{db_name}' created successfully.")
        else:
            print(f"Database '{db_name}' already exists.")
    except Exception as error:
        print(f"Error while creating database: {error}")
    finally:
        if connection:
            cursor.close()
            connection.close()

#
check_db('Research_Data_Integration_System', 'postgres', 'Papasa01!')

with app.app_context():
    db.create_all()
    print("Tables created successfully.")


from routes.auth import auth
from routes.accounts import accounts
from routes.dept_prog import deptprogs
from routes.dataset import dataset


# Register the blueprint for routes
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(accounts, url_prefix='/accounts')
app.register_blueprint(deptprogs, url_prefix='/deptprogs')
app.register_blueprint(dataset, url_prefix='/dataset')


# Create and register Dash app
dash_app = create_dash_app(app)  # Pass the Flask app to the Dash app


if __name__ == "__main__":
    app.run(debug=True)
