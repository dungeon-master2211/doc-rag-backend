from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email:str
    password:str

class User_Docs(SQLModel,table=True):
    id:int|None = Field(default=None,primary_key=True)
    filename:str
    user_id: int | None = Field(default=None, foreign_key="user.id")
    status:str