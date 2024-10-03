from app.api.v1.data.hotels import get_hotels
from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/pages", tags=["Fronted"])

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
