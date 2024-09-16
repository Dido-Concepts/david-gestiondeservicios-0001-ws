from fastapi import APIRouter, Depends, HTTPException
from app.modules.user.aplication.mediator.user_mediator import UserMediator
from app.modules.user.aplication.comands.create_user.create_user_command import (
    CreateUserCommand,
)
from app.modules.user.presentation.dependencies.user_dependencies import (
    get_user_mediator,
)


user_router = APIRouter()


@user_router.post("/user")
async def create_user(
    command: CreateUserCommand, mediator: UserMediator = Depends(get_user_mediator)
) -> bool:
    try:
        result = await mediator.send(command)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
