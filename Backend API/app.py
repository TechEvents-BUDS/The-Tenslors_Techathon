from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from db import engine, SessionLocal, Base
import crud
from models import User
from pydantic import BaseModel
import bcrypt

# Create tables on app start
Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# User Schemas
class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class NoteCreate(BaseModel):
    title: str
    content: str


# Helper function for password hashing
def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


# API Routes
@app.post("/signup/")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    """Signup Endpoint - Hashes and stores password securely"""
    existing_user = crud.get_user_by_username(db, user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken.")

    hashed_password = get_password_hash(user.password)
    created_user = crud.create_user(db, user.username, user.email, hashed_password)
    return {"message": "User created successfully", "user_id": created_user.id}


# @app.post("/login/")
# def login(user: UserLogin, db: Session = Depends(get_db)):
#     """Login Endpoint - Verifies password hash"""
#     user_in_db = crud.get_user_by_username(db, user.username)
#     if not user_in_db or not verify_password(user.password, user_in_db.password):
#         raise HTTPException(status_code=401, detail="Invalid credentials")
#     return {"message": "Login successful", "user": user.username}

@app.post("/login/")
def login(user: UserLogin, db: Session = Depends(get_db)):
    """Login Endpoint - Verifies password hash"""
    user_in_db = crud.get_user_by_username(db, user.username)
    if not user_in_db or not verify_password(user.password, user_in_db.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful", "user": user.username}



# @app.post("/add_note/")
# def add_note(note: NoteCreate, username: str, db: Session = Depends(get_db)):
#     """Add a Note Endpoint"""
#     user = crud.get_user_by_username(db, username)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     new_note = crud.create_note(db, note.title, note.content, user.id)
#     return {"message": "Note added successfully", "note": new_note}

# app.py
@app.post("/add_note/")
def add_note(note: NoteCreate, username: str, db: Session = Depends(get_db)):
    """Add a Note Endpoint"""
    user = crud.get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    new_note = crud.create_note(db, note.title, note.content, user.id)
    return {"message": "Note added successfully", "note": new_note}
# app.py
@app.get("/notes/{username}")
def get_notes(username: str, db: Session = Depends(get_db)):
    """Get Notes Endpoint"""
    user = crud.get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    notes = crud.get_notes_by_user(db, user.id)
    return {"notes": notes}

@app.get("/users/")
def get_users(db: Session = Depends(get_db)):
    """Get all users (for testing purposes)"""
    users = crud.get_all_users(db)
    return {"users": users}


@app.delete("/delete_note/")
def delete_note(note_id: int, db: Session = Depends(get_db)):
    """Delete Note by ID"""
    success = crud.delete_note_by_id(db, note_id)
    if not success:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"message": "Note deleted successfully"}
