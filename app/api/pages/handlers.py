from app.api.data.hotels.handlers import get_hotels
from app.common.constants.api import HOTELS_PATH, PAGES_PATH
from app.common.helpers.api_version import VersionedAPIRouter
from fastapi import Depends, Request
from fastapi.templating import Jinja2Templates

router = VersionedAPIRouter(prefix=PAGES_PATH, tags=["Fronted"])

templates = Jinja2Templates(directory="app/templates")


@router.get(HOTELS_PATH)
async def get_hotels_page(
    request: Request,
    hotels=Depends(get_hotels),
):  # todo: -> templates.TemplateResponse
    # TODO: HTMLResponse ?
    return templates.TemplateResponse(
        name="hotels.html",
        context={"request": request, "hotels": hotels},
    )
