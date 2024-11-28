from fastapi import APIRouter, Depends, Form
from fastapi.responses import JSONResponse
from controller.auth_controller import validate_token
from controller.app_controller import controller
from schema.request.request_schema import MessageRequest

message_router = APIRouter(tags=["Message"], prefix="/message")

@message_router.get("/{notebook_id}")
async def get_messages():
    return "Hello World"

@message_router.delete("/{notebook_id}/all_messages")
async def delete_all_messages(notebook_id: str, user_id: str = Depends(validate_token)):
    pass
    # notebook_controller = controller.notebook_controller
    # await notebook_controller.delete_all_messages_by_notebook_id(notebook_id, user_id)
    # return JSONResponse(content={'message': f'All messages in notebook {notebook_id} deleted successfully'}, status_code=200)