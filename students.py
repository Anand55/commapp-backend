from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Student, User
from auth import get_current_user
from pydantic import BaseModel

router = APIRouter()

# Dependency to get DB Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Pydantic Model for Student Data
class StudentCreate(BaseModel):
    name: str
    class_name: str

# ✅ Create a New Student (Only for Teachers/Admins)
@router.post("/students/")
def create_student(student: StudentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only teachers and admins can add students")
    
    new_student = Student(name=student.name, class_name=student.class_name, teacher_id=current_user.id)
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    
    return {"message": "Student created successfully", "student_id": new_student.id}

# ✅ Get All Students (Only for Teachers/Admins)
@router.get("/students/")
def get_students(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only teachers and admins can view students")
    
    students = db.query(Student).filter(Student.teacher_id == current_user.id).all()
    return students

# ✅ Update Student Information (Only for Teachers/Admins)
@router.put("/students/{student_id}")
def update_student(student_id: int, student_data: StudentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    student = db.query(Student).filter(Student.id == student_id, Student.teacher_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    student.name = student_data.name
    student.class_name = student_data.class_name
    db.commit()
    
    return {"message": "Student updated successfully"}

# ✅ Delete a Student (Only for Teachers/Admins)
@router.delete("/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    student = db.query(Student).filter(Student.id == student_id, Student.teacher_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    db.delete(student)
    db.commit()
    
    return {"message": "Student deleted successfully"}
