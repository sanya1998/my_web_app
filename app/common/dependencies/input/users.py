from typing import Annotated

from app.common.schemas.user import UserInputSchema
from fastapi import Depends

UserInputDep = Annotated[UserInputSchema, Depends(UserInputSchema)]
