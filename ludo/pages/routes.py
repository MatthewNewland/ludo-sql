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

from .models import (
    Page,
    PageInDTO,
    PageOutDTO,
    PageVersion,
    PageVersionDTO,
    PageWithChildren,
)


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

        if parent_id is not None and await session.get(Page, parent_id) is None:
            raise HTTPException(
                status_code=status_codes.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Parent ID does not exist",
            )

        if not page.title and not page.friendly_title:
            raise HTTPException(
                status_code=status_codes.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Must set either `title` or `friendly_title` in create request body.",
            )

        if not page.title and page.friendly_title:
            page.title = page.friendly_title.replace(" ", "-").replace(",", "").lower()
        elif not page.friendly_title and page.title:
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

        async with asyncio.TaskGroup() as tg:
            tasks = [
                tg.create_task(page.with_descendants(session)) for page in root_pages
            ]

        result = [task.result() for task in tasks]
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

    @put("/{id:int}")
    async def update_page(
        self,
        id: int,
        data: Partial[PageInDTO],
        session: AsyncSession,
        user: User,
        save_version: bool = False,
    ) -> PageOutDTO:
        page = await session.get(Page, id)
        if page is None or page.author_id != user.id:
            raise NotFoundException()

        if save_version:
            old_version = PageVersion.from_page(page)
            session.add(old_version)

        for attr, val in data.dict(exclude_unset=True).items():
            setattr(page, attr, val)

        await session.commit()
        await session.refresh(page)

        return page

    @get("/{id:int}/versions")
    async def get_versions(
        self, id: int, session: AsyncSession
    ) -> list[PageVersionDTO]:
        result = await session.scalars(
            select(PageVersion)
            .where(PageVersion.page_id == id)
            .order_by(PageVersion.created.desc())
        )
        return result.all()

    @delete("/{id:int}/versions/drop")
    async def drop_versions(
        self, id: int, session: AsyncSession, keep: int = 1
    ) -> None:
        result = await session.scalars(
            select(PageVersion)
            .where(PageVersion.page_id == id)
            .order_by(PageVersion.created.desc())
            .offset(keep)
        )
        for version in result.all():
            await session.delete(version)

        await session.commit()

    @delete("/{id:int}")
    async def delete_page(
        self, id: int, session: AsyncSession, user: User, force: bool = False
    ) -> None:
        page = await session.get(Page, id)
        if page is None or page.author_id != user.id:
            raise NotFoundException()

        # Check for children
        children = await session.scalars(select(Page).where(Page.parent_id == id))
        if children.first() is not None and not force:
            raise HTTPException(
                status_code=status_codes.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Attempting to delete page with children",
            )

        result = await session.scalars(
            select(PageVersion).where(PageVersion.page_id == page.id)
        )
        versions_to_delete = result.all()

        for version in versions_to_delete:
            await session.delete(version)

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

    @get("/{id:int}/path")
    async def get_page_path(self, id: int, session: AsyncSession) -> Path:
        page = await session.get(Page, id)
        if page is None:
            raise NotFoundException()
        return await page.get_path(session)


class PageVersionController(Controller):
    path = "/api/page_version"
