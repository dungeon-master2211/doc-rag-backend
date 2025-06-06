from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from router.file_upload import router as File_Upload_Router
from router.user_router import router as User_Router
from contextlib import asynccontextmanager
from sqlmodel import create_engine, SQLModel
from models import user_model
from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
@asynccontextmanager
async def lifespan(app:FastAPI):
    db_engine = create_engine("sqlite:///doc.db")
    client = OpenAI(api_key=OPENAI_API_KEY)
    SQLModel.metadata.create_all(db_engine)
    app.state.sqlite_engine = db_engine
    app.state.openai_client = client
    yield
    

app = FastAPI(lifespan=lifespan)

origins = [
    "https://doc-rag-frontend.vercel.app",
    "http://localhost",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(File_Upload_Router)
app.include_router(User_Router)
@app.get('/')
def health_check():
    return {'message':'Voila!'}




