from pydantic import BaseModel, EmailStr
from fastapi import UploadFile,File
from typing import Annotated
Upload_Body_Schema = Annotated[list[UploadFile],File(...)]

class Sign_In_Schema(BaseModel):
    email : EmailStr
    password:str|int

class Process_File_Body(BaseModel):
    id:int
    filename:str

class Query_Body(BaseModel):
    query:str