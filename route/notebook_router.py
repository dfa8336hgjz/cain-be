from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from controller.app_controller import AppController, get_app_controller
from controller.auth_controller import validate_token

notebook_router = APIRouter(tags=["Notebook"], prefix="/notebook")

@notebook_router.post("/create_notebook")
async def create_notebook(title: str, user_id: str = Depends(validate_token), controller: AppController = Depends(get_app_controller)):
    notebook_controller = controller.notebook_controller
    new_notebook_id = await notebook_controller.create_notebook_by_user_id(user_id, title)
    return JSONResponse(content={'message': f'Notebook {title} created successfully', 'notebook_id': new_notebook_id}, status_code=200)
    
@notebook_router.get("/{notebook_id}")
async def get_notebook(notebook_id: str, user_id: str = Depends(validate_token), controller: AppController = Depends(get_app_controller)):
    notebook_controller = controller.notebook_controller
    notebook = await notebook_controller.get_notebook_by_id(notebook_id, user_id)
    return notebook
    
@notebook_router.delete("/{notebook_id}")
async def delete_notebook(notebook_id: str, user_id: str = Depends(validate_token), controller: AppController = Depends(get_app_controller)):
    notebook_controller = controller.notebook_controller
    await notebook_controller.delete_notebook_by_id(notebook_id, user_id)
    return JSONResponse(content={'message': f'Notebook {notebook_id} deleted successfully'}, status_code=200)
