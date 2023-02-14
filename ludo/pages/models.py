from __future__ import annotations
from asyncio import TaskGroup
from datetime import datetime
from pathlib import Path
from typing import Optional
from sqlalchemy import ForeignKey, select, inspect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel, Field
from ludo.db import Base, dto_factory


class Page(Base):
    __tablename__ = "page"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    friendly_title: Mapped[str]
    content: Mapped[str]
    parent_id: Mapped[int | None]

    author_id: Mapped[int | None] = mapped_column(ForeignKey("user.id"))
    author: Mapped[User] = relationship(back_populates="pages", lazy="selectin")

    async def with_descendants(self, session: AsyncSession) -> PageWithChildren:
        pwc = PageWithChildren.from_orm(self)
        sr = await session.scalars(select(Page).where(Page.parent_id == self.id))
        children = sr.all()

        async with TaskGroup() as tg:
            tasks = [tg.create_task(child.with_descendants(session)) for child in children]

        pwc.children = [task.result() for task in tasks]
        return pwc

    async def is_ancestor_of(self, page: Page, session: AsyncSession) -> bool:
        children = (
            await session.scalars(select(Page).where(Page.parent_id == self.id))
        ).all()
        if not children:
            return False

        if any(child.id == page.id for child in children):
            return True

        for child in children:
            if await child.is_ancestor_of(page):
                return True

        return False

    async def get_path(self, session: AsyncSession) -> Path:
        page = self
        parts = []
        while True:
            parts.append(page.title)
            if page.parent_id is None:
                break
            page = await session.get(Page, page.parent_id)
        path = '/' / Path(*reversed(parts))
        return path


from ludo.auth import User


class PageVersion(Base):
    __tablename__ = "page_version"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    friendly_title: Mapped[str]
    content: Mapped[str]
    page_id: Mapped[int] = mapped_column(ForeignKey("page.id"))
    created: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    @classmethod
    def from_page(cls, page: Page) -> PageVersion:
        page_version = PageVersion(
            title=page.title,
            friendly_title=page.friendly_title,
            content=page.content,
            page_id=page.id
        )
        return page_version


PageVersionDTO = dto_factory("PageVersionDTO", PageVersion)


PageInDTO = dto_factory("PageInDTO", Page, exclude=["id", "author_id", "author"])


# Kind of a hack, but it seems to work.
class PageInDTO(PageInDTO):
    friendly_title: str | None = None
    title: str | None = None


PageOutDTO = dto_factory("PageOutDTO", Page, exclude=["author_id", "author"])


class PageWithChildren(BaseModel):
    id: int | None = None
    title: str | None = None
    content: str
    friendly_title: str | None = None
    parent_id: int | None = None
    children: list[PageWithChildren] = Field(default_factory=list)

    class Config:
        orm_mode = True
