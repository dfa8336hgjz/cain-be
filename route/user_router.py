from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from controller.auth_controller import validate_token
from controller.app_controller import controller


user_router = APIRouter(tags=["User"], prefix="/user")

@user_router.get("/me")
async def about_me(id: str = Depends(validate_token)):
    user_controller = controller.user_controller
    info = await user_controller.get_user_info(id)
    return info
    

@user_router.get("/all_notebooks")
async def get_all_notebooks(user_id: str = Depends(validate_token)):
    notebook_controller = controller.notebook_controller
    notebooks = await notebook_controller.get_all_notebooks_by_user_id(user_id)
    return notebooks
    

@user_router.get("/recent_notebooks")
async def get_recent_notebooks(user_id: str = Depends(validate_token)):
    notebook_controller = controller.notebook_controller
    notebooks = await notebook_controller.get_top_recent_notebooks_by_user_id(user_id)
    return notebooks

@user_router.delete("/account")
async def delete_account(user_id: str = Depends(validate_token)):
    user_controller = controller.user_controller
    await user_controller.delete_user_by_id(user_id)
    return JSONResponse(content={'message': 'User deleted successfully'}, status_code=200)
