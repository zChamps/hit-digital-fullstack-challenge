from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies import get_user_fetch_service
from app.schemas.user import UserFetchRequest, UserFetchResponse
from app.services.user_fetch import UserFetchService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/fetch", response_model=UserFetchResponse)
async def fetch_users(
    request: UserFetchRequest,
    service: Annotated[UserFetchService, Depends(get_user_fetch_service)],
) -> UserFetchResponse:
    return await service.fetch_users(request.user_ids)
