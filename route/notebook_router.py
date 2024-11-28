from typing import List
from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from controller.app_controller import controller
from controller.auth_controller import validate_token
from schema.request.request_schema import MessageRequest

notebook_router = APIRouter(tags=["Notebook"], prefix="/notebook")

@notebook_router.post("/create_notebook")
async def create_notebook(title: str, user_id: str = Depends(validate_token)):
    notebook_controller = controller.notebook_controller
    new_notebook_id = await notebook_controller.create_notebook_by_user_id(user_id, title)
    return JSONResponse(content={'message': f'Notebook {title} created successfully', 'notebook_id': new_notebook_id}, status_code=200)
    
@notebook_router.get("/{notebook_id}")
async def get_notebook(notebook_id: str, user_id: str = Depends(validate_token)):
    notebook_controller = controller.notebook_controller
    notebook = await notebook_controller.get_notebook_by_id(notebook_id, user_id)
    await notebook_controller.update_notebook_access_time(notebook_id, user_id)
    return notebook

@notebook_router.get("/{notebook_id}/name")
async def get_notebook_name(notebook_id: str, user_id: str = Depends(validate_token)):
    notebook_controller = controller.notebook_controller
    notebook = await notebook_controller.get_notebook_by_id(notebook_id, user_id)
    return notebook.title
    
@notebook_router.delete("/{notebook_id}")
async def delete_notebook(notebook_id: str, user_id: str = Depends(validate_token)):
    notebook_controller = controller.notebook_controller
    await notebook_controller.delete_notebook_by_id(notebook_id, user_id)
    return JSONResponse(content={'message': f'Notebook {notebook_id} deleted successfully'}, status_code=200)


@notebook_router.post("/upload_file")
async def upload_file(file: UploadFile, notebook_id: str):
    file_controller = controller.file_controller
    file_id = await file_controller.save_file_to_server(file, notebook_id)
    return file_id


@notebook_router.get("/{notebook_id}/all_messages")
async def get_all_messages(notebook_id: str, user_id: str = Depends(validate_token)):
    notebook_controller = controller.notebook_controller
    messages = await notebook_controller.get_all_messages(notebook_id, user_id)
    return messages

@notebook_router.get("/{notebook_id}/all_files")
async def get_all_files(notebook_id: str, user_id: str = Depends(validate_token)):
    notebook_controller = controller.notebook_controller
    files = await notebook_controller.get_all_files(notebook_id, user_id)
    return files


@notebook_router.post("/send_message")
async def send_message(request: MessageRequest,
                       user_id: str = Depends(validate_token)):
    notebook_controller = controller.notebook_controller
    answer = await notebook_controller.submit_message(request.notebook_id, user_id, request.message, request.file_id)
    return answer