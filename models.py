from sqlalchemy import Column, Integer, String, ForeignKey, Date  # ✅ Add Date import
from sqlalchemy.orm import relationship
from database import Base
from passlib.context import CryptContext  # ✅ Ensure passlib is imported properly

# ✅ Password Hashing Context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # teacher, field_worker, admin

    students = relationship("Student", back_populates="teacher")

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.hashed_password)

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    class_name = Column(String, nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"))

    teacher = relationship("User", back_populates="students")
    assessments = relationship("Assessment", back_populates="student", cascade="all, delete-orphan")
    attendance = relationship("Attendance", back_populates="student", cascade="all, delete-orphan")


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"))
    subject = Column(String, nullable=False)
    score = Column(Integer, nullable=False)
    exam_date = Column(Date, nullable=False)

    student = relationship("Student", back_populates="assessments")


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"))
    date = Column(Date, nullable=False)
    status = Column(String, nullable=False)  # "present" or "absent"

    student = relationship("Student", back_populates="attendance")
