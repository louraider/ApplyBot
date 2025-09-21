#this will responsible for fetching the info during onbording of user, like for the admin
from fastapi import APIRouter
from loguru import logger

router = APIRouter()


@router.get("/")
async def getUsers():
    logger.info("Get users endpoint called")
    return {"message": "Users endpoint - not implemented yet"}


@router.post("/")
async def createUser():
    logger.info("Create user endpoint called")
    return {"message": "Create user endpoint - not implemented yet"}


@router.get("/{user_id}")
async def getUser(user_id: str):
    logger.info(f"Get user {user_id} endpoint called")
    return {"message": f"Get user {user_id} endpoint - not implemented yet"}