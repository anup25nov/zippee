from flask import Flask
from extensions import db
from flask_jwt_extended import JWTManager
from flask_restx import Api
from datetime import timedelta

# Initialize extensions
api = Api(title='Task Manager API', version='1.0', description='A simple Task Manager API')
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'super-secret-key'  # Change this in production
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

    db.init_app(app)
    jwt.init_app(app)
    api.init_app(app)

    from auth import auth_ns
    from resources.tasks import tasks_ns
    api.add_namespace(auth_ns)
    api.add_namespace(tasks_ns)

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True) 