import asyncio
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlite import (
    Controller,
    HTTPException,
    NotFoundException,
    Partial,
    delete,
    get,
    patch,
    post,
    put,
    status_codes,
)

from ludo.auth import User

from .models import Page, PageInDTO, PageOutDTO, PageWithChildren


class PagesController(Controller):
    path = "/api/pages"

    @get("/")
    async def get_pages(
        self,
        user: User,
        session: AsyncSession,
        skip: int | None = None,
        limit: int | None = None,
    ) -> list[PageOutDTO]:
        sr = await session.scalars(
            select(Page)
            .where(Page.author_id == user.id)
            .offset(skip)
            .limit(limit)
            .order_by(Page.id)
        )
        return sr.all()

    @post("/")
    async def create_page(
        self,
        user: User,
        session: AsyncSession,
        data: PageInDTO,
        parent_id: int | None = None,
    ) -> PageOutDTO:
        user_for_session = await session.get(User, user.id)
        page = Page(**data.dict())

        if page.title is None and page.friendly_title is None:
            raise HTTPException(
                status_code=status_codes.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Must set either `title` or `friendly_title` in create request body.",
            )

        if page.title is None and page.friendly_title is not None:
            page.title = page.friendly_title.replace(" ", "-").replace(",", "").lower()
        elif page.friendly_title is None and page.title is not None:
            page.friendly_title = page.title

        if parent_id is not None:
            page.parent_id = parent_id
        user_for_session.pages.append(page)
        await session.commit()
        await session.refresh(page)
        return page

    @get("/tree")
    async def get_tree(
        self, session: AsyncSession, id: int | None = None
    ) -> list[PageWithChildren]:
        if id is None:
            stmt = select(Page).where(Page.parent_id == None)
        else:
            stmt = select(Page).where(Page.id == id)
        scalar_result = await session.scalars(stmt)
        root_pages = scalar_result.all()

        result = await asyncio.gather(
            *[page.with_descendants(session) for page in root_pages]
        )

        return result

    @put("/move/{id:int}")
    async def move_page(
        self, id: int, parent_id: int, session: AsyncSession, user: User
    ) -> PageOutDTO:
        page_to_move = await session.get(Page, id)
        parent_page = await session.get(Page, parent_id)
        if (
            page_to_move is None
            or parent_page is None
            or page_to_move.author_id != user.id
            or parent_page.author_id != user.id
        ):
            raise NotFoundException()

        if await page_to_move.is_ancestor_of(parent_page, session):
            raise HTTPException(
                status_code=status_codes.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Cannot move a page to its descandant",
            )

        page_to_move.parent_id = parent_page.id

        await session.commit()
        await session.refresh(page_to_move)

        return page_to_move

    @get("/{id:int}")
    async def get_page(self, id: int, session: AsyncSession, user: User) -> PageOutDTO:
        page = await session.get(Page, id)
        if page is None or page.author_id != user.id:
            raise NotFoundException()
        return page

    @patch("/{id:int}")
    async def update_page(
        self, id: int, data: Partial[PageInDTO], session: AsyncSession, user: User
    ) -> PageOutDTO:
        page = await session.get(Page, id)
        if page is None or page.author_id != user.id:
            raise NotFoundException()

        for attr, val in data.dict(exclude_unset=True).items():
            setattr(page, attr, val)

        await session.commit()
        await session.refresh(page)

        return page

    @delete("/{id:int}")
    async def delete_page(self, id: int, session: AsyncSession, user: User, force: bool = False) -> None:
        page = await session.get(Page, id)
        if page is None or page.author_id != user.id:
            raise NotFoundException()

        # Check for children
        children = await session.scalars(select(Page).where(Page.parent_id == id))
        if children.first() is not None and not force:
            raise HTTPException(
                status_code=status_codes.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Attempting to delete page with children"
            )

        await session.delete(page)
        await session.commit()

    @get("/by-path/{path:path}")
    async def get_page_by_path(
        self, path: Path, session: AsyncSession, user: User
    ) -> PageOutDTO:
        parent_id = None
        page = None
        for part in path.parts[1:]:
            page = await session.scalar(
                select(Page).where((Page.title == part) & (Page.parent_id == parent_id))
            )

            if page is None or page.author_id != user.id:
                raise NotFoundException()

            parent_id = page.id

        if page is None:
            raise NotFoundException()

        return page
