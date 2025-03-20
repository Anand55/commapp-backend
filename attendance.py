from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Attendance, Student, User
from auth import get_current_user
from pydantic import BaseModel
from datetime import date

router = APIRouter()

# Dependency to get DB Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Pydantic Model for Attendance Data
class AttendanceCreate(BaseModel):
    student_id: int
    date: date
    status: str  # "present" or "absent"

# ✅ Mark Student Attendance (Only for Teachers/Admins)
@router.post("/attendance/")
def mark_attendance(attendance: AttendanceCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only teachers and admins can mark attendance")

    student = db.query(Student).filter(Student.id == attendance.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    new_attendance = Attendance(**attendance.dict())
    db.add(new_attendance)
    db.commit()
    db.refresh(new_attendance)

    return {"message": "Attendance marked successfully"}

# ✅ Get Student Attendance (Only for Teachers/Admins)
@router.get("/attendance/")
def get_attendance(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only teachers and admins can view attendance")

    return db.query(Attendance).all()
