from __future__ import annotations
from pydantic import BaseModel
from starlite import UploadFile
from sqlalchemy.orm import Mapped, mapped_column

from ludo.db import Base


class AssetRecord(Base):
    """An `:class:AssetRecord` represents a filesystem asset, giving the CMS the information
    necessary to resolve it.
    """
    __tablename__ = "asset"
    id: Mapped[int] = mapped_column(primary_key=True)
    """The PK of the asset record."""
    name: Mapped[str]
    extension: Mapped[str]
    parent_id: Mapped[int | None] = mapped_column(default=None, nullable=True)


class AssetUploadData(BaseModel):
    name: str
    extension: str = ""
    parent_id: int | None = None
    file: UploadFile

    class Config:
        arbitrary_types_allowed = True
