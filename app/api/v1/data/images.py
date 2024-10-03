import shutil

from fastapi import APIRouter, UploadFile

router = APIRouter(prefix="/images", tags=["Images"])


@router.post("/hotels")
async def add_hotel_image(name: str, file: UploadFile):
    with open(f"static/images/{name}.webp", "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
