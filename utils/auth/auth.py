import jwt
import os
from dotenv import load_dotenv
from datetime import datetime,timezone, timedelta
from fastapi import HTTPException,status, Request
from sqlmodel import select
from dependency import Sqlite_Session
from models.user_model import User
load_dotenv()

JWT_SECRET = os.environ.get('JWT_SECRET')
JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM')

def sign_token(payload):
    expiration_time = datetime.now(timezone.utc)+timedelta(30)
    data = payload.copy()
    data.update({'exp':expiration_time})
    encoded_token = jwt.encode(data, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_token

def verify_token(request:Request,session:Sqlite_Session):
    token = request.cookies.get('doc-rag')
    if token is None: raise HTTPException(status_code=401, detail = 'Login to continue')
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = jwt.decode(token,JWT_SECRET,algorithms=[JWT_ALGORITHM])
    user_email = payload.get('email')
    if user_email is None:
        raise credentials_exception
    fetch_user = session.exec(select(User).where(User.email==user_email)).all()
    if len(fetch_user)==0: 
        raise credentials_exception
    
    user = fetch_user[0]
    return user

    
