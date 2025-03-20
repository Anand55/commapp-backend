from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Assessment, Student, User
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

# ✅ Pydantic Model for Assessment Data
class AssessmentCreate(BaseModel):
    student_id: int
    subject: str
    score: int
    exam_date: date

# ✅ Create Assessment (Only for Teachers/Admins)
@router.post("/assessments/")
def create_assessment(assessment: AssessmentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only teachers and admins can add assessments")

    student = db.query(Student).filter(Student.id == assessment.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    new_assessment = Assessment(**assessment.dict())
    db.add(new_assessment)
    db.commit()
    db.refresh(new_assessment)

    return {"message": "Assessment added successfully", "assessment_id": new_assessment.id}

# ✅ Get All Assessments (Only for Teachers/Admins)
@router.get("/assessments/")
def get_assessments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only teachers and admins can view assessments")

    return db.query(Assessment).all()

# ✅ Update Assessment Score (Only for Teachers/Admins)
@router.put("/assessments/{assessment_id}")
def update_assessment(assessment_id: int, new_score: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    assessment.score = new_score
    db.commit()

    return {"message": "Assessment updated successfully"}

# ✅ Delete an Assessment (Only for Admins)
@router.delete("/assessments/{assessment_id}")
def delete_assessment(assessment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can delete assessments")

    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    db.delete(assessment)
    db.commit()

    return {"message": "Assessment deleted successfully"}
