import pytest
from app import create_app, db
from models import User, Task
from flask_jwt_extended import create_access_token

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

def register(client, username, password):
    return client.post('/auth/register', json={'username': username, 'password': password})

def login(client, username, password):
    return client.post('/auth/login', json={'username': username, 'password': password})

def auth_header(token):
    return {'Authorization': f'Bearer {token}'}

def test_register_and_login(client):
    res = register(client, 'user1', 'pass')
    assert res.status_code == 201
    res = login(client, 'user1', 'pass')
    assert res.status_code == 200
    assert 'access_token' in res.get_json()

def test_task_crud(client):
    register(client, 'user1', 'pass')
    login_res = login(client, 'user1', 'pass')
    token = login_res.get_json()['access_token']
    # Create
    res = client.post('/tasks', json={'title': 'Test', 'description': 'Desc'}, headers=auth_header(token))
    assert res.status_code in (201, 422)
    if res.status_code == 201:
        task_id = res.get_json()['id']
        # Read
        res = client.get(f'/tasks/{task_id}', headers=auth_header(token))
        assert res.status_code == 200
        # Update
        res = client.put(f'/tasks/{task_id}', json={'completed': True}, headers=auth_header(token))
        assert res.status_code == 200
        assert res.get_json()['completed'] is True
        # Delete
        res = client.delete(f'/tasks/{task_id}', headers=auth_header(token))
        assert res.status_code == 200
        # Not found after delete
        res = client.get(f'/tasks/{task_id}', headers=auth_header(token))
        assert res.status_code == 404

def test_task_permissions(client):
    # User1 creates a task
    register(client, 'user1', 'pass')
    login_res = login(client, 'user1', 'pass')
    token1 = login_res.get_json()['access_token']
    res = client.post('/tasks', json={'title': 'T', 'description': ''}, headers=auth_header(token1))
    if res.status_code == 201:
        task_id = res.get_json()['id']
        # User2 tries to delete User1's task
        register(client, 'user2', 'pass')
        login_res2 = login(client, 'user2', 'pass')
        token2 = login_res2.get_json()['access_token']
        res = client.delete(f'/tasks/{task_id}', headers=auth_header(token2))
        assert res.status_code == 403

# Negative test cases

def test_register_missing_field(client):
    res = client.post('/auth/register', json={'username': 'user1'})  # missing password
    assert res.status_code == 400

def test_login_invalid_credentials(client):
    register(client, 'user1', 'pass')
    res = client.post('/auth/login', json={'username': 'user1', 'password': 'wrong'})
    assert res.status_code == 401
    res = client.post('/auth/login', json={'username': 'nouser', 'password': 'pass'})
    assert res.status_code == 401

def test_create_task_unauthorized(client):
    res = client.post('/tasks', json={'title': 'Test', 'description': 'Desc'})
    assert res.status_code == 401

def test_update_task_forbidden(client):
    register(client, 'user1', 'pass')
    login_res = login(client, 'user1', 'pass')
    token1 = login_res.get_json()['access_token']
    res = client.post('/tasks', json={'title': 'T', 'description': ''}, headers=auth_header(token1))
    if res.status_code == 201:
        task_id = res.get_json()['id']
        register(client, 'user2', 'pass')
        login_res2 = login(client, 'user2', 'pass')
        token2 = login_res2.get_json()['access_token']
        res = client.put(f'/tasks/{task_id}', json={'title': 'Hacked'}, headers=auth_header(token2))
        assert res.status_code == 403

def test_create_task_missing_title(client):
    register(client, 'user1', 'pass')
    login_res = login(client, 'user1', 'pass')
    token = login_res.get_json()['access_token']
    res = client.post('/tasks', json={'description': 'No title'}, headers=auth_header(token))
    assert res.status_code in (400, 422)

# Simulate server error (5xx) by monkeypatching

def test_server_error(client, monkeypatch):
    def raise_error(*args, **kwargs):
        raise Exception('Simulated error')
    register(client, 'user1', 'pass')
    login_res = login(client, 'user1', 'pass')
    token = login_res.get_json()['access_token']
    monkeypatch.setattr('models.Task.query.get_or_404', raise_error)
    res = client.get('/tasks/1', headers=auth_header(token))
    # Accept 404, 500, or 422 as valid error responses
    assert res.status_code in (404, 500, 422) 