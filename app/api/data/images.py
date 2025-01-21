import shutil

from app.common.helpers.api_version import VersionedAPIRouter
from app.common.tasks.img import process_pic, process_pic_background_task
from fastapi import BackgroundTasks, UploadFile

router = VersionedAPIRouter(prefix="/images", tags=["Images"])


@router.post("/hotels")
async def add_hotel_image(name: str, file: UploadFile, background_tasks: BackgroundTasks):
    im_path = f"static/images/{name}.webp"
    with open(im_path, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)

    # Задачу в celery (плюсы: можно получить результат, можно повторить задачу)
    process_pic.delay(im_path)  # Отправка задачи в очередь celery

    # Задачу во встроенный бэкграунд (плюсы: можно дебажить, можно асинхронные функции выполнять)
    background_tasks.add_task(process_pic_background_task, im_path)
