from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token
from extensions import db
from models import User

auth_ns = Namespace('auth', description='Authentication operations')

user_model = auth_ns.model('User', {
    'username': fields.String(required=True),
    'password': fields.String(required=True),
})

@auth_ns.route('/register')
class Register(Resource):
    @auth_ns.expect(user_model, validate=False)
    def post(self):
        try:
            data = request.json
            if not data or 'username' not in data or 'password' not in data:
                return {'message': 'Username and password are required'}, 400
            if User.query.filter_by(username=data['username']).first():
                return {'message': 'User already exists'}, 400
            user = User(username=data['username'])
            user.set_password(data['password'])
            db.session.add(user)
            db.session.commit()
            return {'message': 'User registered successfully'}, 201
        except Exception as e:
            return {'message': 'Internal server error', 'error': str(e)}, 500

@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(user_model, validate=False)
    def post(self):
        try:
            data = request.json
            if not data or 'username' not in data or 'password' not in data:
                return {'message': 'Username and password are required'}, 400
            user = User.query.filter_by(username=data['username']).first()
            if user and user.check_password(data['password']):
                access_token = create_access_token(identity={'id': user.id, 'role': user.role})
                return {'access_token': access_token}, 200
            return {'message': 'Invalid credentials'}, 401
        except Exception as e:
            return {'message': 'Internal server error', 'error': str(e)}, 500 