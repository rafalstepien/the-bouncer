from fastapi import APIRouter

router = APIRouter()


@router.post("/v1/evaluate")
async def evaluate_request():
    return {"messsage": "OK"}
