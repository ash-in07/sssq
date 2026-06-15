from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

# Shared extension objects for the application.
db = SQLAlchemy()
jwt = JWTManager()
