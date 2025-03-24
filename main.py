from fastapi import FastAPI
from routes import router
from students import router as student_router
from assessments import router as assessment_router
from attendance import router as attendance_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your frontend URL for tighter security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(student_router)
app.include_router(assessment_router)
app.include_router(attendance_router)
