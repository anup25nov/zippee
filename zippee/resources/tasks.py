from flask import request
from flask_restx import Namespace, Resource, fields, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Task, User
from werkzeug.exceptions import NotFound

tasks_ns = Namespace('tasks', description='Task operations')

task_model = tasks_ns.model('Task', {
    'id': fields.Integer(readOnly=True),
    'title': fields.String(),
    'description': fields.String,
    'completed': fields.Boolean,
    'created_at': fields.DateTime,
    'updated_at': fields.DateTime,
    'user_id': fields.Integer,
})

parser = reqparse.RequestParser()
parser.add_argument('completed', type=bool, required=False, help='Filter by completion status')
parser.add_argument('page', type=int, required=False, default=1, help='Page number')
parser.add_argument('per_page', type=int, required=False, default=5, help='Tasks per page')

@tasks_ns.route('')
class TaskList(Resource):
    @tasks_ns.doc('list_tasks')
    @tasks_ns.expect(parser)
    @jwt_required()
    def get(self):
        try:
            args = parser.parse_args()
            query = Task.query
            if args['completed'] is not None:
                query = query.filter_by(completed=args['completed'])
            page = args['page']
            per_page = args['per_page']
            paginated = query.paginate(page=page, per_page=per_page, error_out=False)
            return {
                'tasks': [self.serialize(task) for task in paginated.items],
                'total': paginated.total,
                'pages': paginated.pages,
                'current_page': paginated.page
            }
        except Exception as e:
            return {'message': 'Internal server error', 'error': str(e)}, 500

    @jwt_required()
    def post(self):
        try:
            data = request.json
            if not data or 'title' not in data:
                return {'message': 'Title is required'}, 400
            user_id = get_jwt_identity()['id']
            task = Task(title=data['title'], description=data.get('description', ''), user_id=user_id)
            db.session.add(task)
            db.session.commit()
            return self.serialize(task), 201
        except Exception as e:
            return {'message': 'Internal server error', 'error': str(e)}, 500

    def serialize(self, task):
        return {
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'completed': task.completed,
            'created_at': task.created_at.isoformat(),
            'updated_at': task.updated_at.isoformat(),
            'user_id': task.user_id
        }

@tasks_ns.route('/<int:id>')
class TaskResource(Resource):
    @jwt_required()
    def get(self, id):
        try:
            task = Task.query.get_or_404(id)
            return TaskList.serialize(self, task)
        except NotFound:
            raise
        except Exception as e:
            return {'message': 'Internal server error', 'error': str(e)}, 500

    @jwt_required()
    def put(self, id):
        try:
            task = Task.query.get_or_404(id)
            user = User.query.get(get_jwt_identity()['id'])
            if task.user_id != user.id and user.role != 'admin':
                return {'message': 'Permission denied'}, 403
            data = request.json
            if not data:
                return {'message': 'No data provided'}, 400
            task.title = data.get('title', task.title)
            task.description = data.get('description', task.description)
            task.completed = data.get('completed', task.completed)
            db.session.commit()
            return TaskList.serialize(self, task)
        except NotFound:
            raise
        except Exception as e:
            return {'message': 'Internal server error', 'error': str(e)}, 500

    @jwt_required()
    def delete(self, id):
        try:
            task = Task.query.get_or_404(id)
            user = User.query.get(get_jwt_identity()['id'])
            if task.user_id != user.id and user.role != 'admin':
                return {'message': 'Permission denied'}, 403
            db.session.delete(task)
            db.session.commit()
            return {'message': 'Task deleted'}
        except NotFound:
            raise
        except Exception as e:
            return {'message': 'Internal server error', 'error': str(e)}, 500 