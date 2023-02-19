import mimetypes
from glob import glob
from pathlib import Path
from ludo.assets.services import AssetService
from starlite import (
    Body,
    Controller,
    File,
    Response,
    NotFoundException,
    Provide,
    RequestEncodingType,
    get,
    post,
    put,
    delete,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import AssetRecord, AssetUploadData


class AssetController(Controller):
    path = "/api/assets"
    dependencies = {"service": Provide(AssetService)}

    @get("/{path:path}")
    async def get_asset_by_path(
        self, path: Path, session: AsyncSession, versions_back: int = 0
    ) -> File:
        parts = path.parts[1:]
        parent_id = None
        asset_record: AssetRecord = None

        for part in parts:
            asset_record = await session.scalar(
                select(AssetRecord)
                .where(AssetRecord.parent_id == parent_id)
                .where(AssetRecord.name == path.stem)
                .where(AssetRecord.extension == path.suffix)
            )

            if asset_record is None:
                raise NotFoundException()

            parent_id = asset_record.parent_id

        filename = f"{asset_record.name}{asset_record.extension}"

        asset_prefix = Path.cwd() / "assets"  # TODO: Make this robust.
        asset_prefix = asset_prefix / asset_record.id

        possible_files = [
            Path(fname) for fname in glob(f"{asset_prefix}/*{asset_record.extension}")
        ]
        possible_files.sort(key=lambda path: path.stat().st_mtime)

        if versions_back < len(possible_files):
            path = possible_files[versions_back]
        else:
            path = possible_files[0]

        return File(
            filename=filename,
            path=path,
            media_type=mimetypes.guess_extension(asset_record.extension),
        )

    @post("/upload")
    async def create_asset(
        self,
        service: AssetService,
        data: AssetUploadData = Body(media_type=RequestEncodingType.MULTI_PART),
    ) -> AssetRecord:
        return service.create_asset(data)

    @get("/view/{id:int}")
    async def get(self, id: int, session: AsyncSession) -> File:
        record = await session.get(AssetRecord, id)
        if record is None:
            raise NotFoundException()
        filename = record.name + record.extension
        path = Path("assets") / str(id) / filename
        return File(
            filename=filename,
            path=path,
            media_type=mimetypes.guess_extension(record.extension),
            content_disposition_type="inline"
        )
