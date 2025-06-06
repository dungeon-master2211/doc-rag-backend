from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from schema.request_schema import Sign_In_Schema
from models.user_model import User
from dependency import Sqlite_Session
from sqlmodel import select
import bcrypt
from utils.auth.auth import sign_token
router = APIRouter()

@router.post('/sign-up')
def sign_up(body:Sign_In_Schema,session:Sqlite_Session):
    email = body.email
    password = str(body.password).encode()

    is_exist = session.exec(select(User).where(User.email==email)).all()
    if len(is_exist): 
        raise HTTPException(status_code=400,detail='user already exist')

    hashed_pwd = bcrypt.hashpw(password=password,salt=bcrypt.gensalt(12))

    user = User(email=email,password=hashed_pwd)
    session.add(user)
    session.commit()
    session.refresh(user)
    payload = {'email':user.email}
    token = sign_token(payload=payload)
    
    res = {
        'message':'User Signed Up'
    }
    response =  JSONResponse(content=res)
    response.set_cookie(
        key = "doc-rag",
        value = token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=60*30,
        path="/"
    )
    return response

@router.post('/sign-in')
def sign_in(body:Sign_In_Schema,session:Sqlite_Session,response:Response):
    email = body.email
    password = str(body.password).encode()
    is_exist = session.exec(select(User).where(User.email==email)).all()
    if len(is_exist)==0:
        raise HTTPException(status_code=400,detail='user does not exist')
    user = is_exist[0]
    hashed_pwd = user.password
    if not bcrypt.checkpw(password=password,hashed_password=hashed_pwd):
        raise HTTPException(status_code=400,detail='Invalid email or password')
    payload = {'email':user.email}
    token = sign_token(payload=payload)

    
    res=  {
        'message':f'Welcome {user.id}, {user.email}'
    }

    response =  JSONResponse(status_code=200,content=res)
    response.set_cookie(
        key = "doc-rag",
        value = token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=60*30,
        path="/"

    )
    return response


@router.get('/logout')
def logout():
    response = JSONResponse(content={'message':'Logged Out!'})
    response.delete_cookie('doc-rag')
    return response