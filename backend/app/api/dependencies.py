from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_session

SessionDep = Annotated[Session, Depends(get_session)]


def pagination(offset: int = Query(default=0, ge=0), limit: int = Query(default=100, ge=1, le=200)):
    return offset, limit


Pagination = Annotated[tuple[int, int], Depends(pagination)]
