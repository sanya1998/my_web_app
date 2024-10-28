import shutil

from app.common.tasks.img import process_pic
from fastapi import APIRouter, UploadFile

router = APIRouter(prefix="/images", tags=["Images"])


@router.post("/hotels")
async def add_hotel_image(name: str, file: UploadFile):
    im_path = f"static/images/{name}.webp"
    with open(im_path, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
    process_pic.delay(im_path)  # Отправка задачи в очередь celery
