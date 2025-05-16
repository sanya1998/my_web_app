import shutil
from typing import List

from app.common.constants.info_types import InfoTypes
from app.common.constants.paths import IMAGES_PATH, PATTERN_INFO_TYPE
from app.common.helpers.api_version import VersionedAPIRouter
from app.common.tasks.img import process_pic, process_pic_background_task
from app.dependencies.auth.moderator import ModeratorUserDep
from fastapi import BackgroundTasks, UploadFile

router = VersionedAPIRouter(prefix=IMAGES_PATH)


@router.post(PATTERN_INFO_TYPE)
async def add_images_for_moderator(
    info_type: InfoTypes,
    name: str,
    files: List[UploadFile],
    background_tasks: BackgroundTasks,
    moderator: ModeratorUserDep,
):
    # TODO: use info_type
    first_file = files[0]  # TODO: all files
    media_type = "images"  # TODO: проверить, что картинка, а не другой тип файла
    im_path = f"static/{media_type}/{name}.webp"
    with open(im_path, "wb+") as file_object:
        shutil.copyfileobj(first_file.file, file_object)

    # Задачу в celery (плюсы: можно получить результат, можно повторить задачу)
    process_pic.delay(im_path)  # Отправка задачи в очередь celery

    # Задачу во встроенный бэкграунд (плюсы: можно дебажить, можно асинхронные функции выполнять)
    background_tasks.add_task(process_pic_background_task, im_path)

    # TODO: Вернуть ответ (id), статус 201, или 202, или 204
