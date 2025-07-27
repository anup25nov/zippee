# Task Manager API (Screenshot of the APIs attached)

A simple RESTful API for managing tasks with user authentication, built using Flask.

## Features

- User registration and login (JWT authentication)
- CRUD operations for tasks
- Pagination and filtering
- User roles (admin, user)
- Unit tests

## Setup

1. Clone the repository:
   ```bash
   git clone git@github.com:anup25nov/zippee.git
   cd zippee
   ```
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python app.py
   ```

### Endpoints

- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and get JWT token
- `GET /tasks` - List tasks (pagination/filtering)
- `POST /tasks` - Create a task (auth required)
- `GET /tasks/<id>` - Get task details (auth required)
- `PUT /tasks/<id>` - Update a task (auth required)
- `DELETE /tasks/<id>` - Delete a task (auth required)

### Example curl Requests

#### Register

```bash
curl -X POST http://localhost:5000/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"username": "user1", "password": "pass"}'
```

#### Login

```bash
curl -X POST http://localhost:5000/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username": "user1", "password": "pass"}'
```

#### Create Task

```bash
curl -X POST http://localhost:5000/tasks \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{"title": "Test Task", "description": "Details"}'
```

#### Get All Tasks (with pagination and filtering)

```bash
curl -X GET 'http://localhost:5000/tasks?page=1&per_page=5&completed=true' \
  -H 'Authorization: Bearer <token>'
```

#### Get Task by ID

```bash
curl -X GET http://localhost:5000/tasks/1 \
  -H 'Authorization: Bearer <token>'
```

#### Update Task

```bash
curl -X PUT http://localhost:5000/tasks/1 \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{"title": "Updated Task", "completed": true}'
```

#### Delete Task

```bash
curl -X DELETE http://localhost:5000/tasks/1 \
  -H 'Authorization: Bearer <token>'
```

## Testing

To run tests:

```bash
pytest
```

## Notes

- Default admin user can be created by manually setting the role in the database.
- Change the JWT secret key in production.
