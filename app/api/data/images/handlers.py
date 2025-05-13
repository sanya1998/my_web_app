import shutil

from app.common.constants.info_types import InfoTypes
from app.common.constants.paths import PATTERN_INFO_TYPE
from app.common.dependencies.auth.moderator import ModeratorUserDep
from app.common.helpers.api_version import VersionedAPIRouter
from app.common.tasks.img import process_pic, process_pic_background_task
from fastapi import BackgroundTasks, UploadFile

router = VersionedAPIRouter(prefix="/images", tags=["Images"])


@router.post(PATTERN_INFO_TYPE)
async def add_image_for_moderator(
    info_type: InfoTypes, name: str, file: UploadFile, background_tasks: BackgroundTasks, moderator: ModeratorUserDep
):
    # TODO: use info_type
    im_path = f"static/images/{name}.webp"
    with open(im_path, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)

    # Задачу в celery (плюсы: можно получить результат, можно повторить задачу)
    process_pic.delay(im_path)  # Отправка задачи в очередь celery

    # Задачу во встроенный бэкграунд (плюсы: можно дебажить, можно асинхронные функции выполнять)
    background_tasks.add_task(process_pic_background_task, im_path)

    # Вернуть ответ (id), статус 201, или 202, или 204
