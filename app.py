import uvicorn
from fastapi import FastAPI, Depends
from route.auth_router import auth_router
from route.user_router import user_router
from fastapi.middleware.cors import CORSMiddleware

from controller.auth_controller import validate_token
from route.notebook_router import notebook_router
from route.message_router import message_router
from route.document_router import document_router

SECURITY_ALGORITHM = 'HS256'
SECRET_KEY = '123456'

app = FastAPI(
    title='CAIN', openapi_url='/openapi.json', docs_url='/docs',
    description='by PMC'
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(notebook_router)
app.include_router(message_router)
app.include_router(document_router)
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
