from pathlib import Path

from app.resources.celery import celery
from PIL import Image


# For celery
@celery.task
def process_pic(path: str):
    im_path = Path(path)
    im = Image.open(im_path)

    width_big, height_big = 1920, 1080
    im_resized_big = im.resize((width_big, height_big))
    im_resized_big.save(f"static/images/{width_big}_{height_big}/{im_path.name}")


# For fastapi background task
def process_pic_background_task(path: str):
    im_path = Path(path)
    im = Image.open(im_path)

    width_small, height_small = 100, 100
    im_resized_small = im.resize((width_small, height_small))
    im_resized_small.save(f"static/images/{width_small}_{height_small}/{im_path.name}")
