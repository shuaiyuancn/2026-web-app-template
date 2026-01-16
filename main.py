from fasthtml.common import *
from fastsql import Database
import os
from datetime import datetime, timedelta

# Database connection configuration
def get_db_url():
    # Priority 1: DATABASE_URL (set in compose.yaml or Vercel)
    url = os.getenv("DATABASE_URL")
    if url: 
        return url.replace("postgres://", "postgresql://")
    
    # Priority 2: Supabase Non-Pooling (Best for SQLAlchemy/FastSQL)
    non_pooling_url = os.getenv("POSTGRES_URL_NON_POOLING")
    if non_pooling_url: 
        return non_pooling_url.replace("postgres://", "postgresql://")

    # Priority 3: Supabase / Postgres env vars
    pg_url = os.getenv("POSTGRES_URL")
    if pg_url: 
        return pg_url.replace("postgres://", "postgresql://")
    
    # Fallback/Default
    return "postgresql://postgres:postgres@localhost:5432/postgres"

db_url = get_db_url()
db = Database(db_url)

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

# Define todos table using FastSQL
# Note: FastSQL's create_table or similar might be needed if it doesn't exist
if 'todos' not in db.t:
    db.t.todos.create(id=int, title=str, done=bool, due_date=str, pk='id')
todos = db.t.todos
Todo = todos.dataclass()

app, rt = fast_app(hdrs=(Link(rel='stylesheet', href='index.css'),), 
                    pico=False)

@rt('/')
def get():
    default_date = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')
    # JS to set default date on focus if empty
    date_js = f"if(!this.value) this.value='{default_date}'"
    
    frm = Form(Input(type="text", placeholder="What needs to be done?", name="title"), 
               Input(type="date", name="due_date", onfocus=date_js),
               Button("Add Task"),
               hx_post="/", target_id='todo-list', hx_swap="afterbegin")
    
    return Main(
        Div(
            H1("Tasks"),
            P("Minimalist Todo App (Postgres)"),
            cls="title-header"
        ),
        Div(
            frm,
            Ul(*map(render, todos(order_by='due_date, title')), id='todo-list'),
            cls="card"
        ),
        cls="container"
    )

@rt('/')
def post(todo: Todo):
    return render(todos.insert(todo))

@rt('/delete/{id}')
def delete(id: int):
    todos.delete(id)

@rt('/toggle/{id}')
def post(id: int):
    todo = todos[id]
    todo.done = not todo.done
    return render(todos.update(todo))

if __name__ == "__main__":
    serve()
