from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from backend.db.database import get_db
from backend.db.models import User
from backend.services.auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth")


class AuthRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/register")
def register(body: AuthRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=400, detail="Email already registered.")
    user = User(email=body.email, hashed_password=hash_password(body.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"access_token": create_access_token({"sub": str(user.id)}), "token_type": "bearer"}


@router.post("/login")
def login(body: AuthRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    return {"access_token": create_access_token({"sub": str(user.id)}), "token_type": "bearer"}
