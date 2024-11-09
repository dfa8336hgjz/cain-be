from fastapi import APIRouter, Depends, HTTPException

document_router = APIRouter(tags=["Document"], prefix="/document")
