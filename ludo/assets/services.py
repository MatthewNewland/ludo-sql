from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from .models import AssetRecord, AssetUploadData


class AssetService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def path_for_asset(self, record: AssetRecord) -> Path:
        path = Path("assets") / str(record.id) / (record.name + record.extension)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    async def create_asset(self, data: AssetUploadData) -> AssetRecord:
        if data.name and not data.extension:
            name = data.name
            extension = Path(data.name).suffix
        else:
            name = data.name
            extension = data.extension
        record = AssetRecord(
            name=name,
            extension=extension,
            parent_id=data.parent_id
        )
        self.session.add(record)
        await self.session.commit()

        path = await self.path_for_asset(record)

        with path.open("+w") as handle:
            handle.buffer.write(await data.file.read())

        return record

    async def delete_asset(self, record: AssetRecord) -> None:
        path = await self.path_for_asset(record)
        path.unlink(missing_ok=True)
        path.parent.unlink(missing_ok=True)
        await self.session.delete(record)
        await self.session.commit()
