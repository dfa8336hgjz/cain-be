from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from controller.auth_controller import validate_token
from schema.request.request_schema import LoginRequest, SignupRequest
from controller.app_controller import controller
from controller.auth_controller import reusable_oauth2

auth_router = APIRouter(tags=["Authentication"], prefix="/auth")

@auth_router.post("/login")
async def login(request_data: LoginRequest):
    try:
        auth = controller.auth_controller
        user = await auth.verify_password(username=request_data.username, password=request_data.password)
        if user:
            token = auth.generate_token(user.user_id)
            user.token = token
            return user
        raise HTTPException(status_code=400, detail="Invalid username or password")
    except Exception as e:
        raise e
    
@auth_router.post("/signup")
async def signup(request: SignupRequest):
    try:
        auth = controller.auth_controller
        await auth.create_user(username=request.username, password=request.password, email=request.email, fullname=request.fullname)
        print("User created successfully. Login again")
        return JSONResponse(content={'message': 'User created successfully. Login again'}, status_code=200)
    except Exception as e:
        raise e
    
@auth_router.post("/check_token")
async def check_token(user_id: str = Depends(validate_token)):
    return JSONResponse(content={'message': 'Token is valid'}, status_code=200)

@auth_router.post("/logout")
async def logout(http_authorization_credentials=Depends(reusable_oauth2)):
    try:
        auth_controller = controller.auth_controller
        await auth_controller.save_token_to_blacklist(token=http_authorization_credentials.credentials)
        return JSONResponse(content={'message': 'User logged out successfully'}, status_code=200)
    except Exception as e:
        raise e
