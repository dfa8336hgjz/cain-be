from fastapi import APIRouter, Depends, HTTPException

file_router = APIRouter(tags=["File"], prefix="/file")
