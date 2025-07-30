from pydantic import BaseModel


class ImportResult(BaseModel):
    success: bool


IMPORT_RESULT = ImportResult(success=True)
