import os
from datetime import date
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload
from .database import Base, engine, get_db
from .models import User, Project, Task, Role, TaskStatus
from .schemas import *
from .auth import hash_password, verify_password, create_token, current_user, admin_user

load_dotenv()
Base.metadata.create_all(bind=engine)
app = FastAPI(title="Team Task Manager API", version="1.0.0")
origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
).split(",")
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

def project_query(db): return db.query(Project).options(joinedload(Project.members))
def task_query(db): return db.query(Task).options(joinedload(Task.assignee), joinedload(Task.project).joinedload(Project.members))
def accessible_project(project, user): return user.role == Role.admin or any(m.id == user.id for m in project.members)
def validate_assignee(db, project, assigned_to):
    if assigned_to is None: return
    if not db.get(User, assigned_to) or not any(member.id == assigned_to for member in project.members):
        raise HTTPException(400, "Assignee must be a member of the project")

@app.get("/api/health")
def health(): return {"status": "ok"}
@app.post("/api/signup", response_model=Token, status_code=201)
def signup(data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first(): raise HTTPException(409, "Email already registered")
    # The first registered account becomes an administrator for initial setup.
    role = Role.admin if db.query(User).count() == 0 else Role.member
    user = User(name=data.name, email=data.email, password=hash_password(data.password), role=role); db.add(user); db.commit(); db.refresh(user)
    return Token(access_token=create_token(user), user=user)
@app.post("/api/login", response_model=Token)
def login(data: Login, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password): raise HTTPException(401, "Incorrect email or password")
    return Token(access_token=create_token(user), user=user)
@app.get("/api/users", response_model=list[UserOut])
def users(_: User = Depends(admin_user), db: Session = Depends(get_db)): return db.query(User).order_by(User.name).all()
@app.post("/api/users", response_model=UserOut, status_code=201)
def create_member(data: MemberCreate, _: User = Depends(admin_user), db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first(): raise HTTPException(409, "Email already registered")
    member = User(name=data.name, email=data.email, password=hash_password(data.password), role=Role.member)
    db.add(member); db.commit(); db.refresh(member)
    return member
@app.get("/api/profile", response_model=UserOut)
def profile(user: User = Depends(current_user)): return user
@app.put("/api/profile", response_model=UserOut)
def update_profile(data: UserUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if data.email and data.email != user.email and db.query(User).filter(User.email == data.email).first(): raise HTTPException(409, "Email already registered")
    if data.new_password:
        if not data.current_password or not verify_password(data.current_password, user.password): raise HTTPException(400, "Current password is incorrect")
        user.password = hash_password(data.new_password)
    if data.name: user.name = data.name
    if data.email: user.email = data.email
    db.commit(); db.refresh(user); return user
@app.get("/api/projects", response_model=list[ProjectOut])
def projects(user: User = Depends(current_user), db: Session = Depends(get_db)):
    all_projects = project_query(db).all(); return all_projects if user.role == Role.admin else [p for p in all_projects if accessible_project(p, user)]
@app.post("/api/projects", response_model=ProjectOut, status_code=201)
def create_project(data: ProjectCreate, user: User = Depends(admin_user), db: Session = Depends(get_db)):
    members = db.query(User).filter(User.id.in_(set(data.member_ids + [user.id]))).all(); p = Project(name=data.name, description=data.description, created_by=user.id, members=members); db.add(p); db.commit(); db.refresh(p); return p
@app.get("/api/projects/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    p = project_query(db).get(project_id)
    if not p or not accessible_project(p,user): raise HTTPException(404,"Project not found")
    return p
@app.put("/api/projects/{project_id}", response_model=ProjectOut)
def edit_project(project_id:int, data:ProjectUpdate, _:User=Depends(admin_user), db:Session=Depends(get_db)):
    p=project_query(db).get(project_id)
    if not p: raise HTTPException(404,"Project not found")
    p.name,p.description=data.name,data.description; p.members=db.query(User).filter(User.id.in_(set(data.member_ids+[p.created_by]))).all(); db.commit(); db.refresh(p); return p
@app.delete("/api/projects/{project_id}", status_code=204)
def delete_project(project_id:int, _:User=Depends(admin_user), db:Session=Depends(get_db)):
    p=db.get(Project,project_id)
    if not p: raise HTTPException(404,"Project not found")
    db.delete(p); db.commit()
@app.get("/api/tasks", response_model=list[TaskOut])
def tasks(status_filter:TaskStatus|None=None, priority:str|None=None, search:str|None=None, user:User=Depends(current_user), db:Session=Depends(get_db)):
    items=task_query(db).all(); items=[t for t in items if user.role==Role.admin or t.assigned_to==user.id or accessible_project(t.project,user)]
    if status_filter: items=[t for t in items if t.status==status_filter]
    if priority: items=[t for t in items if t.priority.value==priority]
    if search: items=[t for t in items if search.lower() in t.title.lower()]
    return sorted(items,key=lambda t:t.due_date or date.max)
@app.post("/api/tasks", response_model=TaskOut, status_code=201)
def create_task(data:TaskCreate, _:User=Depends(admin_user), db:Session=Depends(get_db)):
    project=project_query(db).get(data.project_id)
    if not project: raise HTTPException(404,"Project not found")
    validate_assignee(db, project, data.assigned_to)
    t=Task(**data.model_dump()); db.add(t); db.commit(); return task_query(db).get(t.id)
@app.put("/api/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id:int,data:TaskUpdate,user:User=Depends(current_user),db:Session=Depends(get_db)):
    t=db.get(Task,task_id)
    if not t: raise HTTPException(404,"Task not found")
    if user.role!=Role.admin and t.assigned_to!=user.id: raise HTTPException(403,"You can only update assigned tasks")
    values=data.model_dump(exclude_unset=True)
    if user.role!=Role.admin: values={k:v for k,v in values.items() if k=="status"}
    if user.role==Role.admin and ("project_id" in values or "assigned_to" in values):
        project=project_query(db).get(values.get("project_id", t.project_id))
        if not project: raise HTTPException(404,"Project not found")
        validate_assignee(db, project, values.get("assigned_to", t.assigned_to))
    for k,v in values.items(): setattr(t,k,v)
    db.commit(); return task_query(db).get(task_id)
@app.delete("/api/tasks/{task_id}",status_code=204)
def delete_task(task_id:int,_:User=Depends(admin_user),db:Session=Depends(get_db)):
    t=db.get(Task,task_id)
    if not t: raise HTTPException(404,"Task not found")
    db.delete(t); db.commit()
@app.get("/api/dashboard")
def dashboard(user:User=Depends(current_user),db:Session=Depends(get_db)):
    tasks=task_query(db).all(); tasks=[t for t in tasks if user.role==Role.admin or t.assigned_to==user.id or accessible_project(t.project,user)]
    projects=project_query(db).all(); projects=[p for p in projects if accessible_project(p,user)]
    overdue=[t for t in tasks if t.due_date and t.due_date<date.today() and t.status!=TaskStatus.completed]
    return {"total_projects":len(projects),"total_tasks":len(tasks),"completed":sum(t.status==TaskStatus.completed for t in tasks),"todo":sum(t.status==TaskStatus.todo for t in tasks),"in_progress":sum(t.status==TaskStatus.in_progress for t in tasks),"overdue":len(overdue),"upcoming":sorted([t for t in tasks if t.due_date and t.status!=TaskStatus.completed],key=lambda t:t.due_date)[:5],"recent":sorted(tasks,key=lambda t:t.created_at,reverse=True)[:6]}
