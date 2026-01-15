import os
os.environ['DB_NAME'] = 'test_todos.db'
from starlette.testclient import TestClient
from main import app, todos
import pytest

def test_get_home():
    client = TestClient(app)
    res = client.get('/')
    assert res.status_code == 200
    assert 'Tasks' in res.text
    assert 'Minimalist Todo App' in res.text

def test_add_todo():
    client = TestClient(app)
    # Clear todos
    for t in todos(): todos.delete(t.id)
    
    res = client.post('/', data={'title': 'New Test Todo', 'done': 0})
    assert res.status_code == 200
    assert 'New Test Todo' in res.text
    assert len(todos()) == 1

def test_toggle_todo():
    client = TestClient(app)
    for t in todos(): todos.delete(t.id)
    todo = todos.insert(title='Toggle Me', done=False)
    
    res = client.post(f'/toggle/{todo.id}')
    assert res.status_code == 200
    # The updated todo is returned, should have 'todo-done' class
    assert 'todo-done' in res.text
    assert todos[todo.id].done == True
    
    res = client.post(f'/toggle/{todo.id}')
    assert res.status_code == 200
    assert 'todo-done' not in res.text
    assert todos[todo.id].done == False

def test_delete_todo():
    client = TestClient(app)
    for t in todos(): todos.delete(t.id)
    todo = todos.insert(title='Delete Me', done=False)
    
    res = client.delete(f'/delete/{todo.id}')
    assert res.status_code == 200
    # Delete usually returns empty or success indicator in HTMX
    assert len(todos()) == 0
