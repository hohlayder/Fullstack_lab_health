from typing import TypeVar
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.base import Base

Entity = TypeVar("Entity", bound=Base)


def get_or_404(session: Session, model: type[Entity], entity_id: UUID, label: str) -> Entity:
    entity = session.get(model, entity_id)
    if entity is None:
        raise HTTPException(404, f"{label} не найден(а)")
    return entity


def save(session: Session, entity: Entity) -> Entity:
    session.add(entity)
    session.commit()
    session.refresh(entity)
    return entity


def delete(session: Session, entity: Base) -> None:
    session.delete(entity)
    session.commit()
