from fastapi import APIRouter,HTTPException, Depends
from sqlmodel import select
from schema.request_schema import Upload_Body_Schema, Process_File_Body,Query_Body
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from utils.auth.auth import verify_token
from dependency import Sqlite_Session, Openai_Client
from models.user_model import User_Docs
from pathlib import Path
import aiofiles
import unicodedata
import os
from ingestion.ingestion import process_file
from ingestion.retrieval import retrieve_data
from prompts.prompts import SYSTEM_PROMPT
router = APIRouter()

history = {}


@router.post('/upload')
async def upload_file(files:Upload_Body_Schema,session:Sqlite_Session,user=Depends(verify_token)):
    print(user.email)
    files_size = 0
    cur_dir = Path(__file__).parent
    upload_dir = (cur_dir / '..' / 'uploads').resolve()
    print('Upload dir',upload_dir)
    all_files = []
    for file in files:
        filename = unicodedata.normalize('NFKD', file.filename).encode('ascii', 'ignore').decode('ascii')
        all_files.append(filename)
        files_size+=file.size
        filepath = (upload_dir / filename).resolve()
        print(filename,filepath)
        async with aiofiles.open(filepath,'wb') as f:
            while content := await file.read(1024*1024):
                
                await f.write(content)
    all_final_files = []
    for file in all_files:
        uploaded_file = User_Docs(filename=file,user_id=user.id,status='unprocessed')
        session.add(uploaded_file)
        session.commit()
        session.refresh(uploaded_file)
        all_final_files.append({
            'id':uploaded_file.id,
            'filename':uploaded_file.filename,
            'status':uploaded_file.status
        })
    print('Total File Size: ',files_size)
    res = {
        'message':'file uploaded successfully',
        'files':all_final_files
    }
    return JSONResponse(content=res)

@router.get('/file/all')
def get_all_uploaded_file(session:Sqlite_Session,user=Depends(verify_token)):
    all_files = session.exec(select(User_Docs).where(User_Docs.user_id==user.id)).all()
    all_filename = []
    for file in all_files:
        all_filename.append({
            'id':file.id,'filename':file.filename,'status':file.status
        })
    
    res = {
        'files': all_filename
    }
    return JSONResponse(content=res)

@router.get('/file/process/{id}')
def process_uploaded_file(id:int,session:Sqlite_Session,user=Depends(verify_token)):
    file = session.exec(select(User_Docs).where(User_Docs.id==id)).one()
    filename = file.filename
    if file.status=='processed': 
        raise HTTPException(status_code=404, detail="Already Processed")
    process_file(filename,user.id)
    
    file.status = 'processed'
    session.add(file)
    session.commit()
    res = {
        'message':'File Processed Successfully'
    }
    return JSONResponse(content=res)

@router.post('/query')
def query_docs(body:Query_Body,session:Sqlite_Session,client:Openai_Client,user=Depends(verify_token)):
    query = body.query
    processed_docs = session.exec(select(User_Docs).where(User_Docs.user_id==user.id).where(User_Docs.status=='processed')).all()
    if len(processed_docs)==0:
        raise HTTPException(status_code=404,detail="No Processed File, Process a file to chat")
    context = retrieve_data(query,user.id)
    sys_prompt_with_ctxt = f'''
        {SYSTEM_PROMPT} \n\n
        {context} \n\n

    '''
    user_history = history.get(user.id)
    if user_history is None: 
        history[user.id] = []
    user_history = history[user.id]
    system_chat = {'role':'system','content':sys_prompt_with_ctxt}
    user_chat = {'role':'user','content':query}
    user_history.append(system_chat)
    user_history.append(user_chat)
    

    completion = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=user_history
    )

    assistant_res = completion.choices[0].message.content
    user_history.append({'role':'assistant','content':assistant_res})

    return assistant_res


