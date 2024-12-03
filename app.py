import uvicorn
from fastapi import FastAPI
from route.auth_router import auth_router
from route.user_router import user_router
from fastapi.middleware.cors import CORSMiddleware

from route.notebook_router import notebook_router
from route.file_router import file_router

SECURITY_ALGORITHM = 'HS256'
SECRET_KEY = '123456'

app = FastAPI(
    title='CAIN', openapi_url='/openapi.json', docs_url='/docs',
    description='by PMC'
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*","http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(notebook_router)
app.include_router(file_router)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
