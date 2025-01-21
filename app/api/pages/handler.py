from app.api.data.hotels import get_hotels
from app.common.helpers.api_version import VersionedAPIRouter
from fastapi import Depends, Request
from fastapi.templating import Jinja2Templates

router = VersionedAPIRouter(prefix="/pages", tags=["Fronted"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/hotels")
async def get_hotels_page(
    request: Request,
    hotels=Depends(get_hotels),
):  # todo: -> templates.TemplateResponse
    return templates.TemplateResponse(
        name="hotels.html",
        context={"request": request, "hotels": hotels},
    )
