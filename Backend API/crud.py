from sqlalchemy.orm import Session
from models import User, Note

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, username: str, email: str, password: str):
    """Store the hashed password"""
    user = User(username=username, email=email, password=password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# crud.py
def create_note(db: Session, title: str, content: str, owner_id: int):
    note = Note(title=title, content=content, owner_id=owner_id)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note
# crud.py
def get_notes_by_user(db: Session, owner_id: int):
    return db.query(Note).filter(Note.owner_id == owner_id).all()

def delete_note_by_id(db: Session, note_id: int):
    note = db.query(Note).filter(Note.id == note_id).first()
    if note:
        db.delete(note)
        db.commit()
        return True
    return False

def get_all_users(db: Session):
    return db.query(User).all()
