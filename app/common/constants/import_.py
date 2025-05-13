from app.common.schemas.base import BaseSchema


class ImportResult(BaseSchema):
    success: bool


IMPORT_RESULT = ImportResult(success=True)
