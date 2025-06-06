from typing import Annotated
from fastapi import Depends,Request
from sqlmodel import Session
from openai import OpenAI
def get_session(request:Request):
    engine = request.app.state.sqlite_engine
    with Session(engine) as session:
        yield session

def get_openai_client(request:Request):
    client = request.app.state.openai_client
    return client

Sqlite_Session = Annotated[Session,Depends(get_session)]
Openai_Client = Annotated[OpenAI,Depends(get_openai_client)]