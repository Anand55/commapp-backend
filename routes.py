from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models import User
from auth import get_password_hash, verify_password, create_access_token, get_current_user, oauth2_scheme, decode_access_token
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr

router = APIRouter()

# Function to check role-based access
def require_role(allowed_roles: list):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        return current_user
    return role_checker

# ✅ Define a Pydantic Model for Signup
class SignupRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str

# ✅ Signup Route
class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str

# ✅ Signup Route
@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(user: SignupRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = User(name=user.name, email=user.email, hashed_password=hashed_password, role=user.role)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "User created successfully! Please log in.", "user_id": new_user.id}
# ✅ Login Route: Generates JWT Token
@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}

# ✅ Protected Route Example (Only accessible with JWT)
@router.get("/protected")
def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Welcome {current_user.name}, you are authorized!"}

# ✅ Teacher Dashboard (For Teachers & Admins)
@router.get("/teacher/dashboard")
def teacher_dashboard(current_user: User = Depends(require_role(["teacher", "admin"]))):
    return {"message": "Welcome Teacher! You can manage students."}

# ✅ Admin Dashboard (For Admins Only)
@router.get("/admin/dashboard")
def admin_dashboard(current_user: User = Depends(require_role(["admin"]))):
    return {"message": "Welcome Admin! You have full access."}
