from fastapi import Header, HTTPException, status
from pydantic import BaseModel


class CurrentUser(BaseModel):
    user_id: int
    role: str

ROLE_CREATOR = "creator"
ROLE_APPROVER = "approver"

async def get_current_user(
    x_user_id: str | None = Header(default=None, alias="X-User-Id"),
    x_role: str | None = Header(default=None, alias="X-Role"),
) -> CurrentUser:
    # basic header check, auth is very light for now
    if not x_user_id or not x_role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-User-Id or X-Role header",
        )

    try:
        user_id = int(x_user_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="X-User-Id must be an integer",
        )

    role = x_role.lower().strip()

    if role not in {ROLE_CREATOR, ROLE_APPROVER}:
        raise HTTPException(
            status_code=403,
            detail="Invalid role",
        )

    return CurrentUser(
        user_id=user_id,
        role=role,
    )
