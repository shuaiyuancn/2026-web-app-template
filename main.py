from fasthtml.common import *

# Define the Todo data structure and create the database table

import os
db_name = os.getenv('DB_NAME', 'todos.db')

def render(todo):
    tid = f'todo-{todo.id}'
    is_done = 'todo-done' if todo.done else ''
    due_display = Small(f"Due: {todo.due_date}", cls="todo-due") if getattr(todo, 'due_date', None) else ""
    toggle = CheckboxX(checked=todo.done, 
                       hx_post=f'/toggle/{todo.id}', 
                       target_id=tid, 
                       hx_swap='outerHTML')
    delete = A('Delete', 
               hx_delete=f'/delete/{todo.id}', 
               target_id=tid, 
               hx_swap='outerHTML',
               cls='delete-link')
    return Li(toggle, 
              Span(todo.title, cls='todo-content'), 
              due_display,
              delete, 
              id=tid, 
              cls=is_done)

app, rt, todos, Todo = fast_app(db_name, 
                                todos={'id': int, 'title': str, 'done': bool, 'due_date': str, 'pk': 'id', 'render': render}, 
                                hdrs=(Link(rel='stylesheet', href='index.css'),), 
                                pico=False)

@rt('/')
def get():
    frm = Form(Input(placeholder="What needs to be done?", name="title"), 
               Input(type="date", name="due_date"),
               Button("Add Task"),
               hx_post="/", target_id='todo-list', hx_swap="afterbegin")
    
    return Main(
        Div(
            H1("Tasks"),
            P("Minimalist Todo App"),
            cls="title-header"
        ),
        Div(
            frm,
            Ul(*todos(), id='todo-list'),
            cls="card"
        ),
        cls="container"
    )

@rt('/')
def post(todo: Todo):
    return todos.insert(todo)

@rt('/delete/{id}')
def delete(id: int):
    todos.delete(id)

@rt('/toggle/{id}')
def post(id: int):
    todo = todos[id]
    todo.done = not todo.done
    return todos.update(todo)


if __name__ == "__main__":
    serve()
