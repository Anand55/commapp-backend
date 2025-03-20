from fastapi import FastAPI
from routes import router
from students import router as student_router
from assessments import router as assessment_router
from attendance import router as attendance_router

app = FastAPI()

app.include_router(router)
app.include_router(student_router)
app.include_router(assessment_router)
app.include_router(attendance_router)
