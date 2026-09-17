from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

PositiveUserId = Annotated[int, Field(strict=True, gt=0)]


class User(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: PositiveUserId
    name: str


class UserFetchRequest(BaseModel):
    user_ids: list[PositiveUserId] = Field(min_length=1)


class UserFetchResponse(BaseModel):
    users: list[User]
    failed: list[int]
