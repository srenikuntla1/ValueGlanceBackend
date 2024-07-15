# tests/test_app.py
import json
from app import db, User, BlogPost

def test_register(test_client):
    response = test_client.post('/register', json={
        'username': 'testuser',
        'password': 'password123'
    })
    assert response.status_code == 201
    assert b'User registered successfully' in response.data

def test_login(test_client):
    test_client.post('/register', json={
        'username': 'testuser',
        'password': 'password123'
    })
    response = test_client.post('/login', json={
        'username': 'testuser',
        'password': 'password123'
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'access_token' in data

def test_create_post(test_client):
    test_client.post('/register', json={
        'username': 'testuser',
        'password': 'password123'
    })
    login_response = test_client.post('/login', json={
        'username': 'testuser',
        'password': 'password123'
    })
    access_token = json.loads(login_response.data)['access_token']

    response = test_client.post('/posts', json={
        'title': 'Test Post',
        'content': 'This is a test post'
    }, headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 201
   

def test_get_posts(test_client):
    response = test_client.get('/posts')
    assert response.status_code == 200

def test_get_post_by_id(test_client):
    test_client.post('/register', json={
        'username': 'testuser',
        'password': 'password123'
    })
    login_response = test_client.post('/login', json={
        'username': 'testuser',
        'password': 'password123'
    })
    access_token = json.loads(login_response.data)['access_token']

    # Create a new post
    post_response = test_client.post('/posts', json={
        'title': 'Test Post',
        'content': 'This is a test post'
    }, headers={'Authorization': f'Bearer {access_token}'})

    post_id = json.loads(post_response.data)['id']

    # Retrieve the post by its id
    response = test_client.get(f'/posts/{post_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['id'] == post_id
    assert data['title'] == 'Test Post'
    assert data['content'] == 'This is a test post'

def test_update_post(test_client):
    test_client.post('/register', json={
        'username': 'testuser',
        'password': 'password123'
    })
    login_response = test_client.post('/login', json={
        'username': 'testuser',
        'password': 'password123'
    })
    access_token = json.loads(login_response.data)['access_token']

    post_response = test_client.post('/posts', json={
        'title': 'Test Post',
        'content': 'This is a test post'
    }, headers={'Authorization': f'Bearer {access_token}'})
    post_id = json.loads(post_response.data)['id']

    response = test_client.put(f'/posts/{post_id}', json={
        'title': 'Updated Test Post',
        'content': 'This is an updated test post'
    }, headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 200
    assert b'Post updated successfully' in response.data

def test_delete_post(test_client):
    test_client.post('/register', json={
        'username': 'testuser',
        'password': 'password123'
    })
    login_response = test_client.post('/login', json={
        'username': 'testuser',
        'password': 'password123'
    })
    access_token = json.loads(login_response.data)['access_token']

    post_response = test_client.post('/posts', json={
        'title': 'Test Post',
        'content': 'This is a test post'
    }, headers={'Authorization': f'Bearer {access_token}'})
    post_id = json.loads(post_response.data)['id']

    response = test_client.delete(f'/posts/{post_id}', headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 200
    assert b'Post deleted successfully' in response.data